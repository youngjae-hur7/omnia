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
from ansible.module_utils.omniadb_connection import execute_select_query
import subprocess

def create_node_object():
    """
    Create node objects in the database based on switch information.
    """

    sql = '''SELECT switch_name, switch_port FROM cluster.nodeinfo WHERE switch_port IS NOT NULL and switch_name IS NOT NULL'''
    switch_port_output = execute_select_query(query=sql)

    results = []
    if not switch_port_output:
        return results
    for switch in switch_port_output:
        switch_name = switch['switch_name']
        switch_port = switch['switch_port']
        sql = f"SELECT * FROM cluster.nodeinfo WHERE switch_port = %s AND switch_name = %s"
        row_output = execute_select_query(query=sql, params=(switch_port, switch_name))[0]
        groups_switch_based = 'switch_based,all'
        if row_output:
            groups_switch_based += row_output['roles']
            groups_switch_based += row_output['group_name']
            command = [
                "/opt/xcat/bin/chdef", row_output['node'], f"groups={groups_switch_based}", "mgt=ipmi", "cons=ipmi",
                f"ip={row_output['admin_ip']}", f"bmc={row_output['bmc_ip']}", "netboot=xnba", "installnic=mac", "primarynic=mac",
                f"switch={row_output['switch_ip']}", f"switchport={row_output['switch_port']}"
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            results.append({
                "node": row_output[0],
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            })

    return results

def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )
    results = create_node_object()

    module.exit_json(changed=True, results=results)

if __name__ == '__main__':
    main()
