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
import re
from ansible.module_utils.input_validation.common_utils import validation_utils
from ansible.module_utils.input_validation.common_utils import config
from ansible.module_utils.input_validation.common_utils import en_us_validation_msg
from ansible.module_utils.input_validation.validation_flows import common_validation

file_names = config.files
create_error_msg = validation_utils.create_error_msg
create_file_path = validation_utils.create_file_path

def validate_provision_config(input_file_path, data, logger, module, omnia_base_dir, module_utils_base, project_name):
    errors = []
    software_config_file_path = create_file_path(input_file_path, file_names["software_config"])
    software_config_json = json.load(open(software_config_file_path, "r"))

     # Call validate_software_config from common_validation
    software_errors = common_validation.validate_software_config(
        input_file_path,
        software_config_json,
        logger,
        module,
        omnia_base_dir,
        module_utils_base,
        project_name
    )
    errors.extend(software_errors)

    # Validate disk partition duplicates
    if "disk_partition" in data:
        mount_points = [partition.get('mount_point') for partition in data["disk_partition"]]
        unique_mount_points = set(mount_points)
        if len(mount_points) != len(unique_mount_points):
            errors.append(create_error_msg(
                "disk_partition",
                input_file_path,
                en_us_validation_msg.disk_partition_fail_msg
            ))

    # Validate language setting
    language = data.get("language", "")
    if not language:
        errors.append(create_error_msg(
            "language",
            input_file_path,
            en_us_validation_msg.language_empty_msg
        ))
    elif "en-US" not in language:
        errors.append(create_error_msg(
            "language",
            input_file_path,
            en_us_validation_msg.language_fail_msg
        ))

    # Validate domain name
    domain_name = data.get("domain_name", "")
    domain_pattern = r'^[a-zA-Z0-9.-]+$'
    if not domain_name or not re.match(domain_pattern, domain_name):
        errors.append(create_error_msg(
            "domain_name",
            domain_name,
            en_us_validation_msg.domain_name_fail_msg
        ))

    timezone_file_path = os.path.join(module_utils_base,'input_validation','common_utils','timezone.txt')
    pxe_mapping_file_path = data["pxe_mapping_file_path"]
    if data["pxe_mapping_file_path"] and not (validation_utils.verify_path(pxe_mapping_file_path)):
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

    if not data.get("Networks"):
        errors.append(create_error_msg(
            "Networks",
            None,
            en_us_validation_msg.admin_network_missing_msg
        ))
        return errors

    for network in data["Networks"]:
        # Validate admin network
        if "admin_network" in network:
            admin_net = network["admin_network"]

            # Validate admin network gateway format
            if "network_gateway" in admin_net and admin_net["network_gateway"]:
                gateway = admin_net["network_gateway"]
                if not validation_utils.validate_ipv4_range(gateway):
                    errors.append(create_error_msg(
                        "admin_network.network_gateway",
                        gateway,
                        en_us_validation_msg.network_gateway_fail_msg
                    ))

            # Validate admin network static/dynamic range format
            if "static_range" in admin_net and "dynamic_range" in admin_net:
                static_range = admin_net["static_range"]
                dynamic_range = admin_net["dynamic_range"]

                # First validate the IP range format for static and dynamic ranges
                if not validation_utils.validate_ipv4_range(static_range):
                    errors.append(create_error_msg(
                        "admin_network.static_range",
                        static_range,
                        en_us_validation_msg.range_ip_check_fail_msg
                    ))

                if not validation_utils.validate_ipv4_range(dynamic_range):
                    errors.append(create_error_msg(
                        "admin_network.dynamic_range",
                        dynamic_range,
                        en_us_validation_msg.range_ip_check_fail_msg
                    ))

                # Then check for overlap between static and dynamic ranges
                if validation_utils.validate_ipv4_range(static_range) and validation_utils.validate_ipv4_range(dynamic_range):
                    does_overlap, _ = validation_utils.check_overlap([static_range, dynamic_range])
                    range_info = {
                            "static_range": static_range,
                            "dynamic_range": dynamic_range
                        }
                    if does_overlap:
                        errors.append(create_error_msg(
                            "admin_network.ranges",range_info,
                            en_us_validation_msg.range_ip_check_overlap_msg
                        ))

        # Validate BMC network
        if "bmc_network" in network:
            bmc_net = network.get("bmc_network", {})

            # Skip validation if BMC network is empty or not configured
            if not any(bmc_net.values()):
                continue

            # Validate BMC network gateway format
            if bmc_net.get("network_gateway"):
                gateway = bmc_net["network_gateway"]
                if not validation_utils.validate_ipv4_range(gateway):
                    errors.append(create_error_msg(
                        "bmc_network.network_gateway",
                        gateway,
                        en_us_validation_msg.network_gateway_fail_msg
                    ))

            # Validate BMC network dynamic range and conversion range format
            if bmc_net.get("dynamic_range"):
                dynamic_range = bmc_net["dynamic_range"]
                if not validation_utils.validate_ipv4_range(dynamic_range):
                    errors.append(create_error_msg(
                        "bmc_network.dynamic_range",
                        dynamic_range,
                        en_us_validation_msg.range_ip_check_fail_msg
                    ))

            if bmc_net.get("dynamic_conversion_static_range"):
                conv_range = bmc_net["dynamic_conversion_static_range"]
                if not validation_utils.validate_ipv4_range(conv_range):
                    errors.append(create_error_msg(
                        "bmc_network.dynamic_conversion_static_range",
                        conv_range,
                        en_us_validation_msg.range_ip_check_fail_msg
                    ))

    return errors
