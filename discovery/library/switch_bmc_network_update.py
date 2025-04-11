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
 
#!/usr/bin/python3


from ansible.module_utils.basic import AnsibleModule
import subprocess

def main():
    module_args = dict(
        groups_roles_info=dict(type='dict', required=True),
        oim_nic_name=dict(type='str', required=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    groups_roles_info = module.params['groups_roles_info']
    bmc_interface_name = module.params['oim_nic_name']
    update_network_msg = ""
    failed_networks = []
    created_networks = []
    for group, details in groups_roles_info.items():
        if not details.get("switch_status"):
            continue

        bmc_info = details.get("bmc_details", {})
        bmc_network = bmc_info.get("network")
        bmc_nic_ip = bmc_info.get("interface_ip")
        netmask = bmc_info.get("netmask")

        if not all([bmc_network, bmc_nic_ip, netmask]):
            failed_networks.append((group, "Missing BMC network info"))
            continue
  
        # Check if this network already exists in xCAT's networks table
        grep_check = subprocess.run(
            ["bash", "-c", f"tabdump networks | grep -E '{bmc_nic_ip}'"],
            capture_output=True,
            text=True
        )

        if grep_check.returncode == 0:
            continue  # Already exists, skip defining it again

        # Define the network using chdef
        result = subprocess.run([
            "/opt/xcat/bin/chdef",
            "-t", "network",
            "-o", f"{group}_network",
            f"net={bmc_network}",
            f"mask={netmask}",
            f"mgtifname={bmc_interface_name}",
            f"gateway={bmc_nic_ip}",
            f"dhcpserver={bmc_nic_ip}",
            f"tftpserver={bmc_nic_ip}"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            failed_networks.append((f"{group}_network", result.stderr.strip()))
        else:
            created_networks.append(f"{group}_network")
            update_network_msg += f"\n Network created for group {group}"

    msg = ""
    if created_networks:
        msg += "Networks table entry added for: " + ", ".join(created_networks) + "."
    if failed_networks:
        msg += "\n Failed to create network table entry for :\n" + "\n".join([f"{g}: {err}" for g, err in failed_networks])
    if not msg:
        msg = "No new networks created."
 
    module.exit_json(
        changed=True,
        msg = msg,
        updated_groups_roles_info=groups_roles_info
    )

if __name__ == '__main__':
    main()
