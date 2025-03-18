#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import json

def load_rules(file_path):
    """Loads validation rules from JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def fetch_rule(field, rules):
    """Fetches validation rule for a given field."""
    if field not in rules:
        return (False, f"No validation rules found for '{field}'")

    rule = rules[field]
    return (True, rule.get("description", "No description available"))

def main():
    """Main function."""
    module_args = dict(
        credential_field=dict(type="str", required=True),
        rules_file=dict(type="str", required=False, default="input_validation/module_utils/schema/credential_rules.json")
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    params = module.params

    # Load validation rules
    try:
        rules = load_rules(params["rules_file"])
    except Exception as e:
        module.fail_json(msg=f"Failed to load rules: {e}")

    # Fetch and return rule description
    success, message = fetch_rule(params["credential_field"], rules)
    if success:
        module.exit_json(changed=False, msg=message, debug_rule=message)
    else:
        module.fail_json(msg=message)

if __name__ == "__main__":
    main()
