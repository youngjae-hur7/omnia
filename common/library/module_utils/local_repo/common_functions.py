# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import yaml

def load_yaml_file(path):
    """
    Load YAML from a given file path.

    Args:
        path (str): The path to the YAML file.

    Returns:
        dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding = "utf-8") as file:
        return yaml.safe_load(file)

def get_repo_list(config_file, repo_key):
    """
    Retrieve the list of repositories from config using a given key.

    Args:
        config_file (dict): The configuration file data.
        repo_key (str): The key to retrieve the repository list.

    Returns:
        list: The list of repositories.
    """
    return config_file.get(repo_key, [])

def is_file_exists(file_path):
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(file_path)

def is_encrypted(file_path):
    """
    Check if a file encrypted at the given path.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file encrypted, False otherwise.
    """
    with open(file_path, 'r', encoding = 'utf-8') as f:
        first_line = f.readline()
    return "$ANSIBLE_VAULT" in first_line

def run_vault_command(command, file_path, vault_key):
    """
    Run ansible-vault command at the given path.

    Args:
        command (str): Command to execute
        file_path (str): The path to the file.
        vault_key (str): key string

    Returns:
        bool: True/False based on execute command.
    """
    cmd = [
        "ansible-vault",
        command,
        file_path,
        "--vault-password-file", vault_key
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check = True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()
