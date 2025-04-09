import os
import yaml

def load_yaml_file(path):
    """Load YAML from a given file path."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as file:
        return yaml.safe_load(file)

def get_repo_list(config_file, repo_key):
    """Retrieve the list of repositories from config using a given key."""
    return config_file.get(repo_key, [])

def is_file_exists(file_path):
    """Check if a file exists at the given path."""
    return os.path.isfile(file_path)
