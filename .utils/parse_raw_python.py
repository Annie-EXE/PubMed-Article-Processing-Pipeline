import json
import re
import os
import sys
from typing import Tuple


def check_empty_report(report_path: str):
    """Checks if the opened report is empty, and exits with system code 0 if so
    The github workflow will continue if it receives an exit code 0

    Parameters
    ----------
    report_path : str
        Full path to report
    """

    empty_file = os.stat(report_path).st_size == 0
    if empty_file:
        sys.exit(0)


def read_file(report_path: str) -> str:
    """Reads the contents of the report and will return it for processing
    Contains error handling in case the report file does not exist

    Parameters
    ----------
    report_path : str
        Full path to report

    Returns
    -------
    content : str
        Contents of file in string format
    """
    
    try:
        with open(report_path,encoding='utf-8') as file:
            content = file.read()
            check_empty_report(report_path)

    except FileNotFoundError:
        print("File not found")
        sys.exit(0)

    return content


def obtain_files(content: str) -> list:
    """Separates the report into files using a regular expression to identify the end of the report for a specific file

    Parameters
    ----------
    content : str
        Full string content of report

    Returns
    -------
    list_files: list
        Report separated into a list based on each file
    """
    score_regex = r"(Your code has been rated at \d*\d.\d\d.\d\d)"
    list_files = re.split(score_regex, content)

    return list_files


def obtain_file_name(file_info: str) -> Tuple[list, str]:
    """Obtain the name of the file using a regular expression applied to the full file info

    Parameters
    ----------
    file_info : str
        Linter report for specific file

    Returns
    -------
    file_name: str
        Filename extracted from file info
    """
    file_name_regex = r"(.*py)\n"
    file_name = re.findall(file_name_regex, file_info)[0]
    return file_name


def obtain_scores(score_info: list) -> float:
    """Obtain the scores given by pylint for each file and convert to percentage

    Parameters
    ----------
    score_info: str
        Linter score for specific file

    Returns
    -------
    score: float
        Score of linter for specific file

    """
    try:
        score_line = re.findall(r"\d*\d.\d\d.\d\d", score_info)[0]
        score = round(float(score_line[0:4]) * 10, 1)

    except IndexError:
        score = 100

    return score


def obtain_errors(file_info: str) -> list:
    """Obtains a list of errors from the report of a specific file

    Parameters
    ----------
    file_info: str
        Linter report for specific file

    Returns
    -------
    error_list: list
        List of errors obtained from the report of the file

    """
    file_info = file_info.split("\n")
    discounted_strings = ("-", "Your code", ".", "*") #Exclude strings that are not error related
    error_list = []

    error_list = [error for error in file_info if not error.startswith(discounted_strings) and error != ""]

    return error_list


def prepare_dict(list_files: list) -> Tuple[dict, list]:
    """Prepare the dictionary with error and score data for each file
    
    Parameters
    ----------
    list_files: list
        List of reports for each file

    Returns
    -------
    files_dict, scores_list : Tuple[dict,list]
        Files dictionary containing file information, and scores_list to calculate average score
    
    """
    scores_list = []
    files_dict: dict = {"files": []}
    list_files = list_files[:-1]  # remove unwanted element

    for i in range(0, len(list_files), 2):
        file_info = list_files[i]
        score_info = list_files[i + 1]

        file_name = obtain_file_name(file_info)

        score = obtain_scores(score_info)
        scores_list.append(score)

        errors = obtain_errors(file_info)

        files_dict["files"].append({"file_name": file_name, "errors": errors, "score": round(score, 1)})

    return files_dict, scores_list


def add_avg_score(files_dict: dict, scores_list: list) -> dict:
    """Calculate and add the average score of files to the dictionary
    
    Parameters
    ----------
    files_dict: dict
        dictionary containing all file information
    scores_list: list
        List containing all file scores

    Returns
    -------
    files_dict
        Files dictionary ready for JSONification

    """

    avg_score = sum(scores_list) / len(scores_list)
    files_dict["average_score"] = round(avg_score, 1)
    return files_dict


def create_json(files_dict: dict, output_path: str):
    """Create a json from the dictionary
    
    Parameters
    ----------
    files_dict: dict
        Files dictionary ready for JSONification
    output_path: str
        Output path of final JSON file
    
    """
    with open(output_path, "w",encoding='utf-8') as write_file:
        json.dump(files_dict, write_file, indent=1)


if __name__ == "__main__":
    """Takes a raw text output of pylint and converts to json format with a separate entry for each file"""
    content = read_file("code_review/report.txt")
    list_files = obtain_files(content)
    files_dict, scores_list = prepare_dict(list_files)
    files_dict= add_avg_score(files_dict, scores_list)
    create_json(files_dict, "code_review/report.json")
