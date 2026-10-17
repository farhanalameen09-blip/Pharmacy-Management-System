import os
import tempfile
import unittest
import database


class TestPharmacyDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.original_db_path = database.DATABASE_PATH
        self.original_db_dir = database.DATABASE_DIR

        database.DATABASE_DIR = self.temp_dir.name
        database.DATABASE_PATH = os.path.join(
            self.temp_dir.name, "test_pharmacy.db"
        )

    def tearDown(self):
        database.DATABASE_PATH = self.original_db_path
        database.DATABASE_DIR = self.original_db_dir
        self.temp_dir.cleanup()

    def test_database_connection(self):
        with database.get_connection() as connection:
            result = connection.execute("SELECT 1").fetchone()

        self.assertEqual(result[0], 1)

    def test_tables_are_created(self):
        database.create_tables()

        with database.get_connection() as connection:
            result = connection.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = 'users'
            """).fetchone()

        self.assertIsNotNone(result)

    def test_tables_can_be_created_twice(self):
        database.create_tables()
        database.create_tables()

        with database.get_connection() as connection:
            result = connection.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = 'medicines'
            """).fetchone()

        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)