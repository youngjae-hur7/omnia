NVIDIA GPU Operator
=====================

Kubernetes provides access to special hardware resources such as NVIDIA GPUs, NICs, Infiniband adapters and other devices through the device plugin framework.
However, configuring and managing nodes with these hardware resources requires configuration of multiple software components such as drivers, container runtimes or other libraries which are difficult and prone to errors.
The NVIDIA GPU Operator uses the operator framework within Kubernetes to automate the management of all NVIDIA software components needed to provision GPU.
These components include the NVIDIA drivers (to enable CUDA), Kubernetes device plugin for GPUs, the NVIDIA Container Toolkit, automatic node labelling using GFD, DCGM based monitoring and others. To know more, `click here <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html>`_.

Prerequisite
---------------

Ensure that the ``input/software_config.json`` file contains the following line under ``softwares``: ::

    {"name": "nvidia_gpu_operator", "version":"24.9.2"}

A sample version of the ``input/software_config.json`` is located `here <../../../samplefiles.html>`_.

.. note:: Currently, Omnia only supports the ``24.9.2`` version of the NVIDIA GPU operator.

Configurations
----------------

Omnia installs the NVIDIA GPU operator as part of ``omnia.yml`` or ``scheduler.yml`` playbook execution, based on if the ``input/omnia_config.yml`` file contains the required inputs.
Follow the below provided steps to set up the NVIDIA GPU operator for your cluster:

1. For the NVIDIA GPU operator to be installed, you must have a ``nvidia_gpu_operator_config_value.yml`` file that contains all the required details. An pre-filled example of this can be found in the ``omnia/examples/`` folder.

2. You can either edit the ``nvidia_gpu_operator_config_value.yml`` file present in the ``omnia/examples`` folder or create a new one with the same name and save it to the Omnia shared directory. Provide inputs to the following mandatory parameters in that file:

        * ``http_proxy``: This value can be found in the ``/opt/omnia/offline/local_repo_access.yml`` file.
        * ``https_proxy``: This value can be found in the ``/opt/omnia/offline/local_repo_access.yml`` file.

.. note:: All other parameters in the ``examples/nvidia_gpu_operator_config_value.yml`` comes pre-filled for a basic configuration, but can be edited for a more customised installation.

3. Once the ``nvidia_gpu_operator_config_value.yml`` file is ready, provide the filepath of it to the ``nvidia_gpu_operator_value_file_path`` parameter in ``input/omnia_config.yml`` file.

Playbook execution
--------------------

Once the above mentioned configurations are done, execute the ``omnia.yml`` or ``scheduler.yml`` playbook to install the NVIDIA GPU operator:

    ::

        cd omnia
        ansible-playbook omnia.yml

    ::

        cd scheduler
        ansible-playbook scheduler.yml