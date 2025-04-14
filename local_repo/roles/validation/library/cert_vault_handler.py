#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common_functions import decrypt_certificate, encrypt_certificate

def run_module():
    module_args = dict(
        action=dict(type='str', required=True, choices=['encrypt', 'decrypt']),
        cert_path=dict(type='str', required=True),
        vault_password_file=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        message='',
        status=0
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    action = module.params['action']
    cert_path = module.params['cert_path']
    vault_password_file = module.params['vault_password_file']

    if action == 'decrypt':
        status = decrypt_certificate(cert_path, vault_password_file)
        result['status'] = status
        result['message'] = "Certificate decrypted successfully." if status == 1 else "Decryption failed. Please check the path or vault key."

    elif action == 'encrypt':
        status = encrypt_certificate(cert_path, vault_password_file)
        result['status'] = status
        result['message'] = "Certificate encrypted successfully." if status == 1 else "Encryption failed. Please check the path or vault key."

    result['changed'] = (status == 1)
    if status == 0:
        module.fail_json(msg=result['message'], **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
