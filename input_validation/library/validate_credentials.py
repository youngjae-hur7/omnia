#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import json
import re

def load_rules(file_path):
    """Loads validation rules from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_input(field, value, rules):
    """Validates input against rules."""
    if field not in rules:
        return (False, f"Validation rules not found for '{field}'")

    rule = rules[field]
    if not (rule["minLength"] <= len(value) <= rule["maxLength"]):
        return (False, f"'{field}' length must be between {rule['min_length']} and {rule['max_length']} characters")

    if "pattern" in rule and not re.match(rule["pattern"], value):
        return (False, f"'{field}' format is invalid. Expected pattern: {rule['pattern']}")
    return (True, f"'{field}' is valid")

def main():
    """Main module function."""
    module_args = dict(
        credential_field=dict(type="str", required=True),
        credential_input=dict(type="str", required=True),
        rules_file=dict(type="str", required=False, default="input_validation/module_utils/schema/credential_rules.json")
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    params = module.params

    # Load validation rules
    try:
        rules = load_rules(params["rules_file"])
    except Exception as e:
        module.fail_json(msg=f"Failed to load rules: {e}")

    # Validate credential
    credential_valid, credential_msg = validate_input(params["credential_field"], params["credential_input"], rules)

    if credential_valid:
        module.exit_json(changed=False, msg=f"{credential_msg}")
    else:
        module.fail_json(msg=f"Validation failed: {credential_msg}")

if __name__ == "__main__":
    main()
