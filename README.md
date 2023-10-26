# 🧑‍💻 PubMed Pipeline Coursework

Coursework: an ETL pipeline deployed using AWS Lambda, which processes medical article data downloaded from S3.

## 🛠️ Getting Setup

1. Create and enter a venv

2. Run `pip install -r requirements.txt` to download the necessary modules

3. Run `python -m spacy download en_core_web_sm`

4. Create the folders `Local Pipeline/tmp` and `Local Pipeline/GRID_Data`

5. Navigate to the `Local Pipeline/tmp` folder and run the following:

- `curl -o https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/pubmed_result_sjogren.xml`

6. Navigate to the `Local Pipeline/GRID_Data` folder and run the following:

- `curl -o https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/aliases.csv`
- `curl -o https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/institutes.csv`
- `curl -o https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/addresses.csv`

7. Navigate back to the `Local Pipeline` folder and create a .env file with the following variables:

- ACCESS_KEY_ID=XXXX
- SECRET_ACCESS_KEY=XXXX
- INPUT_BUCKET_NAME=XXXX
- OUTPUT_BUCKET_NAME=XXXX
- INPUT_BUCKET_PREFIX=XXXX
- INPUT_BUCKET_GRID_PREFIX=XXXX
- OUTPUT_BUCKET_PREFIX=XXXX

8. Run:

- `python processing_pipeline.py`

## 🗂️ Files Explained

- `README.md`

  - This is the file you are currently reading

- `.gitignore`

  - This file is used to tell Git what files to ignore for any changes. This can be safely ignored.

- `Lambda Pipeline/`

  - This folder contains everything needed to build a Docker image, suitable for execution by AWS Lambda

- `Local Pipeline/`

  - This folder contains everything needed to run the pipeline locally

- `processing_pipeline.py`

  - When run, this file extracts and processes PubMed `.xml` data

  - It flattens the data so that each author and each author affiliation have a separate row. Useful data points (including country, zipcode, email address, and institution) are extracted and given appropriate columns to reside in

  - Fuzzy matching is used to match the extracted institution names to the institution names (and corresponding GRID IDs) in the `institutes.csv` file

  - The processed data is saved as a `.csv` file before being uploaded to an s3 output bucket
