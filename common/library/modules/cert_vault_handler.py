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
from ansible.module_utils.common_functions import is_encrypted, run_vault_command

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
        'file_path': {'type': 'str', 'required': False},
        'dir_path': {'type': 'str', 'required': False},
        'vault_key': {'type': 'str', 'required': True},
        'mode': {'type': 'str', 'required': True, 'choices': ['encrypt', 'decrypt']}
    },
    mutually_exclusive=[['file_path', 'dir_path']],
    required_one_of=[['file_path', 'dir_path']],
    supports_check_mode=False
    )
    file_path = module.params['file_path']
    dir_path = module.params['dir_path']
    vault_key = module.params['vault_key']
    mode = module.params['mode']

    if not os.path.isfile(vault_key):
        module.fail_json(msg=f"Vault key file not found: {vault_key}")

    messages = []
    changed = False

    if file_path:
        result, msg = process_file(file_path, vault_key, mode)
        if result is False:
            module.fail_json(msg=msg)
        changed = changed or result
        messages.append(msg)

    elif dir_path:
        if not os.path.isdir(dir_path):
            module.fail_json(msg=f"Directory not found: {dir_path}")

        files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if not files:
            module.exit_json(changed=False, msg="No files to process in the directory.")

        successes = 0
        for f in files:
            result, msg = process_file(f, vault_key, mode)
            messages.append(msg)
            if result:
                changed = True
                successes += 1

        if successes == 0:
            module.exit_json(changed=False,
                msg="No changes made. Files were already in desired state:\n" + "\n".join(messages))

    module.exit_json(changed=changed, msg="; ".join(messages))

if __name__ == '__main__':
    main()
