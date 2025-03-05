Intel Gaudi accelerators
==========================

⦾ **Why does the** ``hl-smi`` **command fail to detect the Intel Gaudi drivers installed during provisioning?**

.. image:: ../../../images/intel_known_issue.png

**Potential Cause**: This occurs when the Intel Gaudi node has internet access during provisioning. If the node has internet access, the OS kernel gets updated during provisioning which impacts the Gaudi driver installation.

**Resolution**: If you encounter the above-mentioned error, run the ``accelerator.yml`` playbook to fix the issue. Omnia recommends to install the Intel Gaudi driver post provisioning using the ``accelerator.yml`` playbook in case the node has internet connectivity during provisioning. For more information, `click here <../../../OmniaInstallGuide/Ubuntu/AdvancedConfigurationsUbuntu/Habana_accelerator.html>`_.

⦾ **Missing Intel Gaudi Infiniband device files after cluster provisioning**

**Potential Cause**: The missing hb_devices (such as hbl_0, hbl_1, hbl_2, hbl_3, hbl_4, hbl_5, hbl_6, hbl_7) in the ``/sys/class/infiniband`` directory issue is caused due to the presence of both BCM RoCE and Intel Gaudi in the ``input/software_config.json`` file. This configuration likely leads to a conflict, preventing the hb_devices from being properly recognized, while devices like ibp155s0 are displayed instead.

**Resolution**: To resolve this issue, perform the following steps:

1. Execute the ``oim_cleanup.yml`` with ``skip-tags local_repo`` to reset the local repository configurations.

2. Edit the ``input/software_config.json`` file and remove BCM RoCE.

3. Reprovision the Intel Gaudi node using the ``provision.yml`` playbook.

4. Finally, navigate to the ``/sys/class/infiniband`` directory and you should see the Intel Gaudi Infiniband device files.