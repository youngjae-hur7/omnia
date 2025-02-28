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
import sys
import subprocess

def validate_osimage(osimage):
    """Validates if the given `osimage` is a string."""
    if not isinstance(osimage, str):
        raise ValueError("osimage must be a string")
    return osimage

def nodeset_mapping_nodes(install_osimage, service_osimage, discovery_mechanism):
    """
    Retrieves the nodes from the cluster.nodeinfo table in omniadb and sets the osimage using nodeset.
    """
    import omniadb_connection

    # Establish connection with cluster.nodeinfo
    conn = omniadb_connection.create_connection()
    cursor = conn.cursor()
    sql = "SELECT node, role FROM cluster.nodeinfo WHERE discovery_mechanism = %s"
    cursor.execute(sql, (discovery_mechanism,))
    node_name = cursor.fetchall()
    cursor.close()
    conn.close()

    install_osimage = validate_osimage(install_osimage)
    service_osimage = validate_osimage(service_osimage)

    # Establish connection with omniadb
    conn_x = omniadb_connection.create_connection_xcatdb()
    cursor_x = conn_x.cursor()
    new_mapping_nodes = []
    changed = False

    for node in node_name:
        sql = "SELECT exists(SELECT node FROM nodelist WHERE node = %s AND status IS NULL)"
        cursor_x.execute(sql, (node[0],))
        output = cursor_x.fetchone()[0]

        if output:
            if service_osimage != "None" and 'service' in node[1]:
                osimage = service_osimage
            else:
                osimage = install_osimage

            new_mapping_nodes.append(node[0])
            command = ["/opt/xcat/sbin/nodeset", node[0], f"osimage={osimage}"]
            subprocess.run(command, capture_output=True, shell=False, check=True)
            changed = True
    cursor_x.close()
    conn_x.close()

    return {"changed": changed, "nodes_updated": new_mapping_nodes}

def main():
    module_args = dict(
        db_path=dict(type="str", required=True),
        discovery_mechanism=dict(type="str", required=True),
        install_osimage=dict(type="str", required=True),
        service_osimage=dict(type="str", required=True)
    )

    module = AnsibleModule( argument_spec=module_args, supports_check_mode=True)
    sys.path.insert(0, module.params["db_path"])  # Change this to the actual path

    try:
        if module.params["discovery_mechanism"] == "mapping":
            result = nodeset_mapping_nodes(
                module.params["install_osimage"],
                module.params["service_osimage"],
                module.params["discovery_mechanism"]
            )
            module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == "__main__":
    main()
