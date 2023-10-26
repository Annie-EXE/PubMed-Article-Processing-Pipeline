import pandas as pd
import ast
import rapidfuzz
from rapidfuzz import fuzz
from rapidfuzz.process_cpp import extract, extractOne
from rapidfuzz.distance import Levenshtein
from rapidfuzz.fuzz import partial_ratio, partial_token_ratio

sample_folder = 'Outputs (Sample)'
full_folder = 'Outputs (Fall)'

# def select_org(orgs, institutes):
#     for org in orgs[::-1]:
#         inst = extractOne(org, institutes,
#                           scorer=partial_ratio, score_cutoff=90)
#         if inst:
#             return inst[0]
#     return None

def select_grid_inst(inst_names, grid_inst_names):
    for inst_name in inst_names[::-1]:
        grid_inst = extractOne(inst_name, grid_inst_names,
                          scorer=partial_ratio, score_cutoff=90)
        if grid_inst:
            return grid_inst[0]
    return None


# if __name__ == "__main__":
#     articles_df = pd.read_csv(
#         "../articles_post_extraction.csv", converters={'institutes': pd.eval})
#     institutions_df = pd.read_csv("../institutes.csv")
#     inst_names = institutions_df["name"].values

#     articles_df = articles_df[:200]

#     articles_df["institutes"] = [select_org(orgs, inst_names)
#                                  for orgs in articles_df["institutes"].values]

if __name__ == "__main__":  

    institutes_df = pd.read_csv("./GRID Data/institutes.csv")
    aliases_df = pd.read_csv("./GRID Data/aliases.csv")
    addresses_df = pd.read_csv("./GRID Data/addresses.csv")

    grid_inst_names = institutes_df["name"].values

    # main_df = pd.read_csv(f'./{sample_folder}/stage_2_output_add_countries_institutes.csv', converters={'affiliation_name': ast.literal_eval})

    main_df = pd.read_csv(f'./{sample_folder}/stage_2_output_add_countries_institutes.csv')

    main_df["grid_institution_names"] = [select_grid_inst(inst_names, grid_inst_names)
                                 for inst_names in main_df["institutions"].values]
    
    main_df.to_csv(f'./{sample_folder}/stage_3_output_with_closest_matches.csv')
