Integrate External Nodes with Omnia Kubernetes Cluster
========================================================

Omnia provides you a way to integrate external nodes (with pre-installed Ubuntu OS) into an existing Omnia Kubernetes (K8s) cluster.

.. note:: Currently, this feature is only supported on nodes running Ubuntu 24.04 OS.

Prerequisites
--------------

Before integrating external nodes, ensure the following requirements are met:

* **OpenSSH**: Ensure OpenSSH is enabled during the Ubuntu OS installation process.
* **Enable root user**: Edit the ``/etc/ssh/sshd_config`` file and set ``PermitRootLogin yes`` (instead of ``PermitRootLogin prohibit-password``). 
* **Root password**: Ensure that all servers use the same root password.
* **Fully Qualified Domain Name (FQDN)**: Set the FQDN for each node (Example: ``compute1.omnia.test``). Ensure that the same is also updated in the ``etc/hosts`` file on the OIM.
* **IP Configuration**: Assign either a static or dynamic IP from the PXE network (Example: ``10.5.0.x``). Ensure that the same is also updated in the ``etc/hosts`` file on the OIM.
* **Internet Access**: The node should have internet access. To test the internet connection, execute: ::

    wget https://github.com/opencontainers/runc/releases/download/v1.2.3/runc.amd64

Steps to Integrate External Nodes
----------------------------------

1. Ensure that the OIM server is set up and running with Ubuntu 24.04 OS.

2. Activate the Omnia Python virtual environment using the following command:
   ::
	source /opt/omnia/omnia171_venv/bin/activate

3. Create an inventory file in the following format:
   
   ::

    [compute]
    10.5.0.101
    10.5.0.102
 
   .. note:: Only IP addresses are supported in the inventory file. Ensure that these IPs align with the PXE subnet.

4. Run the ``connect-external-server.yml`` playbook using the following command to connect the external servers, where ``<inventory>`` is the path to your inventory file:
   ::
	cd utils
	ansible-playbook connect-external-server.yml -i <inventory>

5. While execution, the playbook will prompt for the root password. Enter the root password that has been configured on all servers.

6. Navigate to the ``input/omnia_config.yml`` file and set the ``k8s_offline_install`` variable to ``false``. For more information, `click here <../OmniaInstallGuide/Ubuntu/OmniaCluster/schedulerinputparams.html#id1>`_.
   
   .. note:: If the ``input/omnia_config.yml`` file is encrypted, run the following command to decrypt it:
 	::
	   ansible-vault edit omnia_config.yml --vault-password-file .omnia_vault_key
   
7. Navigate to the ``input/software_config.json`` and remove all software entries except ``k8s`` and ``nfs``. Omnia supports adding external nodes with only these two entries in the ``input/software_config.json``. 

8. Run the ``omnia.yml`` to deploy a Kubernetes cluster with the new nodes, where ``<inventory>`` is the path to your inventory file consisting of the external nodes:
   ::
	ansible-playbook omnia.yml -i <inventory>

.. note:: A fresh Kubernetes cluster deployment does not support a mix of Omnia-provisioned nodes and external nodes with a pre-loaded OS. To build such a cluster, first deploy the Omnia-provisioned nodes by running ``omnia.yml`` with ``k8s_offline_install: true``. Once that's complete, add the pre-loaded OS nodes by re-running ``omnia.yml`` with ``k8s_offline_install: false``.

