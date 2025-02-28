#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.process_parallel import execute_parallel, log_table_output
from ansible.module_utils.download_common import (
    process_manifest,
    process_tarball,
    process_git,
    process_shell,
    process_ansible_galaxy_collection,
    process_iso,
    process_pip
)
from ansible.module_utils.download_image import process_image
from ansible.module_utils.download_rpm import process_rpm
from ansible.module_utils.standard_logger import setup_standard_logger
from prettytable import PrettyTable
from datetime import datetime
import logging
import os
import re
import time
import json

from ansible.module_utils.software_utils import (
    get_software_names,
    check_csv_existence,
    get_failed_software,
    process_software,
    load_json,
    load_yaml,
    get_json_file_path,
    get_csv_file_path,
    transform_package_dict,
    parse_repo_urls,
    set_version_variables,
    get_subgroup_dict
)

from ansible.module_utils.config import (
    DEFAULT_NTHREADS,
    DEFAULT_TIMEOUT,
    LOG_DIR_DEFAULT,
    DEFAULT_LOG_FILE,
    DEFAULT_SLOG_FILE,
    CSV_FILE_PATH_DEFAULT,
    DEFAULT_REPO_STORE_PATH,
    USER_JSON_FILE_DEFAULT,
    DEFAULT_STATUS_FILENAME,
    SOFTWARE_CSV_FILENAME,
    SOFTWARE_CSV_HEADER,
    STATUS_CSV_HEADER
)


def update_status_csv(csv_dir, software, overall_status):
    """
    Update the status CSV file with the status for given software.
    
    If the software already exists, update its status.
    If 'software' is a list, update each software with the same overall_status.
    """
    parent_dir = os.path.dirname(csv_dir)
    status_file = os.path.join(parent_dir, SOFTWARE_CSV_FILENAME)
    #header = "name,status"
    header = SOFTWARE_CSV_HEADER

    # Create the file with header if it does not exist.
    if not os.path.exists(status_file):
        with open(status_file, "w", encoding="utf-8") as f:
            f.write(header + "\n")

    # Read the existing file content.
    with open(status_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Ensure there is a header.
    if not lines or lines[0] != header:
        lines.insert(0, header)

    # Build a dictionary for existing entries (skip header).
    status_dict = {}
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) >= 2:
            key = parts[0].strip()
            value = parts[1].strip()
            status_dict[key] = value

    # Transform the new status.
    transformed_status = re.sub(r'failure', 'failed', overall_status.lower())

    # Update or add the entry for each given software.
    if isinstance(software, list):
        for sw in software:
            status_dict[sw] = transformed_status
    else:
        status_dict[software] = transformed_status

    # Recreate the CSV content.
    final_lines = [header]
    for key, value in status_dict.items():
        final_lines.append(f"{key},{value}")

    # Write the updated content back to the file.
    with open(status_file, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))


def determine_function(task, repo_store_path, csv_file_path, user_data, version_variables):
    """
    Determines the appropriate function and its arguments to process a given task.
    """
    try:
        # Ensure the CSV directory exists.
        os.makedirs(csv_file_path, exist_ok=True)
        cluster_os_type = user_data['cluster_os_type']
        cluster_os_version = user_data['cluster_os_version']

        # Construct the status file path using DEFAULT_STATUS_FILENAME.
        status_file = os.path.join(csv_file_path, DEFAULT_STATUS_FILENAME)
        if not os.path.exists(status_file) or os.stat(status_file).st_size == 0:
            with open(status_file, 'w', encoding="utf-8") as file:
                file.write(STATUS_CSV_HEADER)

        task_type = task.get("type")
        if task_type == "manifest":
            return process_manifest, [task, repo_store_path, status_file]
        elif task_type == "git":
            return process_git, [task, repo_store_path, status_file]
        elif task_type == "tarball":
            return process_tarball, [task, repo_store_path, status_file, version_variables]
        elif task_type == "shell":
            return process_shell, [task, repo_store_path, status_file]
        elif task_type == "ansible_galaxy_collection":
            return process_ansible_galaxy_collection, [task, repo_store_path, status_file]
        elif task_type == "iso":
            return process_iso, [task, repo_store_path, status_file,
                                 cluster_os_type, cluster_os_version, version_variables]
        elif task_type == "pip_module":
            return process_pip, [task, repo_store_path, status_file]
        elif task_type == "image":
            return process_image, [task, repo_store_path, status_file,
                                   cluster_os_type, cluster_os_version, version_variables]
        elif task_type == "rpm":
            return process_rpm, [task, repo_store_path, status_file,
                                 cluster_os_type, cluster_os_version]
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    except Exception as e:
        raise RuntimeError(f"Failed to determine function for task: {str(e)}")


