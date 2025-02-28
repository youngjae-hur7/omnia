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

import subprocess
import sys

db_path = sys.argv[3]
sys.path.insert(0, db_path)
import omniadb_connection

node_obj_nm = []
groups_static = "all,bmc_static"
groups_dynamic = "all,bmc_dynamic"
chain_setup = "runcmd=bmcsetup"
provision_os_image = sys.argv[1]
service_os_image = sys.argv[2]
chain_os = f"osimage={provision_os_image}"
discovery_mechanism = "mtms"


def get_node_obj():
    """
	Get a list of node objects present in Omnia Infrastrcuture Management (OIM) node

	Returns:
		A list of node object names
	"""

    command = "/opt/xcat/bin/lsdef"
    node_objs = subprocess.run(command.split(), capture_output=True)
    temp = str(node_objs.stdout).split('\n')
    for i in range(0, len(temp) - 1):
        node_obj_nm.append(temp[i].split(' ')[0])

    update_node_obj_nm()


def update_node_obj_nm():
    """
	Update the node objects with proper details as per their bmc mode.

	This function establishes a connection with omniadb and performs the following tasks:
	- Executes a SQL query to select the service_tag from the cluster.nodeinfo table where the discovery_mechanism is equal to the given discovery_mechanism.
	- Iterates over the serial_output and checks if the service_tag is not None.
	- If the condition is true, it converts the service_tag to lowercase.
	- Iterates over the serial_output and prints the service_tag.
	- Checks if the service_tag is not None.
	- If the condition is true, it converts the service_tag to uppercase.
	- Executes a SQL query to select the node from the cluster.nodeinfo table where the service_tag is equal to the current serial_output.
	- Fetches the node_name.
	- Executes a SQL query to select the admin_ip from the cluster.nodeinfo table where the service_tag is equal to the current serial_output.
	- Fetches the admin_ip.
	- Executes a SQL query to select the bmc_mode from the cluster.nodeinfo table where the service_tag is equal to the current serial_output.
	- Fetches the mode.
	- Checks if the mode is None.
	- If the condition is true, it prints a warning message.
	- Checks if the mode is equal to "static".
	- If the condition is true, it executes a command to update the node object with the given admin_ip, groups, and chain.
	- Checks if the mode is equal to "dynamic".
	- If the condition is true, it executes a command to update the node object with the given admin_ip, groups, and chain.
	- Executes a SQL query to select the bmc_ip from the cluster.nodeinfo table where the service_tag is equal to the current serial_output.
	- Fetches the bmc_ip.
	- Executes a command to update the node object with the given bmc_ip.

	Parameters:
	None

	Returns:
	None
	"""

    # Establish a connection with omniadb
    conn = omniadb_connection.create_connection()
    cursor = conn.cursor()
    sql = """select service_tag from cluster.nodeinfo where discovery_mechanism = %s"""
    cursor.execute(sql, (discovery_mechanism,))
    serial_output = cursor.fetchall()
    for i in range(0, len(serial_output)):
        if serial_output[i][0] is not None:
            serial_output[i] = str(serial_output[i][0]).lower()
    for i in range(0, len(serial_output)):
        print(serial_output[i])
        if serial_output[i][0] is not None:
            serial_output[i] = serial_output[i].upper()
            params = (serial_output[i],)
            sql = """SELECT node, admin_ip, bmc_ip, bmc_mode, role, group_name, architecture
                     FROM cluster.nodeinfo
                     WHERE service_tag = %s"""
            cursor.execute(sql, params)
            node_name, admin_ip, bmc_ip, mode, role, group_name, architecture = cursor.fetchone()

            if mode is None:
                print("No device is found!")
            if mode == "static":
                if service_os_image != "None" and 'service' in role:
                    chain_os = f"osimage={service_os_image}"
                command = ["/opt/xcat/bin/chdef", node_name, f"ip={admin_ip}", f"groups={groups_static},{role},{group_name}",
                           f"chain={chain_setup},{chain_os}", f"arch={architecture}"]
                subprocess.run(command)
            if mode == "dynamic":
                command = ["/opt/xcat/bin/chdef", node_name,
                           f"ip={admin_ip}", f"groups={groups_dynamic}",
                           f"chain={chain_setup},{chain_os}",
                           f"bmc={bmc_ip}"]
                subprocess.run(command)

    cursor.close()
    conn.close()


get_node_obj()
