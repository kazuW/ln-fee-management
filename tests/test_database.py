import sqlite3
import unittest
from src.db.database import Database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database('lightning_node.db')
        cls.db.create_tables()

    def test_insert_channel(self):
        channel_data = {
            'channel_name': 'Test Channel',
            'channel_id': 'test_channel_1',
            'capacity': 1000000
        }
        self.db.insert_channel(channel_data)
        channel = self.db.get_channel('test_channel_1')
        self.assertEqual(channel['channel_name'], 'Test Channel')
        self.assertEqual(channel['capacity'], 1000000)

    def test_insert_channel_data(self):
        channel_data = {
            'channel_id': 'test_channel_1',
            'date': '2023-10-01',
            'local_balance': 500000,
            'local_fee': 100,
            'remote_balance': 500000,
            'amboss_fee': 50,
            'active': 1
        }
        self.db.insert_channel_data(channel_data)
        data = self.db.get_channel_data('test_channel_1', '2023-10-01')
        self.assertEqual(data['local_balance'], 500000)
        self.assertEqual(data['local_fee'], 100)

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_tables()
        cls.db.close()

if __name__ == '__main__':
    unittest.main()