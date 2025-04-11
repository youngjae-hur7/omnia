import os
import yaml
from ansible.module_utils.common_functions import (
    load_yaml_file,
    get_repo_list,
)

def get_pem_files(repo_cert_path):
    """
    Return a list of .pem files in the given repository certificate path.
    If the directory doesn't exist, return an empty list.
    """
    if not os.path.isdir(repo_cert_path):
        return None  # Explicitly indicate missing directory
    return [f for f in os.listdir(repo_cert_path) if f.endswith(".pem")]

def validate_repo_certificates(repo_list, certs_path):
    """
    Validate that each repo has exactly 3 .pem files,
    and optionally at most 1 .key and 1 .crt file in its certs path.
    """
    cert_issues = []

    for repo in repo_list:
        repo_name = repo.get("name", "unnamed_repo")
        repo_cert_path = os.path.join(certs_path, repo_name)

        cert_keys = ["sslcacert", "sslclientkey", "sslclientcert"]
        cert_values = {key: repo.get(key) for key in cert_keys}

        # # Skip if all cert values are None, No cert scenario
        if all(value is None for value in cert_values.values()):
            continue

        if not os.path.isdir(repo_cert_path):
            cert_issues.append(f"{repo_name} (certificate path not found)")
            continue

        all_files = os.listdir(repo_cert_path)
        pem_files = [f for f in all_files if f.endswith(".pem")]
        key_files = [f for f in all_files if f.endswith(".key")]
        crt_files = [f for f in all_files if f.endswith(".crt")]

        issues = []

        if len(pem_files) != 3:
            issues.append(f"{len(pem_files)} .pem files found: {pem_files}")
        if len(key_files) > 1:
            issues.append(f"{len(key_files)} .key files found: {key_files}")
        if len(crt_files) > 1:
            issues.append(f"{len(crt_files)} .crt files found: {crt_files}")

        if issues:
            cert_issues.append(f"{repo_name} ({'; '.join(issues)})")

    return cert_issues


def validate_certificates(local_repo_config_path, certs_path, repo_key="user_repo_url"):
    """
    Main entry point to validate certificates for repositories.
    Reads YAML config, extracts the repository list, and validates each.
    """
    config_file = load_yaml_file(local_repo_config_path)
    repo_list = get_repo_list(config_file, repo_key)

    issues = validate_repo_certificates(repo_list, certs_path)

    if issues:
        return {"status": "error", "missing": issues}

    return {"status": "ok"}

