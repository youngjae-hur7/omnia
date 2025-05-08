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
Unit tests for data_validation.py module
"""
import unittest
import os
import sys
from unittest.mock import MagicMock, patch, mock_open

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import data_validation  # pylint: disable=import-error,wrong-import-position


class TestDataValidation(unittest.TestCase):
    """Tests for the data validation module."""

    @patch('data_validation.get.input_data')
    def test_schema_success(self, mock_input_data):
        """Tests for the data validation schema module."""
        mock_input_data.return_value = ({'key': 'value'}, '.json')
        with patch('builtins.open', mock_open(read_data='{}')), patch('json.load', return_value={}):
            result = data_validation.schema(
                'input.json',
                'schema.json',
                set(),
                '/base/dir',
                'project',
                MagicMock(),
                MagicMock())
            self.assertTrue(result)

    @patch('data_validation.get.input_data')
    def test_schema_failure(self, mock_input_data):
        """Tests for the data validation schema module."""
        mock_input_data.return_value = (None, '.yaml')  # simulate YAML syntax error
        result = data_validation.schema(
            'input.yaml',
            'schema.yaml',
            set(),
            '/base/dir',
            'project',
            MagicMock(),
            MagicMock())
        self.assertFalse(result)

    @patch('data_validation.get.input_data')
    @patch('data_validation.logical_validation.validate_input_logic')
    def test_logic_success(self, mock_validate_logic, mock_input_data):
        """Tests for the data validation logic module."""
        mock_input_data.return_value = ({'key': 'value'}, '.json')
        mock_validate_logic.return_value = []  # No errors
        result = data_validation.logic(
            'input.json',
            MagicMock(),
            MagicMock(),
            '/base/dir',
            MagicMock(),
            'project')
        self.assertTrue(result)

    @patch('data_validation.get.input_data')
    @patch('data_validation.logical_validation.validate_input_logic')
    def test_logic_failure(self, mock_validate_logic, mock_input_data):
        """Tests for the data validation logic module."""
        mock_input_data.return_value = ({'key': 'value'}, '.json')
        mock_validate_logic.return_value = [
            {'error_msg': 'error', 'error_key': 'key', 'error_value': 'val'}]
        result = data_validation.logic(
            'input.json',
            MagicMock(),
            MagicMock(),
            '/base/dir',
            MagicMock(),
            'project')
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
