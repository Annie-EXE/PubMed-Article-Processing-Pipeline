import os

def make_or_replace_dir(directory_path: str) -> bool:
    """Will create a directory if it does not already exist

    Parameters
    ----------
    directory_path : str
        path to directory

    Returns
    -------
    bool
        True if the directory is made, False otherwise
    """
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
        return True
    return False


def main():
    make_or_replace_dir("code_review")


if __name__ == "__main__":
    main()
