import unittest
import os
from unittest.mock import patch, MagicMock
from src.user_db_manager import UserDBManager
from typing import Dict
import base64

class TestUserDBManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = UserDBManager()

    def tearDown(self):
        # Clean up any files created during tests
        pass

    def test_initialize_db(self):
        # Ensure the database is initialized correctly
        self.db_manager.initialize_db()
        # Assert if the file exists
        self.assertTrue(os.path.exists(self.db_manager.get_file_path))

    @patch('src.user_db_manager.dbm.open')
    @patch('src.user_db_manager.base64.urlsafe_b64encode')
    def test_store_user_string(self, mock_urlsafe_b64encode, mock_dbm_open):
        # Prepare request data
        request_data: Dict[str, str] = {'request_string': 'test_user_string'}
        # Mock the dbm.open function
        mock_dbm_open.return_value.__enter__.return_value = {
            'hash_string': 'mocked_hash_string'
        }
        # Mock urlsafe_b64encode
        mock_urlsafe_b64encode.return_value = b'mocked_secure_user_string'
        # Store user string
        self.db_manager.store_user_string(request_data)
        # Retrieve the stored data
        stored_data = self.db_manager.deserialize_data(self.db_manager.display_user_db()['hash_string'])
        # Check if stored data matches the input
        self.assertEqual(stored_data['request_string'], request_data['request_string'])

    @patch('src.user_db_manager.dbm.open')
    @patch('src.user_db_manager.base64.urlsafe_b64encode')
    def test_verify_user(self, mock_urlsafe_b64encode, mock_dbm_open):
        # Prepare request data
        request_data: Dict[str, str] = {'request_string': 'test_user_string'}
        # Store user string
        self.db_manager.store_user_string(request_data)
        # Mock the dbm.open function
        mock_dbm_open.return_value.__enter__.return_value = {
            'hash_string': 'mocked_hash_string'
        }
        # Mock urlsafe_b64encode
        mock_urlsafe_b64encode.return_value = b'mocked_secure_user_string'
        # Verify the user string
        result = self.db_manager.verify_user({'uid': self.db_manager.pk})
        # Check if verification is successful
        self.assertEqual(result, f"User authenticated successfully for UID: {self.db_manager.pk}")

    # Add more test cases as needed

if __name__ == '__main__':
    unittest.main()
