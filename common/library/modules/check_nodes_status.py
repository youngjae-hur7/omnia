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

#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

def run_cmd(cmd):
    run = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if 'ERROR' in run.stderr:
        return False, run.stderr.strip(), run.stdout.strip()
    else:
        return True, run.stderr.strip(), run.stdout.strip()

def get_discover_nodes(group_name):
    cmd = f'/opt/xcat/bin/lsdef -t group -o {group_name} | grep members | sed -n "/members=/s/    members=//p"'
    status, err, out = run_cmd(cmd)
    if status and out:
        return out.split(',')
    else:
        return []

def check_discover_nodes(nodelist):
    bmc_list = []
    for node in nodelist:
        node = node.strip()
        cmd = f'/opt/xcat/bin/lsdef {node} -i status -c | sed -n "/{node}: status=/s/{node}: status=//p"'
        status, err, out = run_cmd(cmd)
        if status and not out.strip():
            bmc_list.append(node)
    return bmc_list

def main():
    module = AnsibleModule(
        argument_spec=dict(
            group_name=dict(type='str', required=True)
        )
    )

    group_name = module.params['group_name']

    try:
        nodelist = get_discover_nodes(group_name)
        if not nodelist:
            module.exit_json(changed=False, discovered_nodes=[], message=f"No members found in group {group_name}")

        new_nodes = check_discover_nodes(nodelist)
        module.exit_json(changed=False, discovered_nodes=new_nodes)

    except Exception as e:
        module.fail_json(msg=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