def generate_pretty_table(task_results, total_duration, overall_status):
    """
    Generates a pretty table with the task results, total duration, and overall status.
    """
    table = PrettyTable(["Task", "Status", "LogFile"])
    for result in task_results:
        table.add_row([result["package"], result["status"], result["logname"]])
    table.add_row(["Total Duration", total_duration, ""])
    table.add_row(["Overall Status", overall_status, ""])
    return table.get_string()


def main():
    """
    Executes a list of tasks in parallel using multiple worker processes.
    """
    module_args = dict(
        tasks=dict(type="list", required=True),
        nthreads=dict(type="int", required=False, default=DEFAULT_NTHREADS),
        timeout=dict(type="int", required=False, default=DEFAULT_TIMEOUT),
        log_dir=dict(type="str", required=False, default=LOG_DIR_DEFAULT),
        log_file=dict(type="str", required=False, default=DEFAULT_LOG_FILE),
        slog_file=dict(type="str", required=False, default=DEFAULT_SLOG_FILE),
        csv_file_path=dict(type="str", required=False, default=CSV_FILE_PATH_DEFAULT),
        repo_store_path=dict(type="str", required=False, default=DEFAULT_REPO_STORE_PATH),
        software=dict(type="list", elements="str", required=True),
        user_json_file=dict(type="str", required=False, default=USER_JSON_FILE_DEFAULT)
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    tasks = module.params["tasks"]
    nthreads = module.params["nthreads"]
    log_dir = module.params["log_dir"]
    log_file = module.params["log_file"]
    slog_file = module.params["slog_file"]
    timeout = module.params["timeout"]
    csv_file_path = module.params["csv_file_path"]
    repo_store_path = module.params["repo_store_path"]
    software = module.params["software"]
    user_json_file = module.params["user_json_file"]

    # Initialize standard logger.
    slogger = setup_standard_logger(slog_file)
    result = dict(changed=False, task_results=[])

    # Record start time.
    start_time = datetime.now()
    formatted_start_time = start_time.strftime("%I:%M:%S %p")
    slogger.info(f"Start execution time: {formatted_start_time}")
    slogger.info(f"Task list: {tasks}")
    slogger.info(f"Number of threads: {nthreads}")
    slogger.info(f"Timeout: {timeout}")

    try:
        user_data = load_json(user_json_file)
        cluster_os_type = user_data['cluster_os_type']
        cluster_os_version = user_data['cluster_os_version']

        subgroup_dict, software_names = get_subgroup_dict(user_data)
        version_variables = set_version_variables(user_data, software_names, cluster_os_version)
        slogger.info(f"Cluster OS: {cluster_os_type}")
        first_entry_dict = dict([list(version_variables.items())[0]])

        overall_status, task_results = execute_parallel(
            tasks, determine_function, nthreads, repo_store_path, csv_file_path,
            log_dir, user_data, first_entry_dict, slogger, timeout
        )

        end_time = datetime.now()
        formatted_end_time = end_time.strftime("%I:%M:%S %p")
        total_seconds = (end_time - start_time).total_seconds()
        minutes, seconds = divmod(int(total_seconds), 60)
        total_duration = f"{minutes} min {seconds} sec" if minutes > 0 else f"{seconds} sec"

        slogger.info(f"End execution time: {formatted_end_time}")
        slogger.info(f"Total execution time: {total_duration}")
        slogger.info(f"Task results: {task_results}")

        table_output = generate_pretty_table(task_results, total_duration, overall_status)
        log_table_output(table_output, log_file)
        result["total_duration"] = total_duration
        result["task_results"] = task_results
        result["table_output"] = table_output

        update_status_csv(csv_file_path, software, overall_status)

        if overall_status == "SUCCESS":
            result["overall_status"] = "SUCCESS"
            result["changed"] = True
            slogger.info(f"Result: {result}")
            module.exit_json(**result)
        elif overall_status == "PARTIAL":
            result["overall_status"] = "PARTIAL"
            module.exit_json(msg="Some tasks partially failed", **result)
        else:
            result["overall_status"] = "FAILURE"
            module.exit_json(msg="Some tasks failed", **result)

    except Exception as e:
        result["table_output"] = table_output if "table_output" in locals() else "No table generated."
        slogger.error(f"Execution failed: {str(e)}")
        module.fail_json(msg=f"Error during execution: {str(e)}", **result)


if __name__ == "__main__":
    main()

