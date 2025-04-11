

import os

# Function to verify if a file exists at the given path
def file_exists(file_path, module, logger):
    """
    Verify if a file exists at the given path.

    Args:
        file_path (str): The path of the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if os.path.exists(file_path) and os.path.isfile(file_path):
        message = "The file %s exists" % file_path
        logger.info(message)
        return True
    else:
        message = "The file %s does not exist" % file_path
        logger.error(message)
        module.fail_json(msg=message)
        return False

# Function to verify if a directory exists at the given path
def directory_exists(directory_path, module, logger):
    """
    Verify if a directory exists at the given path.

    Args:
        directory_path (str): The path of the directory to check.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        message = "The directory %s exists." % directory_path
        logger.info(message)
        return True
    else:
        message = "The directory %s does not exist." % directory_path
        logger.error(message)
        module.fail_json(msg=message)
        return False
