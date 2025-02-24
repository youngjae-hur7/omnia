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

file_names = config.files
create_error_msg = validation_utils.create_error_msg
create_file_path = validation_utils.create_file_path

def validate_roles_config(input_file_path, data, logger, module, omnia_base_dir, project_name):
    errors = []
    # roles_config_file_path = create_file_path(input_file_path, file_names["roles_config"])
    # provision_config_json = validation_utils.load_yaml_as_json(roles_config_file_path, omnia_base_dir, project_name, logger, module)

    roles = data["Roles"]
    groups = data["Groups"]

    if len(groups) == 0:
        errors.append(create_error_msg("Current number of groups is " + str(len(groups)) + ":", None, en_us_validation_msg.min_number_of_groups_msg))
    if len(roles) == 0:
        errors.append(create_error_msg("Current number of roles is " + str(len(roles)) + ":", None, en_us_validation_msg.min_number_of_roles_msg))
    if len(roles) > 100:
        errors.append(create_error_msg("Current number of roles is " + str(len(roles)) + ":", None, en_us_validation_msg.max_number_of_roles_msg))
   
    # List of groups which need to have their resource_mgr_id set
    set_resource_mgr_id = set()

    for role in roles:
        if len(role["groups"]) == 0:
            errors.append(create_error_msg("Role " + role["name"] + " must be associated with a group" + ":", None, en_us_validation_msg.min_number_of_groups_msg))
        if role["name"] == "slurmworker" or role["name"] == "k8worker":
            for group in role["groups"]:
                set_resource_mgr_id.add(group)
    
    for group in groups.keys():
        if group in set_resource_mgr_id and (groups[group].get("resource_mgr_id") == None or groups[group].get("resource_mgr_id") == ""):
            errors.append(create_error_msg("Group " + group + " is missing resource_mgr_id" + ":", None, en_us_validation_msg.resource_mgr_id_msg))
        elif group not in set_resource_mgr_id and (groups[group].get("resource_mgr_id") != None or groups[group].get("resource_mgr_id") != ""):
            errors.append(create_error_msg("Group " + group + " should not have the resource_mgr_id set" + ":", None, en_us_validation_msg.resource_mgr_id_msg))

    return errors