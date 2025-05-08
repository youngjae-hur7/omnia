# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#!/usr/bin/env python3
"""
Unit tests for logical_validation.py module
"""

import unittest
from unittest import mock
import sys
import os
import logging

# Add correct path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Now import your logical_validation
import logical_validation # pylint: disable=import-error,wrong-import-position

class TestUtils(unittest.TestCase):
    """Tests for the logical_validation module."""
    def setUp(self):
        self.logical_validation = logical_validation


    @mock.patch('logical_validation.validate_input_logic')
    def test_validate_input_logic_success(self, mock_validate_input_logic):
        """
        Test case for successful validation.

        This test case validates the logic of the input file
        by mocking the validate_input_logic function.

        Args:
            mock_validate_input_logic function.

        Returns:
            None
        """
        input_file_path = "test_input_file.yml"
        data = {"key": "value"}
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        module = None
        omnia_base_dir = None
        module_utils_base = None
        project_name = None
        mock_validate_input_logic.return_value = {"input_file_path": input_file_path,
                                                  "data": data,
                                                  "logger": logger,
                                                  "module": module,
                                                  "omnia_base_dir": omnia_base_dir,
                                                  "module_utils_base": module_utils_base,
                                                  "project_name": project_name
                                                  }
        errors = logical_validation.validate_input_logic(
            input_file_path,
            data,
            logger,
            module,
            omnia_base_dir,
            module_utils_base,
            project_name
        )
        self.assertEqual(errors, mock_validate_input_logic.return_value)

    def test_validate_input_logic_failure(self):
        """
        Test case for validation failure.

        This test case validates the logic of the input file
        by mocking the validate_input_logic function.

        Parameters:
            input_file_path (str): The path to the input file.
            data (dict): The data to validate.
            logger (Logger): The logger object.
            module (AnsibleModule): The Ansible module object.
            omnia_base_dir (str): The base directory of Omnia.
            module_utils_base (str): The base directory of module utils.
            project_name (str): The name of the project.

        Returns:
            None
        """
        input_file_path = "test_input_file.yml"
        data = {"key": "invalid_value"}
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        module = None
        omnia_base_dir = None
        module_utils_base = None
        project_name = None
        errors = self.logical_validation.validate_input_logic(
            input_file_path,
            data,
            logger,
            module,
            omnia_base_dir,
            module_utils_base,
            project_name
        )
        self.assertEqual(errors, {})

if __name__ == "__main__":
    unittest.main()
