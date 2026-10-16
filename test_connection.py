from database import get_connection

def test_database():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
        print("Database connection successful!")
    except Exception as error:
        print("Database connection failed:", error)

if __name__ == "__main__":
    test_database()