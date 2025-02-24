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

def check_switch_required(group_data):
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


def fetch_bmc_details(groups_data, roles_data, layer):
    """
    Fetches the bmc details for the given groups and roles.

    Args:
        groups_data (dict): A dictionary containing group information.
        roles_data (dict): A dictionary containing role information.
        layer (str): The layer of the roles.

    Returns:
        tuple: A tuple containing a boolean indicating if the bmc details are present,
        a boolean indicating if the switch details are present, and a dictionary of bmc details based on layer.

    Raises:
        Exception: If a group does not exist in the role_config.yml Groups dictionary.
    """

    if layer == "first":
        valid_roles = set(roles_data.keys()).intersection(FIRST_LAYER_ROLES)
    else:
        valid_roles = set(roles_data.keys()) - FIRST_LAYER_ROLES

    bmc_check = False
    bmc_details = {}

    for role in valid_roles:
        for group in roles_data[role]["groups"]:
            if groups_data.get(group, {}) and check_bmc_required(groups_data[group]):
                bmc_check = True
                switch_check = check_switch_required(groups_data[group])
                bmc_details[role] = {}
                bmc_details[role][group] = groups_data[group]
            else:
                raise Exception("Group `{}` doesn't exist in role_config.yml Groups dict".format(group))
    return bmc_check, switch_check, bmc_details


def fetch_mapping_details(groups_data, roles_data, node_df, layer):
    """
    Fetches the mapping details for the given groups and roles.

    Args:
        groups_data (dict): A dictionary containing group information.
        roles_data (dict): A dictionary containing role information.
        node_df (DataFrame): A DataFrame containing node information.
        layer (str): The layer of the roles.

    Returns:
        list: A list of dictionaries containing the filtered node details based on layer.

    """

    if layer == "first":
        valid_roles = set(FIRST_LAYER_ROLES).intersection(set(roles_data.keys()))
    else:
        valid_roles = set(roles_data.keys()) - FIRST_LAYER_ROLES

    # Create mappings
    group_to_roles = {}

    for role_name in valid_roles:
        for group in roles_data[role_name]["groups"]:
            group_to_roles.setdefault(group, []).append(role_name)

    # Organize node details
    filtered_nodes = []
    node_df = node_df[node_df['GROUP_NAME'].isin(group_to_roles.keys())]
    for _, node in node_df.iterrows():
        group = node["GROUP_NAME"]

        if group in group_to_roles:
            node_data = {
                "service_tag": node["SERVICE_TAG"],
                "hostname": node["HOSTNAME"],
                "admin_mac": node["ADMIN_MAC"],
                "admin_ip": node["ADMIN_IP"],
                "bmc_ip": node["BMC_IP"],
                "group_name": group,
                "roles": ",".join(group_to_roles[group]),
                "location_id": groups_data.get(group, {}).get("location_id", ""),
                "resource_mgr_id": groups_data.get(group, {}).get("resource_mgr_id", ""),
                "parent": groups_data.get(group, {}).get("parent", ""),
                "bmc_details": groups_data.get(group, {}).get("bmc_details", {}),
                "switch_details": groups_data.get(group, {}).get("switch_details", {}),
                "architecture": groups_data.get(group, {}).get("architecture", ""),
            }
            filtered_nodes.append(node_data)

    return filtered_nodes

def main():
    module_args = dict(
        roles_data=dict(type="list", required=True),
        groups_data=dict(type="dict", required=True),
        mapping_file_path=dict(type="str", required=True),
        layer=dict(type="str", choices=["first", "default"], required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        roles_list = module.params["roles_data"]
        groups = module.params["groups_data"]
        layer = module.params["layer"]
        node_df = load_csv(module.params["mapping_file_path"])
        roles = {role.pop('name'): role for role in roles_list}
        bmc_required, switch_required, bmc_details = fetch_bmc_details(groups, roles, layer)
        mapping_details = fetch_mapping_details(groups, roles, node_df, layer)
        module.exit_json(changed=False, mapping_details=mapping_details, roles_data=roles, groups_data=groups,
                            bmc_required=bmc_required, bmc_details=bmc_details if bmc_required else {}, switch_required=switch_required)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == "__main__":
    main()
