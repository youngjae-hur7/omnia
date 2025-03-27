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
from ansible.module_utils import omniadb_connection
from ansible.module_utils.omniadb_connection import execute_select_query, insert_switch_info
import subprocess

# Global variables
switch_name_prefix = "switch"
switch_group = "switch"
switch_snmp_version = 3
switch_auth_type = "sha"


def create_table_switchinfo():
    """
    Creates cluster.switchinfo table for switch_based discovery mechanism
    """

    # Create cluster.switchinfo table
    conn = omniadb_connection.create_connection()
    cursor = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS cluster.switchinfo(
        ID SERIAL NOT NULL PRIMARY KEY UNIQUE,
        switch_ip INET,
        switch_name VARCHAR(30),
        group_name VARCHAR(15))'''
    cursor.execute(sql)
    cursor.close()

def create_switch_object(group, switch_ip, switch_snmp_username, switch_snmp_password):

    # Check if switch already exists in the database
    sql = f"SELECT EXISTS(SELECT switch_ip FROM cluster.switchinfo WHERE switch_ip=%s)"
    output_switch_ip = execute_select_query(query=sql, params=(switch_ip,))[0]
    msg = ''
    if output_switch_ip and output_switch_ip.get('exists', False):
        msg = f'Switch -(ip- {switch_ip}) already exists in the database'
        return msg
    # Generate switch_name
    result = execute_select_query("SELECT id FROM cluster.switchinfo ORDER BY id DESC LIMIT 1")
    switch_id = int(result[0]['id']) + 1 if result else 1
    switch_name = f"{switch_name_prefix}{switch_id}"

    msg = insert_switch_info(switch_name, switch_ip, group)

    # Create switch object
    subprocess.run(["/opt/xcat/bin/chdef", switch_name, f"ip={switch_ip}", f"groups={switch_group},{group}"])

    # Update xCAT switches table with switch credentials
    subprocess.run([
        "/opt/xcat/sbin/tabch",
        f"switch={switch_name}",
        f"switches.snmpversion={switch_snmp_version}",
        f"switches.username={switch_snmp_username}",
        f"switches.password={switch_snmp_password}",
        f"switches.auth={switch_auth_type}"
    ])

    msg += f"\nCreated switch object for: {switch_name}"
    return msg


def main():
    """
    Main function to process Ansible input and execute switch provisioning.

    Parameters:
    None

    Returns:
    None
    """
    module_args = dict(
        groups_roles_info=dict(type='dict', required=True),
        switch_snmp3_username=dict(type='str', required=True),
        switch_snmp3_password=dict(type='str', required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    groups_roles_info = module.params['groups_roles_info']
    switch_snmp3_username = module.params['switch_snmp3_username']
    switch_snmp3_password = module.params['switch_snmp3_password']

    create_table_switchinfo()
    msg = []

    for group, details in groups_roles_info.items():
        if details.get("switch_status", False):  # Only process if switch_status is True
            switch_info = details.get("switch_details", {})
            switch_ip = switch_info.get("ip", '')
            output = create_switch_object(group, switch_ip, switch_snmp3_username, switch_snmp3_password)
            msg.append(output)

    msg = '\n'.join(msg)
    module.exit_json(changed=True, msg=msg)


if __name__ == '__main__':
    main()