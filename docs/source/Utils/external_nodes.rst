Integrate External Nodes with Omnia Kubernetes Cluster
========================================================

Omnia provides you a way to integrate external nodes (with pre-installed Ubuntu OS) into an existing Omnia Kubernetes (K8s) cluster. The integration supports both x86 and ARM architecture nodes.

.. note:: Currently, this feature is only supported on nodes running Ubuntu 24.04.01 OS.

Prerequisites
--------------

Before integrating external nodes, ensure the following requirements are met:

* **OpenSSH**: Ensure OpenSSH is enabled during the Ubuntu OS installation process.
* **Enable root user**: Edit the ``/etc/ssh/sshd_config`` file and set ``PermitRootLogin yes`` (instead of ``PermitRootLogin prohibit-password``). 
* **Fully Qualified Domain Name (FQDN)**: Set the FQDN for each node (for example; ``armcompute.omnia.test``) for ARM-based nodes.
* **IP Configuration**: Assign either a static or dynamic IP from the PXE network (for example; ``10.5.0.x``).
* **Internet Access**: The node should have internet access. To test the internet connection, execute: ::

    wget https://github.com/opencontainers/runc/releases/download/v1.2.3/runc.amd64

Steps to Integrate External Nodes
----------------------------------

1. Ensure that the OIM server is set up and running with Ubuntu 24.04.01 OS.

2. Activate the Omnia Python virtual environment using the following command:
   ::
	source /opt/omnia/omnia171_venv/bin/activate

3. Create an inventory file in the following format:
   
   ::

    [compute]
    10.3.0.101
    10.3.0.102
 
   .. note:: Only IP addresses are supported in the inventory file. Ensure that these IPs align with the PXE subnet.

4. Run the ``connect-external-server.yml`` playbook using the following command to connect the external servers, where ``<inventory>`` is the path to your inventory file:
   ::
	cd utils
	ansible-playbook connect-external-server.yml -i <inventory>

5. While execution, the playbook will prompt for the root password. Enter the root password that has been configured on all servers. Ensure that all servers use the same root password.

6. Navigate to the ``input/omnia_config.yml`` file and modify the ``k8s_offline_install`` variable:
   
   .. note:: If the file is encrypted, run the following command to decrypt it:
 	::
	   ansible-vault edit omnia_config.yml --vault-password-file .omnia_vault_key
   
   +-----------------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | Parameter                   | Details                                                                                                                         |
   +=============================+=================================================================================================================================+
   | ``k8s_offline_install``     | * **Type**: ``boolean``                                                                                                         |
   |                             | * **Default value**: ``true``.                                                                                                  |
   |                             | * Set it to ``false`` if you want to pull Kubernetes packages and images from the internet instead of the OIM local repository. |
   +-----------------------------+---------------------------------------------------------------------------------------------------------------------------------+
   
7. Run the ``omnia.yml`` to deploy a Kubernetes cluster with the new nodes, where ``<inventory>`` is the path to your inventory file consisting of the external nodes:
   ::
	ansible-playbook omnia.yml -i <inventory>