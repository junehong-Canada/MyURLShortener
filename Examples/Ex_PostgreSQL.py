import psycopg2                 # pip install psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    "dbname": "test_db",        # Replace with your database name
    "user": "admin",        # Replace with your username
    "password": "root",    # Replace with your password
    "host": "localhost",       # Replace with your host
    "port": "5432",            # Replace with your port
}

# Connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Database connection successful.")
        return conn
    except psycopg2.Error as e:
        print("Error connecting to database:", e)
        return None

# Create table
def create_table():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        age INT NOT NULL,
                        city VARCHAR(50)
                    );
                """)
                conn.commit()
                print("Table created successfully.")
        except psycopg2.Error as e:
            print("Error creating table:", e)
        finally:
            conn.close()

# 1. CREATE: Insert data into the table
def create_record(name, age, city):
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_table (name, age, city) VALUES (%s, %s, %s);",
                    (name, age, city)
                )
                conn.commit()
                print("Record inserted successfully.")
        except psycopg2.Error as e:
            print("Error inserting record:", e)
        finally:
            conn.close()

# 2. READ: Query data from the table
def read_records():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM test_table;")
                rows = cur.fetchall()
                print("Records:")
                for row in rows:
                    print(row)
        except psycopg2.Error as e:
            print("Error reading records:", e)
        finally:
            conn.close()

# 3. UPDATE: Modify existing data in the table
def update_record(record_id, new_age):
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE test_table SET age = %s WHERE id = %s;",
                    (new_age, record_id)
                )
                conn.commit()
                print("Record updated successfully.")
        except psycopg2.Error as e:
            print("Error updating record:", e)
        finally:
            conn.close()

# 4. DELETE: Remove data from the table
def delete_record(record_id):
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM test_table WHERE id = %s;", (record_id,))
                conn.commit()
                print("Record deleted successfully.")
        except psycopg2.Error as e:
            print("Error deleting record:", e)
        finally:
            conn.close()

# Main function to demonstrate CRUD operations
if __name__ == "__main__":
    create_table()          # Ensure the table exists
    create_record("Alice", 25, "New York")  # Insert record
    create_record("Bob", 30, "Los Angeles")
    read_records()          # Read all records
    update_record(1, 26)    # Update record with ID 1
    read_records()          # Read updated records
    delete_record(1)        # Delete record with ID 1
    read_records()          # Verify deletion