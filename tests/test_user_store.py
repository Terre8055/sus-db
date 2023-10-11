"""Test cases for UserDBManager"""
import unittest
import os
from src.user_db_manager import UserDBManager


class TestUserDBManager(unittest.TestCase):
    """Test cases for UserDBManager"""

    @classmethod
    def setUpClass(cls):
        cls.db_manager = UserDBManager()

    def test_initialize_db(self):
        """Test to check if db is initialised"""
        self.db_manager.initialize_db()
        self.assertTrue(os.path.exists(self.db_manager.get_file_path))

    def test_hash_user_string(self):
        """Test hashed strings with argon2"""
        hashed_string = self.db_manager.hash_user_string("password")
        self.assertIsInstance(hashed_string, str)
        self.assertTrue(len(hashed_string) > 0)

    def test_serialize_data(self):
        """Test to return serialised data and check data type"""
        serialized_data = self.db_manager.serialize_data({"request_string": "data"})
        self.assertIsInstance(serialized_data, str)
        self.assertTrue(len(serialized_data) > 0)
        

    def test_storage_return(self):
        """Test toreturn case of store method"""
        req = {'request_string': 'mike12345678iuiujfkk'}
        x = self.db_manager.store_user_string(req)
        self.assertIsInstance(x, dict)
        self.assertIsNotNone(x.get('id'))
        
    def test_display_db(self):
        """Test to verify data in the store"""
        req = {'request_string': 'mike12345678iuiujfghf'}
        self.db_manager.store_user_string(req)
        self.assertIsNotNone(self.db_manager.display_user_db())
        self.assertIsInstance(self.db_manager.display_user_db(), dict)
        self.assertTrue(len(self.db_manager.display_user_db()) == 4)
        for key in self.db_manager.display_user_db():
            if key == '_id':
                self.assertIsNotNone(self.db_manager.display_user_db[key])
            elif key == 'secured_user_string':
                self.assertTrue(len(self.db_manager.display_user_db[key]) == 12)

        