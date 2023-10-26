import json

def read_json(json_path):
    """Read JSON file of report, with error handling if it does not exist"""
    try:
        json_file = open(json_path)
        json_dict = json.load(json_file)
        files_list = json_dict.get('files')

    except FileNotFoundError:
        files_list = {}
    
    return files_list

 
def obtain_errors(files_list):
    """Loop through the report of each file and count the total number of errors for all files"""
    total_errors = 0
    for files in files_list:
        errors = len(files.get('errors'))
        total_errors += errors

    return total_errors

if __name__ == "__main__":
    files_list = read_json('code_review/report.json')
    total_errors = obtain_errors(files_list)
    print(total_errors) #needed for saving to badge
