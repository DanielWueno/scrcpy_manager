import os

def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that the specified directory exists. If it does not exist, it will be created.
    
    :param directory: The path of the directory to ensure exists.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)