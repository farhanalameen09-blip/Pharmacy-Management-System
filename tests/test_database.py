import os
import tempfile
import unittest
import database


class TestPharmacyDatabase(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()

        # Save the original database configuration
        self.original_db_path = database.DATABASE_PATH
        self.original_db_dir = database.DATABASE_DIR

        # Use a separate temporary database for every test
        database.DATABASE_DIR = self.temp_dir.name
        database.DATABASE_PATH = os.path.join(
            self.temp_dir.name,
            "test_pharmacy.db"
        )

    def tearDown(self):
        # Restore the original database configuration
        database.DATABASE_PATH = self.original_db_path
        database.DATABASE_DIR = self.original_db_dir

        # Remove the temporary database
        self.temp_dir.cleanup()

    def test_database_connection(self):
        """Test that the database connection works."""
        with database.get_connection() as connection:
            result = connection.execute("SELECT 1").fetchone()

        self.assertEqual(result[0], 1)

    def test_tables_are_created(self):
        """Test that the users table is created."""
        database.create_tables()

        with database.get_connection() as connection:
            result = connection.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name = 'users'
            """).fetchone()

        self.assertIsNotNone(result)

    def test_tables_can_be_created_twice(self):
        """Test that creating tables twice does not cause an error."""
        database.create_tables()
        database.create_tables()

        with database.get_connection() as connection:
            result = connection.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name = 'medicines'
            """).fetchone()

        self.assertIsNotNone(result)

    def test_default_admin_is_created_once(self):
        """Test that running admin setup twice creates only one admin."""
        database.create_tables()

        database.create_default_admin()
        database.create_default_admin()

        with database.get_connection() as connection:
            users = connection.execute(
                "SELECT username FROM users WHERE username = ?",
                ("admin",)
            ).fetchall()

        self.assertEqual(len(users), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)