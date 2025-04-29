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

#!/usr/bin/python
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.local_repo.common_functions import is_encrypted, run_vault_command, get_repo_list, load_yaml_file
from ansible.module_utils.local_repo.config import (
    USER_REPO_URL,
    LOCAL_REPO_CONFIG_PATH_DEFAULT,
    VAULT_KEY_PATH
)

def process_file(file_path, vault_key, mode):
    """
    Encrypt or decrypt a file using Ansible Vault.

    Args:
        file_path (str): The path to the file.
        vault_key (str): The path to the Ansible Vault key.
        mode (str): The mode of operation, either 'encrypt' or 'decrypt'.

    Returns:
        tuple: A tuple containing a boolean indicating whether the operation was successful and a message.
    """
    if not os.path.isfile(file_path):
        return False, f"File not found: {file_path}"

    currently_encrypted = is_encrypted(file_path)
    success = False
    message = ""

    if mode == 'encrypt':
        if currently_encrypted:
            success, message = True, f"Already encrypted: {file_path}"
        else:
            code, out, err = run_vault_command('encrypt', file_path, vault_key)
            if code == 0:
                success, message = True, f"Encrypted: {file_path}"
            else:
                message = f"Failed to encrypt {file_path}: {err}"

    elif mode == 'decrypt':
        if not currently_encrypted:
            success, message = True, f"Already decrypted: {file_path}"
        else:
            code, out, err = run_vault_command('decrypt', file_path, vault_key)
            if code == 0:
                success, message = True, f"Decrypted: {file_path}"
            else:
                message = f"Failed to decrypt {file_path}: {err}"
    else:
        message = f"Invalid mode for {file_path}"

    return success, message
    
def extract_repos_with_certs(repo_entries):
    """
    Extracts repositories that include SSL certificate configuration.

    Args:
        repo_entries (list): List of dictionaries with possible keys:
                             'name', 'sslcacert', 'sslclientkey', 'sslclientcert'.

    Returns:
        list: A list of dictionaries, each containing 'name', 'sslcacert',
              'sslclientkey', and 'sslclientcert' for repos where 'sslcacert' is present.
    """
    results = []

    for entry in repo_entries:
        if "sslcacert" in entry and entry["sslcacert"]:
            results.append({
                "name": entry.get("name", "unknown"),
                "sslcacert": entry["sslcacert"],
                "sslclientkey": entry.get("sslclientkey", ""),
                "sslclientcert": entry.get("sslclientcert", "")
            })

    return results

def main():
    """
    Encrypt or decrypt files using Ansible Vault.

    The module takes in the following parameters:
        * file_path: The path to the file to encrypt or decrypt.
        * dir_path: The path to the directory containing files to encrypt or decrypt.
        * vault_key: The path to the Ansible Vault key.
        * mode: The mode of operation, either 'encrypt' or 'decrypt'.

    The module is mutually exclusive for file_path and dir_path.
    The module requires one of file_path or dir_path.
    The module does not support check mode.
    """
    module = AnsibleModule(
    argument_spec={
        'mode': {'type': 'str', 'required': True, 'choices': ['encrypt', 'decrypt']}
    },
    supports_check_mode=False
    )
    mode = module.params['mode']
    
    local_repo_config = load_yaml_file(LOCAL_REPO_CONFIG_PATH_DEFAULT)
    user_repos = local_repo_config.get(USER_REPO_URL, [])
    
    cert_entries = extract_repos_with_cert(user_repos)
    for entry in cert_entries:
        for key in ["sslcacert", "sslclientkey", "sslclientcert"]:
            path = entry.get(key)
            if path and not os.path.isfile(path):
                module.fail_json(msg=f"Missing {key} for repo '{entry['name']}': {path}")
                
    messages = []
    changed = False
    for entry in cert_entries:
        for key in ["sslcacert", "sslclientkey", "sslclientcert"]:
            path = entry.get(key)
            if path:
                result, msg = process_file(path, VAULT_KEY_PATH, mode)
                if result is False:
                    module.fail_json(msg=f"Failed to decrypt {key} for repo '{entry['name']}': {msg}")
                else:
                    messages.append(msg)
                    changed = True
                    
    module.exit_json(changed=changed, msg="; ".join(messages))

if __name__ == '__main__':
    main()
