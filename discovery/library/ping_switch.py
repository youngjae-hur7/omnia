#  Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
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
import subprocess

def is_ip_reachable(ip):
    """Checks if an IP is reachable using the ping command."""
    result = subprocess.run(["ping", "-c", '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result.returncode == 0

def main():
    module_args = dict(
        groups_roles_info=dict(type='dict', required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    groups_roles_info = module.params['groups_roles_info']
    reachable_switch_groups = {}
    unreachable_switch_groups = {}
    switch_status = False

    for group, details in groups_roles_info.items():
        switch_info = details.get("switch_details", {})
        switch_ip = switch_info.get("ip")

        if switch_ip:
            try:
                ping_status = is_ip_reachable(switch_ip)
            except Exception as e:
                module.fail_json(msg=str(e))

            switch_status = switch_status or ping_status
            if ping_status:
                reachable_switch_groups[group] = details
            else:
                details['switch_status'] = False
                unreachable_switch_groups[group] = details
        else:
            module.fail_json(msg=f"Missing switch IP for group {group}")

    module.exit_json(
        changed=False,
        reachable_switch_groups=reachable_switch_groups,
        unreachable_switch_groups=unreachable_switch_groups,
        switch_status=switch_status,
    )

if __name__ == '__main__':
    main()
