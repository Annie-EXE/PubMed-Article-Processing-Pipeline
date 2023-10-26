import spacy
import pandas as pd
from rapidfuzz.process_cpp import extract, extractOne
from rapidfuzz.distance import Levenshtein
from rapidfuzz.fuzz import partial_ratio, partial_token_ratio
from rapidfuzz import fuzz

sample_folder = 'Outputs (Sample)'
full_folder = 'Outputs (Fall)'

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

    grid_institutions_df = pd.read_csv("./GRID Data/institutes.csv")
    aliases_df = pd.read_csv("./GRID Data/aliases.csv")
    addresses_df = pd.read_csv("./GRID Data/addresses.csv")

    nlp = spacy.load("en_core_web_sm")

    data = pd.read_csv(f"./{sample_folder}/stage_1_output_flatten.csv")

    data = data[:50] 

    docs = data['affiliation'].apply(nlp)

    world_countries = get_world_countries_list("world_countries.txt")

    identified_countries_list = identify_countries(docs, world_countries)

    add_column_to_data(identified_countries_list, 'country', data, f'./{sample_folder}/stage_2_output_add_countries_institutes.csv')

    identified_institutions_list, grid_institutions_list = identify_institutions(docs, grid_institutions_df)

    add_column_to_data(identified_institutions_list, 'institutions', data, f'./{sample_folder}/stage_2_output_add_countries_institutes.csv')

    add_column_to_data(grid_institutions_list, 'grid_institutions', data, f'./{sample_folder}/stage_2_output_add_countries_institutes.csv')