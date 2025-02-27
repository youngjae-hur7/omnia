# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.utility import load_csv

FIRST_LAYER_ROLES = {"service", "login", "compiler", "k8setcd", "k8shead", "slurmhead", "slurmdbd"}

def check_switch_required(group_data, layer):
    if layer == 'first':
        return False
    switch_data = group_data.get("switch_details", {})
    if switch_data and switch_data.get("ip", '') and switch_data.get("ports", ''):
        return True
    else:
        return False

def check_bmc_required(group_data):
    bmc_data = group_data.get("bmc_details", {})
    if bmc_data and bmc_data.get("static_range", ''):
        return True
    else:
        return False

def filter_roles(groups_data, roles_data, layer):

    if layer == "first":
        valid_roles = set(roles_data.keys()).intersection(FIRST_LAYER_ROLES)
    else:
        valid_roles = set(roles_data.keys()) - FIRST_LAYER_ROLES
    return valid_roles


def roles_groups_mapping(groups_data, roles_data, layer):

    valid_roles = filter_roles(groups_data, roles_data, layer)

    bmc_check = False
    switch_check = False
    roles_groups_data = {}
    groups_roles_info = {}

    for role in valid_roles:
        for group in roles_data[role]["groups"]:

            if groups_data.get(group, {}):
                groups_roles_info.setdefault(group, {}).setdefault('roles', []).append(role)
                groups_roles_info[group].update(groups_data.get(group))
                bmc_check = bmc_check or check_bmc_required(groups_data[group])
                switch_check = switch_check or check_switch_required(groups_data[group], layer)
                roles_groups_data[role] = {}
                roles_groups_data[role][group] = groups_data[group]
            else:
                raise Exception("Group `{}` doesn't exist in roles_config.yml Groups dict".format(group))

    return bmc_check, switch_check, roles_groups_data, groups_roles_info

def main():
    module_args = dict(
        roles_data=dict(type="list", required=True),
        groups_data=dict(type="dict", required=True),
        layer=dict(type="str", choices=["first", "default"], required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        roles_list = module.params["roles_data"]
        groups = module.params["groups_data"]
        layer = module.params["layer"]
        roles = {role.pop('name'): role for role in roles_list}
        need_bmc, need_switch, roles_groups_data, groups_roles_info = roles_groups_mapping(groups, roles, layer)
        module.exit_json(changed=False, roles_data=roles, groups_data=groups, groups_roles_info=groups_roles_info,
                            bmc_required=need_bmc, roles_groups_data=roles_groups_data, switch_required=need_switch)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == "__main__":
    main()
