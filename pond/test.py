import psycopg2

# PostgreSQL Connection Details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "127.0.0.1",  # Try this instead of "localhost"
    "port": 5432
}


def test_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Run this before your main application
if test_connection():
    print("Database connection verified, proceeding with application...")
else:
    print("Failed to connect to database, please check configuration")