import os
from os import environ
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from dotenv import dotenv_values, load_dotenv
from boto3 import client
import pandas as pd
import spacy
from spacy.lang.en import English
from rapidfuzz import fuzz
from rapidfuzz.process_cpp import extract, extractOne
from rapidfuzz.distance import Levenshtein
from rapidfuzz.fuzz import partial_ratio, partial_token_ratio


def download_pubmed_xml_file(s3, input_bucket_name: str, folder_prefix: str, local_file_path: str):

    objects = s3.list_objects_v2(Bucket=input_bucket_name, Prefix=folder_prefix)
    
    most_recent_file = None
    most_recent_date = None
    for obj in objects.get('Contents', []):
        if obj['Key'].endswith('.xml'):
            if most_recent_date is None or obj['LastModified'] > most_recent_date:
                most_recent_file = obj['Key']
                most_recent_date = obj['LastModified']
    
    if most_recent_file:
        s3.download_file(input_bucket_name, most_recent_file, local_file_path)


def get_author_info_from_article_num(root: Element, article_num: int):

    article = root.findall(".//PubmedArticle")[article_num]

    authors = article.findall(".//AuthorList/Author")

    title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle").text is not None else None
    pmid = article.find(".//PMID").text if article.find(".//PMID").text is not None else None
    year = article.find(".//DateRevised/Year").text if article.find(".//DateRevised/Year").text is not None else None

    keyword_list = [keyword.text for keyword in article.findall(".//KeywordList/Keyword")]

    mesh_list = [mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName[@UI]")]
    
    authors_info = []
    
    for author in authors:

        forename = author.find(".//ForeName").text if author.find(".//ForeName") is not None else None
        lastname = author.find(".//LastName").text if author.find(".//LastName") is not None else None
        initials = author.find(".//Initials").text if author.find(".//Initials") is not None else None
        affiliation_name_pubmed = author.find(".//AffiliationInfo/Affiliation").text if author.find(".//AffiliationInfo/Affiliation") is not None else None
        identity = author.find(".//AffiliationInfo/Identifier[@Source='GRID']").text if author.find(".//AffiliationInfo/Identifier[@Source='GRID']") is not None else None

        affiliation_list = [aff.text for aff in author.findall(".//Affiliation")]

        author_info = {
            "forename": forename,
            "lastname": lastname,
            "initials": initials,
            "identity": identity,
            "affiliation_name": affiliation_name_pubmed,
            "affiliation": affiliation_list
        }
        authors_info.append(author_info)
    
    output = {
        "title": title,
        "pmid": pmid,
        "year": year,
        "keyword_list": keyword_list,
        "mesh_list": mesh_list,
        "authors_info": authors_info
    }
    
    return output


def get_all_data_for_each_article(root, article_cap):

    data = []

    for i in range(article_cap):

        data.append(get_author_info_from_article_num(root, i))

    return data


def flatten_article_data(article_data):

    flattened_data = []

    for article in article_data:
        for author in article['authors_info']:
            for affiliation in author['affiliation']:
                flattened_dict = {
                    "title": article['title'],
                    "pmid": article['pmid'],
                    "year": article['year'],
                    "keyword_list": article['keyword_list'],
                    "mesh_list": article['mesh_list'],
                    "forename": author['forename'],
                    "lastname": author['lastname'],
                    "full_name": author['forename'] + " " + author['lastname'],
                    "initials": author['initials'],
                    "identity": author['identity'],
                    "affiliation_name": author['affiliation_name'],
                    "affiliation": affiliation
                }
                flattened_data.append(flattened_dict)

    return flattened_data


def find_email_zipcode(df):

    df['author_email'] = df['affiliation'].str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    df['zipcode'] = df['affiliation'].str.extract(r'(\b\d{5}(?:-\d{4})?\b|\b[A-Z]\d[A-Z] \d[A-Z]\b|\b[A-Z]\d[A-Z]\d[A-Z]\b)', flags=re.IGNORECASE)

    return df


def identify_countries(docs, world_countries):

    world_countries = set(world_countries)

    countries_list = []

    for doc in docs:
        countries_found = [ent.text for ent in doc.ents if ent.label_ == "GPE" and ent.text.title() in world_countries]
        if countries_found:
            countries_list.append(countries_found[-1])
        else:
            countries_list.append(None)
    
    return countries_list


def identify_institutions(docs, grid_institutions_df):

    institutions_list = []
    grid_institutions_list = []

    target_keywords = {"university", "center", "centre", "laboratory", "hospital"}

    for doc in docs:
        institutions_found = [ent.text for ent in doc.ents if ent.label_ == "ORG" and any(keyword in ent.text.lower() for keyword in target_keywords)]
        if institutions_found:
            institutions_list.append(institutions_found)
            grid_institutions_found = []
            for institution in institutions_found:
                grid_institution_found = fuzzy_match(grid_institutions_df, institution, 90)
                grid_institutions_found.append(grid_institution_found)
            grid_institutions_list.append(grid_institutions_found)
        else:
            institutions_list.append(None)
            grid_institutions_list.append(None)
    
    return institutions_list, grid_institutions_list


def get_world_countries_list(file_path):

    with open(file_path) as f:

        world_countries = f.read()

        world_countries = world_countries.split("\n")

        return world_countries


def add_column_to_data(column_values_list, column_name, df, file_path):

    df[column_name] = column_values_list

    df.to_csv(file_path, index=False)


def fuzzy_match(grid_institutions_df, found_institute, threshold):

    for grid_inst in grid_institutions_df['name']:
        if fuzz.ratio(found_institute, grid_inst) >= threshold:
            return grid_inst

    return None


if __name__ == "__main__":

    load_dotenv()

    config = {}

    config["ACCESS_KEY_ID"] = environ.get("ACCESS_KEY_ID")
    config["SECRET_ACCESS_KEY"] = environ.get("SECRET_ACCESS_KEY")

    config["INPUT_BUCKET_NAME"] = environ.get("INPUT_BUCKET_NAME")
    config["OUTPUT_BUCKET_NAME"] = environ.get("OUTPUT_BUCKET_NAME")

    config["INPUT_BUCKET_PREFIX"] = environ.get("INPUT_BUCKET_PREFIX")
    config["INPUT_BUCKET_GRID_PREFIX"] = environ.get("INPUT_BUCKET_GRID_PREFIX")
    config["OUTPUT_BUCKET_PREFIX"] = environ.get("OUTPUT_BUCKET_PREFIX")

    s3 = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                aws_secret_access_key=config["SECRET_ACCESS_KEY"])
    
    grid_institutions_df = pd.read_csv("./GRID_Data/institutes.csv")
    aliases_df = pd.read_csv("./GRID_Data/aliases.csv")
    addresses_df = pd.read_csv("./GRID_Data/addresses.csv")
    
    pubmed_xml_file_path = '/Users/anniemahmood/Documents/Coursework-Data-Engineering-Week-5/Pipeline/tmp/pubmed_xml_file.xml'
    processed_csv_file_path = '/Users/anniemahmood/Documents/Coursework-Data-Engineering-Week-5/Pipeline/tmp/processed_article_data.csv'
    processed_csv_destination_key = f'{config["OUTPUT_BUCKET_PREFIX"]}processed_article_data.csv'

    download_pubmed_xml_file(s3, config["INPUT_BUCKET_NAME"], 'Annie/', pubmed_xml_file_path)

    if not os.path.exists(pubmed_xml_file_path):
        raise FileNotFoundError(f"File {pubmed_xml_file_path} not found.")

    tree = ET.parse(pubmed_xml_file_path)

    root = tree.getroot()

    # data = get_all_data_for_each_article(root, len(root.findall(".//PubmedArticle")))

    data = get_all_data_for_each_article(root, 50)

    flattened_data = flatten_article_data(data)

    df = pd.DataFrame(flattened_data)

    df = find_email_zipcode(df)

    # enrich:

    nlp = spacy.load("en_core_web_sm")

    docs = df['affiliation'].apply(nlp)

    world_countries = get_world_countries_list("./world_countries.txt")

    identified_countries_list = identify_countries(docs, world_countries)

    add_column_to_data(identified_countries_list, 'country', df, processed_csv_file_path)

    identified_institutions_list, grid_institutions_list = identify_institutions(docs, grid_institutions_df)

    add_column_to_data(identified_institutions_list, 'institutions', df, processed_csv_file_path)

    add_column_to_data(grid_institutions_list, 'grid_institutions', df, processed_csv_file_path)

    s3.upload_file(processed_csv_file_path, config["OUTPUT_BUCKET_NAME"], processed_csv_destination_key)

