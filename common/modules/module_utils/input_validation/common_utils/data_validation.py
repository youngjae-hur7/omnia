    # Main L1 Validation code. Get the JSON schema and input file to validate

import json
import ansible.module_utils.input_validation.common_utils.data_fetch as get
from ansible.module_utils.input_validation.common_utils import en_us_validation_msg
import jsonschema
from ansible.module_utils.input_validation.common_utils import logical_validation


def schema(input_file_path, schema_file_path, passwords_set, omnia_base_dir, project_name, logger, module):
    """
    Validates the input file against a JSON schema.

    Args:
        input_file_path (str): The path to the input file.
        schema_file_path (str): The path to the schema file.

    Returns:
        bool: True if the validation is successful, False otherwise.
    """
    try:
        input_data, extension = get.input_data(input_file_path, omnia_base_dir, project_name, logger, module)

        # If input_data is None, it means there was a YAML syntax error
        if input_data is None:
            return False

        # Load schema
        schema = json.load(open(schema_file_path, "r"))
        logger.debug(en_us_validation_msg.get_validation_initiated(input_file_path))

        # Validate the input file with the schema and output the errors
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(input_data), key=lambda e: e.path)

        # if errors exist, then print an error with the line number
        if errors:
            for error in errors:
                error_path = ".".join(map(str, error.path))

                # Custom error messages for regex pattern failures
                if 'Groups' == error_path:
                    error.message = en_us_validation_msg.invalid_group_name_msg
                elif 'location_id' in error_path:
                    error.message = en_us_validation_msg.invalid_location_id_msg
                elif 'ports' in error_path:
                    error.message = en_us_validation_msg.invalid_switch_ports_msg
                # TODO: Add a syntax error message for roles
                # elif 'is not of type' in error.message:
                #     error.message = en_us_validation_msg.invalid_attributes_role_msg
                error_msg = f"Validation Error at {error_path}: {error.message}"

                # For passwords, mask the value so that no password values are logged
                if (error.path[-1] in passwords_set):
                    parts = error.message.split(' ', 1)
                    if parts:
                        parts[0] = f"'{'*' * (len(parts[0]) - 2)}'"
                    error_msg = f"Validation Error at {error_path}: {' '.join(parts)}"
                # For all other fields, just log the value
                logger.error(error_msg)

                # get the line number and log it
                line_number, is_line_num = None, False
                if "json" in extension:
                    line_number, is_line_num = get.json_line_number(input_file_path, error_path, module)
                elif "yml" in extension:
                    line_number, is_line_num = get.yml_line_number(input_file_path, error_path, omnia_base_dir, project_name)
                    logger.info(line_number, is_line_num)
                if line_number:
                    message = f"Error occurs on line {line_number}" if is_line_num else f"Error occurs on object or list entry on line {line_number}"
                    logger.error(message)
            logger.error(en_us_validation_msg.get_schema_failed(input_file_path))
            return False
        else:
            logger.info(en_us_validation_msg.get_schema_success(input_file_path))
            return True
    except jsonschema.exceptions.SchemaError as se:
        message = f"Internal schema validation error: {se.message}"
        logger.error(message)
    except ValueError as ve:
        message = f"Value error: {ve}"
        logger.error(message)
    except Exception as e:
        message = f"An unexpected error occurred: {e}"
        logger.error(message)

# Code to run the L2 validation validate_input_logic function.
def logic(input_file_path, logger, module, omnia_base_dir, module_utils_base, project_name):
    """
    Validates the logic of the input file.

    Args:
        input_file_path (str): The path to the input file.
        logger (logging.Logger): The logger object.
        module (AnsibleModule): The Ansible module.
        omnia_base_dir (str): The base directory of Omnia.
        project_name (str): The name of the project.

    Returns:
        bool: True if the logic validation is successful, False otherwise.

    Raises:
        ValueError: If a value error occurs.
        Exception: If an unexpected error occurs.
    """
    try:
        input_data, extension = get.input_data(input_file_path, omnia_base_dir, project_name, logger, module)

        # errors = [{error_msg: custom message, error_key: ex-node_name (to find line number), error_value: ex-6,"node" (to help find line #)}]
        errors = logical_validation.validate_input_logic(input_file_path, input_data, logger, module, omnia_base_dir, project_name)

        # Print errors, if the error value is None then send a separate message.
        # This is for values where it did not have a single key as the error
        if errors:
            for error in errors:
                error_key = error['error_key']
                error_value = error['error_value']
                error_msg = error['error_msg']

                # Log the error message based on the error value
                if error_value is None:
                    message = f"Validation Error at {error_key} {error_msg}"
                    logger.error(message)
                elif isinstance(error_value, str):
                    message = f"Validation Error at {error_key}: '{error_value}' {error_msg}"
                    logger.error(message)
                else:
                    message = f"Validation Error at {error_key}: {error_value} {error_msg}"
                    logger.error(message)

                # log the line number based off of the input config file extension
                if "json" in extension:
                    line_number, is_line_num = get.json_line_number(input_file_path, error_key, module)
                    if line_number:
                        message = f"Error occurs on line {line_number}" if is_line_num else f"Error occurs on object or list entry on line {line_number}"
                        logger.error(message)
                if "yml" in extension:
                    if error_value is None:
                        continue
                    line_number, is_line_num = get.yml_line_number(input_file_path, error_key, omnia_base_dir, project_name)
                    if line_number:
                        message = f"Error occurs on line {line_number}" if is_line_num else f"Error occurs on object or list entry on line {line_number}"
                        logger.error(message)

            logger.error(en_us_validation_msg.get_logic_failed(input_file_path))
            return False
        else:
            logger.info(en_us_validation_msg.get_logic_success(input_file_path))
            return True
    except ValueError as ve:
        message = f"Value error: {ve}"
        logger.error(message, exc_info=True)
        return False
    except Exception as e:
        message = f"An unexpected error occurred: {e}"
        logger.error(message, exc_info=True)
        return False

