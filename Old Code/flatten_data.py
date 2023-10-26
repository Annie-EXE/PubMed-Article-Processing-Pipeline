import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import pandas as pd
import re
import spacy
from spacy.lang.en import English

sample_folder = 'Outputs (Sample)'
full_folder = 'Outputs (Fall)'

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


def enrich_dataframe(df):

    df['author_email'] = df['affiliation'].str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    df['zipcode'] = df['affiliation'].str.extract(r'(\b\d{5}(?:-\d{4})?\b|\b[A-Z]\d[A-Z] \d[A-Z]\b|\b[A-Z]\d[A-Z]\d[A-Z]\b)', flags=re.IGNORECASE)

    return df


def create_dataframe(flattened_data):

    df = pd.DataFrame(flattened_data)

    return df


def export_dataframe_to_csv(df):

    df.to_csv('output.csv', index=False)


if __name__ == "__main__":

    tree = ET.parse("pubmed_result_sjogren.xml")

    root = tree.getroot()

    # data = get_all_data_for_each_article(root, len(root.findall(".//PubmedArticle")))

    data = get_all_data_for_each_article(root, 50)

    flattened_data = flatten_article_data(data)

    print(flattened_data)

    df = pd.DataFrame(flattened_data)

    df = enrich_dataframe(df)

    df.to_csv(f'./{sample_folder}/stage_1_output_flatten.csv', index=False)

    nlp = spacy.load("en_core_web_sm")

    nlp = English()

