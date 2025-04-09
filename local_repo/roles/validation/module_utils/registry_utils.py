import requests
from ansible.module_utils.common_functions import is_file_exists

def validate_user_registry(user_registry):
    for item in user_registry:
        if not isinstance(item, dict):
            return False, "Each item in user_registry must be a dictionary."
        if not item.get('host'):
            return False, f"Missing or empty 'host' in entry: {item}"
        if not item.get('cert_path'):
            return False, f"Missing 'cert_path' in entry: {item}"
    return True, ""

def check_reachability(user_registry, timeout):
    reachable, unreachable = [], []
    for item in user_registry:
        try:
            resp = requests.get(f"https://{item['host']}", timeout=timeout, verify=False)
            if resp.status_code == 200:
                reachable.append(item['host'])
            else:
                unreachable.append(item['host'])
        except Exception:
            unreachable.append(item['host'])
    return reachable, unreachable

def find_invalid_cert_paths(user_registry):
    return [
        item['cert_path'] for item in user_registry
        if item.get('cert_path') and not is_file_exists(item['cert_path'])
    ]

