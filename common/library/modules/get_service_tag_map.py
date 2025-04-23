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

def get_service_tag_map(hierarchical_service_node_data, service_ha_config):
    service_tag_map = {}

    # Iterate over hierarchical_service_node_data
    for node_key, node_data in hierarchical_service_node_data.items():
        service_tag = node_data.get('service_tag')
        if not service_tag:
            continue  # Skip if service_tag is not available

        # Default admin_ip
        ip_address = node_data.get('admin_ip', '')

        # Check if service_ha_config contains the service_tag and has active nodes
        if service_ha_config.get(service_tag):
            for node in service_ha_config[service_tag]:
                if node.get('active') and 'virtual_ip' in node:
                    ip_address = node.get('virtual_ip')
                    break  # We need only the virtual_ip from the active node

        # Add the mapping for the service_tag
        service_tag_map[service_tag] = {
            'node': node_key,
            'admin_ip': ip_address
        }

    return service_tag_map

def main():
    module = AnsibleModule(
        argument_spec={
            'hierarchical_service_node_data': {'type': 'dict', 'required': True},
            'service_ha_config': {'type': 'dict', 'required': True}
        },
        supports_check_mode=False
    )

    hierarchical_service_node_data = module.params['hierarchical_service_node_data']
    service_ha_config = module.params['service_ha_config']

    # Get the service tag map
    service_tag_map = get_service_tag_map(hierarchical_service_node_data, service_ha_config)

    # Return the result to Ansible
    module.exit_json(changed=False, service_tag_map=service_tag_map)

if __name__ == '__main__':
    main()
