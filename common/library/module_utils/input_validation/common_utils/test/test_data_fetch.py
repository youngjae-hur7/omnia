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
Unit tests for data_fetch.py module
"""
import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import data_fetch  # pylint: disable=import-error,wrong-import-position

class TestDataFetch(unittest.TestCase):
    """Tests for the data fetch module."""

    def setUp(self):
        self.data_fetch = data_fetch

    def tearDown(self):
        pass

    def test_files_recursively(self):
        """Tests for the data_fetch files_recursively module."""
        with patch("data_fetch.glob.iglob") as mock_iglob, \
             patch("data_fetch.os.path.isfile") as mock_isfile:

            mock_iglob.return_value = ["/path/file1.json", "/path/file2.json"]
            mock_isfile.side_effect = lambda x: True

            result = self.data_fetch.files_recursively("/path", "*.json")
            expected = [os.path.abspath("/path/file1.json"), os.path.abspath("/path/file2.json")]

            self.assertEqual(result, expected)

    def test_file_name_from_path(self):
        """Tests for the data_fetch file_name_from_path module."""
        path = "/some/random/path/to/file.txt"
        result = self.data_fetch.file_name_from_path(path)
        self.assertEqual(result, "file.txt")

    def test_json_line_number_found(self):
        """Tests for the data_fetch json_line_number module."""
        file_content = '{"key": "value"}\n'
        module = MagicMock()

        with patch("builtins.open", unittest.mock.mock_open(read_data=file_content)):
            line, is_line_num = self.data_fetch.json_line_number("fake_path.json", "key", module)
            self.assertEqual(line, 1)
            self.assertTrue(is_line_num)

    def test_json_line_number_not_found(self):
        """Tests for the data_fetch json_line_number module."""
        file_content = '{"other_key": "value"}\n'
        module = MagicMock()

        with patch("builtins.open", unittest.mock.mock_open(read_data=file_content)):
            result = self.data_fetch.json_line_number("fake_path.json", "key", module)
            self.assertEqual(result, (1, True))

    def test_yml_line_number_found(self):
        """Tests for the data_fetch yml_line_number module."""
        file_content = "key: value\n"
        omnia_base_dir = "/tmp"
        project_name = "test_project"

        with patch("builtins.open", unittest.mock.mock_open(read_data=file_content)), \
             patch("data_fetch.validation_utils.is_file_encrypted", return_value=False):
            line, is_line_num = self.data_fetch.yml_line_number(
                "fake_file.yaml", "key", omnia_base_dir, project_name)
            self.assertEqual(line, 1)
            self.assertTrue(is_line_num)

    def test_yml_line_number_not_found(self):
        """Tests for the data_fetch yml_line_number module."""
        file_content = "another_key: value\n"
        omnia_base_dir = "/tmp"
        project_name = "test_project"

        with patch("builtins.open", unittest.mock.mock_open(read_data=file_content)), \
             patch("data_fetch.validation_utils.is_file_encrypted", return_value=False):
            result = self.data_fetch.yml_line_number(
                "fake_file.yaml", "key", omnia_base_dir, project_name)
            self.assertEqual(result, (1, True))

    def test_input_data_json(self):
        """Tests for the data_fetch input_data module."""
        data = {"key": "value"}
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(data))):
            result, ext = self.data_fetch.input_data(
                "test.json", "/tmp", "test_project", None, None)
            self.assertEqual(result, data)
            self.assertEqual(ext, ".json")

    def test_input_data_unsupported_extension(self):
        """Tests for the data_fetch input_data module."""
        logger = MagicMock()
        module = MagicMock()

        with self.assertRaises(ValueError):
            self.data_fetch.input_data("test.unsupported", "/tmp", "test_project", logger, module)

if __name__ == "__main__":
    unittest.main()
