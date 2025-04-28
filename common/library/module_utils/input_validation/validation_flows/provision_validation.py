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
import os
from ansible.module_utils.input_validation.common_utils import validation_utils
from ansible.module_utils.input_validation.common_utils import config
from ansible.module_utils.input_validation.common_utils import en_us_validation_msg

file_names = config.files
create_error_msg = validation_utils.create_error_msg
create_file_path = validation_utils.create_file_path

def validate_provision_config(input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name):
    errors = []
    software_config_file_path = create_file_path(input_file_path, file_names["software_config"])
    software_config_json = json.load(open(software_config_file_path, "r"))
    cluster_os_type = software_config_json["cluster_os_type"]
    cluster_os_version = software_config_json["cluster_os_version"]
    timezone_file_path = os.path.join(module_utils_base,'input_validation','common_utils','timezone.txt')
    pxe_mapping_file_path = data.get("pxe_mapping_file_path", '')
    if pxe_mapping_file_path and not (validation_utils.verify_path(pxe_mapping_file_path)):
        errors.append(create_error_msg("pxe_mapping_file_path", pxe_mapping_file_path, en_us_validation_msg.pxe_mapping_file_path_fail_msg))

    timezone = data["timezone"]
    if not (validation_utils.validate_timezone(timezone, timezone_file_path)):
        errors.append(create_error_msg("timezone", timezone, en_us_validation_msg.timezone_fail_msg))

    default_lease_time = data["default_lease_time"]
    if not (validation_utils.validate_default_lease_time(default_lease_time)):
        errors.append(create_error_msg("default_lease_time", default_lease_time, en_us_validation_msg.default_lease_time_fail_msg))

     # Validate NTP support
    ntp_support = data["ntp_support"]
    if ntp_support is None or ntp_support == "":
        errors.append(create_error_msg("ntp_support", ntp_support, en_us_validation_msg.ntp_support_empty_msg))

    return errors

def validate_network_spec(input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name):
    errors = []
    return errors