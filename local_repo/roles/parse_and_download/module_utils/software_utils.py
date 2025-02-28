import os
import json
import csv
import yaml
from collections import defaultdict
import re
from jinja2 import Template

# Import default variables from config.py
from ansible.module_utils.config import (
    PACKAGE_TYPES,
    CSV_COLUMNS,
    SOFTWARE_CONFIG_SUBDIR,
    DEFAULT_STATUS_FILENAME,
    RPM_LABEL_TEMPLATE,
    OMNIA_REPO_KEY,
    SOFTWARES_KEY
)

def load_json(file_path):
    """
    Load JSON data from a file.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: Failed to parse JSON in file '{file_path}'.")

def load_yaml(file_path):
    """
    Load YAML data from a file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def get_json_file_path(software_name, cluster_os_type, cluster_os_version, user_json_path):
    """
    Generate the file path for a JSON file based on the software name, cluster OS type, 
    cluster OS version, and the user JSON file path.
    """
    base_path = os.path.dirname(os.path.abspath(user_json_path))
    json_path = os.path.join(base_path, f'{SOFTWARE_CONFIG_SUBDIR}/{cluster_os_type}/{cluster_os_version}/{software_name}.json')
    if os.path.exists(json_path):
        return json_path
    return None

def get_csv_file_path(software_name, user_csv_dir):
    """
    Generates the absolute path of the CSV file based on the software name and the user-provided CSV directory.
    """
    status_csv_file_path = os.path.join(user_csv_dir, software_name, DEFAULT_STATUS_FILENAME)
    return status_csv_file_path

def transform_package_dict(data):
    """
    Transforms a dictionary of packages into a new dictionary.
    """
    result = {}
    rpm_packages = defaultdict(list)

    for key, items in data.items():
        transformed_items = []

        for item in items:
            if item.get("type") == "rpm":
                rpm_packages[key].append(item["package"])
            else:
                transformed_items.append(item)

        if rpm_packages[key]:
            transformed_items.append({
                "package": RPM_LABEL_TEMPLATE.format(key=key),
                "rpm_list": rpm_packages[key],
                "type": "rpm"
            })

        result[key] = transformed_items

    return result

def parse_repo_urls(local_repo_config_path, version_variables):
    """
    Parses the repository URLs from the local repository configuration file.
    """
    local_yaml = load_yaml(local_repo_config_path)
    repo_entries = local_yaml.get(OMNIA_REPO_KEY, [])
    parsed_repos = []

    for repo in repo_entries:
        name = repo.get("name", "unknown")
        url = repo.get("url", "")
        gpgkey = repo.get("gpgkey")
        version = version_variables.get(f"{name}_version")
        try:
            rendered_url = Template(url).render(version_variables)
        except Exception as e:
            print(f"Warning: Error rendering URL {url} - {str(e)}")
            rendered_url = url
        parsed_repos.append({
            "package": name,
            "url": rendered_url,
            "gpgkey": gpgkey if gpgkey else "null",
            "version": version if version else "null"
        })

    return json.dumps(parsed_repos)

def set_version_variables(user_data, software_names, cluster_os_version):
    """
    Generates a dictionary of version variables from the user data.
    """
    version_variables = {}

    for software in user_data.get(SOFTWARES_KEY, []):
        name = software.get('name')
        if name in software_names and 'version' in software:
            version_variables[f"{name}_version"] = software['version']

    for key in software_names:
        for item in user_data.get(key, []):
            name = item.get('name')
            if 'version' in item:
                version_variables[f"{name}_version"] = item['version']

    version_variables["cluster_os_version"] = cluster_os_version
    return version_variables

def get_subgroup_dict(user_data):
    """
    Returns a tuple containing a dictionary mapping software names to subgroup lists,
    and a list of software names.
    """
    subgroup_dict = {}
    software_names = []

    for sw in user_data.get(SOFTWARES_KEY, []):
        software_name = sw['name']
        software_names.append(software_name)
        subgroups = [sw['name']] + [item['name'] for item in user_data.get(software_name, [])]
        subgroup_dict[software_name] = subgroups if isinstance(user_data.get(software_name), list) else [sw['name']]
    return subgroup_dict, software_names

def get_csv_software(file_name):
    """
    Retrieves a list of software names from a CSV file.
    """
    csv_software = []

    if not os.path.isfile(file_name):
        return csv_software

    with open(file_name, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_software = [row.get(CSV_COLUMNS["column1"], "").strip() for row in reader]

    return csv_software

def get_failed_software(file_name):
    """
    Retrieves a list of failed software from a CSV file.
    """
    failed_software = []

    if not os.path.isfile(file_name):
        return failed_software

    with open(file_name, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        failed_software = [row.get(CSV_COLUMNS["column1"], "").strip()
                           for row in reader
                           if row.get(CSV_COLUMNS["column2"], "").strip().lower() == "failed"]

    return failed_software

def parse_json_data(file_path, package_types, failed_list=None, subgroup_list=None):
    """
    Retrieves a filtered list of items from a JSON file.
    """
    data = load_json(file_path)
    filtered_list = []

    for key, package in data.items():
        if subgroup_list is None or key in subgroup_list:
            for value in package.values():
                filtered_list.extend([
                    item for item in value
                    if item.get("type") in package_types and (failed_list is None or item.get("package") in failed_list)
                ])

    return filtered_list

def check_csv_existence(path):
    """
    Checks if a CSV file exists at the given path.
    """
    return os.path.isfile(path)

def process_software(software, fresh_installation, json_path, csv_path, subgroup_list):
    """
    Processes the given software by parsing JSON data and returning a filtered list of items.
    """
    failed_packages = None if fresh_installation else get_failed_software(csv_path)
    rpm_package_type = ['rpm']
    rpm_tasks = []
    if failed_packages is not None and any("RPMs" in software for software in failed_packages):
        rpm_tasks = parse_json_data(json_path, rpm_package_type, None, subgroup_list)

    combined = parse_json_data(json_path, PACKAGE_TYPES, failed_packages, subgroup_list) + rpm_tasks
    return combined, failed_packages

def get_software_names(data_path):
    """
    Retrieves a list of software names from a given data file.
    """
    data = load_json(data_path)
    return [software['name'] for software in data.get(SOFTWARES_KEY, [])]

