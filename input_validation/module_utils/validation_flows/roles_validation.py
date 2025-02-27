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

import json
import validation_utils
import config
import en_us_validation_msg
import common_validation

file_names = config.files
create_error_msg = validation_utils.create_error_msg
create_file_path = validation_utils.create_file_path

"""
Validates the L2 logic of the roles_config.yaml file.

Returns:
    list: A list of errors.
"""
def validate_roles_config(input_file_path, data, logger, module, omnia_base_dir, project_name):
    NAME = "name"
    ROLES = "Roles"
    GROUPS = "Groups"
    ROLE_GROUPS = "groups"
    SLURMWORKER = "slurmworker"
    K8WORKER = "k8worker"
    SWITCH_DETAILS = "switch_details"
    IP = "ip"
    PORTS = "ports"
    PARENT = "parent"
    BMC_DETAILS = "bmc_details"
    STATIC_RANGE = "static_range"
    RESOURCE_MGR_ID = "resource_mgr_id"
    ROLES_PER_GROUP = 5

    roles_per_group = {}
    empty_parent_roles = {'login', 'compiler', 'service', 'k8head', 'slurmhead'}

    errors = []
    provision_config_file_path = create_file_path(input_file_path, file_names["provision_config"])
    provision_config_json = validation_utils.load_yaml_as_json(provision_config_file_path, omnia_base_dir, project_name, logger, module)

    provision_config_credentials_file_path = create_file_path(input_file_path, file_names["provision_config_credentials"])
    provision_config_credentials_json = validation_utils.load_yaml_as_json(provision_config_credentials_file_path, omnia_base_dir, project_name, logger, module)

    roles = data[ROLES]
    groups = data[GROUPS]
    
    # Check for at least 1 group
    # Check for at least 1 role
     # Check to make sure there are not more than 100 roles
    if len(groups) == 0:
        errors.append(create_error_msg("Current number of groups is " + str(len(groups)) + ":", None, en_us_validation_msg.min_number_of_groups_msg))
    if len(roles) == 0:
        errors.append(create_error_msg("Current number of roles is " + str(len(roles)) + ":", None, en_us_validation_msg.min_number_of_roles_msg))
    if len(roles) > 100:
        errors.append(create_error_msg("Current number of roles is " + str(len(roles)) + ":", None, en_us_validation_msg.max_number_of_roles_msg))
    
    if len(errors) <= 0:
        # List of groups which need to have their resource_mgr_id set
        set_resource_mgr_id = set()

        # Set switch_details_required based on if credentials are provided
        switch_details_required = False
        switch_snmp3_username = provision_config_credentials_json.get("switch_snmp3_username", "")
        switch_snmp3_password = provision_config_credentials_json.get("switch_snmp3_password", "")
        if (not validation_utils.is_string_empty(switch_snmp3_username) and not validation_utils.is_string_empty(switch_snmp3_password)):
            switch_details_required = True
        
        # Get enable_switch_based boolean from provision config
        enable_switch_based = provision_config_json.get("enable_switch_based", False)

        # Check if the bmc_network is defined
        bmc_network_defined = check_bmc_network(input_file_path, logger, module, omnia_base_dir, project_name)

        service_role_defined = False
        if validation_utils.key_value_exists(roles, NAME, "service"):
            service_role_defined = True

        for role in roles:
            # Check role-group association, all roles must have a group
            if role[ROLE_GROUPS] and len(role[ROLE_GROUPS]) == 0:
                errors.append(role[NAME], create_error_msg("Role " + role[NAME] + " must be associated with a group.", en_us_validation_msg.min_number_of_groups_msg))
            if role[NAME] == SLURMWORKER or role[NAME] == K8WORKER:
                for group in role[ROLE_GROUPS]:
                    set_resource_mgr_id.add(group)
            
            if not role[ROLE_GROUPS]:
                role[ROLE_GROUPS] = []
            # Validate each group and its configs under each role
            for group in role[ROLE_GROUPS]:
                roles_per_group[group] = roles_per_group.get(group, 0) + 1
                if roles_per_group[group] > ROLES_PER_GROUP:
                    errors.append(create_error_msg(group, "Current number of roles for " + group + " is " + str(roles_per_group[group]) + ":", en_us_validation_msg.max_number_of_roles_per_group_msg))
                if group in groups:
                    if switch_details_required:
                        # Validate switch details based on if switch credentials were provided
                        # If switch credentials provided then IP and Ports info must be present
                        # If switch credentials not provided then IP and Ports info should be empty
                        if validation_utils.is_string_empty(groups[group].get(SWITCH_DETAILS, {}).get(IP, None)):
                            errors.append(create_error_msg(group, "Switch is missing IP information.", en_us_validation_msg.switch_details_required_msg))
                        if validation_utils.is_string_empty(groups[group].get(SWITCH_DETAILS, {}).get(PORTS, None)):
                            errors.append(create_error_msg(group, "Switch is missing ports information.", en_us_validation_msg.switch_details_required_msg))
                    else:
                        if not validation_utils.is_string_empty(groups[group].get("switch_details", {}).get(IP, None)) or not validation_utils.is_string_empty(groups[group].get("switch_details", {}).get("ports", None)):
                            errors.append(create_error_msg(group, "Switch should not have IP or ports information set.", en_us_validation_msg.switch_details_not_required_msg))
                
                    # Validate parent feild is empty for specific role cases
                    if role[NAME] in empty_parent_roles:
                        # If parent is not empty and group  is associated with login, compiler, service, k8head, or slurmhead
                        if not validation_utils.is_string_empty(groups[group].get(PARENT, None)):
                            errors.append(create_error_msg(group, "Group " + group + " should not have parent defined.", en_us_validation_msg.parent_service_node_msg))
                    if not service_role_defined and role[NAME] == "worker" or role[NAME] == "default":
                        # If a service role is not present, the parent is not empty and the group is associated with worker or default roles. 
                        if not validation_utils.is_string_empty(groups[group].get(PARENT, None)):
                            errors.append(create_error_msg(group, "Group " + group + " should not have parent defined.", en_us_validation_msg.parent_service_role_dne_msg))
                
                    if not validation_utils.is_string_empty(groups[group].get(BMC_DETAILS, {}).get(STATIC_RANGE, None)):
                        # Check if bmc details are defined, but enable_switch_based is true or the bmc_network is not defined
                        if enable_switch_based or not bmc_network_defined:
                            errors.append(create_error_msg(group, "Group " + group + " BMC static range invalid use case.", en_us_validation_msg.bmc_static_range_msg))
                        # Validate the static range is properly defined
                        elif not validation_utils.validate_ipv4_range(groups[group].get(SWITCH_DETAILS, {}).get(SWITCH_DETAILS, "")):
                            errors.append(create_error_msg(group, "Group " + group + " BMC static range is invalid.", en_us_validation_msg.bmc_static_range_invalid_msg))
                else: 
                    # Error log for if a group under a role does not exist
                    errors.append(create_error_msg(group, "Group " + group + " does not exist.", en_us_validation_msg.grp_exist_msg))
        
        for group in groups.keys():
            # Validate resource_mgr_id is set for groups that belong to k8worker or slurmworker roles
            if group in set_resource_mgr_id and validation_utils.is_string_empty(groups[group].get(RESOURCE_MGR_ID, None)):
                errors.append(create_error_msg(group, "Group " + group + " is missing resource_mgr_id.", en_us_validation_msg.resource_mgr_id_msg))
            elif group not in set_resource_mgr_id and not validation_utils.is_string_empty(groups[group].get(RESOURCE_MGR_ID, None)):
            # Validate resource_mgr_id is not set for groups that do not belong to k8worker or slurmworker roles
                errors.append(create_error_msg(group, "Group " + group + " should not have the resource_mgr_id set.", en_us_validation_msg.resource_mgr_id_msg))

    return errors

"""
Check if the BMC network is defined in the given input file.

Returns:
    bool: True if the BMC network's nic_name and netmask_bits are defined, False otherwise.
"""
def check_bmc_network(input_file_path, logger, module, omnia_base_dir, project_name) -> bool:
    admin_bmc_networks = common_validation.get_admin_bmc_networks(input_file_path, logger, module, omnia_base_dir, project_name)
    bmc_network_defined = admin_bmc_networks["bmc_network"].get("nic_name", None) != None and admin_bmc_networks["bmc_network"].get("netmask_bits", None) != None

    return bmc_network_defined