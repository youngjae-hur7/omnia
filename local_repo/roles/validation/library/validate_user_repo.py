#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.validate_utils import validate_certificates

def main():
    module_args = dict(
        local_repo_config_path=dict(type='str', required=True),
        certs_path=dict(type='str', required=True),
        repo_key=dict(type='str', required=False, default="user_repo_url")
    )

    result = dict(
        changed=False,
        failed=False,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        validation_result = validate_certificates(
            local_repo_config_path=module.params['local_repo_config_path'],
            certs_path=module.params['certs_path'],
            repo_key=module.params['repo_key']
        )

        if validation_result.get("status") == "error":
            result["failed"] = True
            result["msg"] = "Missing certificate keys or files detected:"
            for item in validation_result.get("missing", []):
                repo_name = item.split(" ")[0]
                # Append each missing repo and path
                result["msg"] += f"  - {item}. Expected certificate files should exist under: {module.params['certs_path']}/{repo_name}/"
        else:
            result["msg"] = f"All certificate checks passed for '{module.params['repo_key']}'."

    except Exception as e:
        module.fail_json(msg=f"Validation failed: {str(e)}", **result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()


