import os
import yaml
from ansible.module_utils.common_functions import (
    load_yaml_file,
    get_repo_list,
    is_file_exists
)

def check_cert_files_exist(repo_name, cert_fields):
    """Check if all given cert files exist in the expected path."""
    missing_files = []
    for cert in cert_fields:
        if not is_file_exists(cert):
            missing_files.append(os.path.basename(cert))
    return missing_files

def validate_repo_certificates(repo_list, certs_path):
    """Validate certificates for repositories where certs are defined."""
    missing_certs = []

    for repo in repo_list:
        repo_name = repo.get("name", "unnamed_repo")
        repo_cert_path = os.path.join(certs_path, repo_name)

        cert_keys = ["sslcacert", "sslclientkey", "sslclientcert"]
        cert_values = {key: repo.get(key) for key in cert_keys}

        # # Skip if all cert values are None, No cert scenario
        if all(value is None for value in cert_values.values()):
            continue

        # Find keys that have None values
        missing_keys = [key for key, value in cert_values.items() if value is None]
        if missing_keys:
            missing_certs.append(f"{repo_name} (missing keys: {missing_keys})")
            continue

        missing_files = check_cert_files_exist(repo_name, list(cert_values.values()))
        if missing_files:
            missing_certs.append(f"{repo_name} (missing files: {missing_files})")


    return missing_certs

def validate_certificates(local_repo_config_path, certs_path, repo_key="user_repo_url"):
    """Main function to load config and validate certs if any are defined."""
    config_file = load_yaml_file(local_repo_config_path)
    repo_list = get_repo_list(config_file, repo_key)

    missing = validate_repo_certificates(repo_list, certs_path)
    if missing:
        return {"status": "error", "missing": missing}

    return {"status": "ok"}


