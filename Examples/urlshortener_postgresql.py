import psycopg2 # pip install psycopg2
import random
import string


# CREATE TABLE urls (
#     id SERIAL PRIMARY KEY,
#     short_url CHAR(7) UNIQUE NOT NULL,
#     used BOOLEAN DEFAULT FALSE
# );


# Database connection details
DB_CONFIG = {
    "dbname": "mydb",
    "user": "admin",
    "password": "password",
    "host": "localhost",
    "port": 5432
}


def connect_to_db():
    """Establish connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None


def create_url_entry(conn, short_url, used=False):
    """Create a new URL entry."""
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO urls (short_url, used)
                VALUES (%s, %s)
                RETURNING id;
            """
            cur.execute(query, (short_url, used))
            conn.commit()
            return cur.fetchone()[0]  # Return the new record's ID
    except Exception as e:
        conn.rollback()
        print("Error creating URL entry:", e)


def read_url_entry(conn, short_url):
    """Read a URL entry based on the short_url."""
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM urls WHERE short_url = %s;"
            cur.execute(query, (short_url,))
            return cur.fetchone()  # Return the record
    except Exception as e:
        print("Error reading URL entry:", e)


def update_url_entry(conn, short_url, used):
    """Update the 'used' status of a URL entry."""
    try:
        with conn.cursor() as cur:
            query = """
                UPDATE urls
                SET used = %s
                WHERE short_url = %s
                RETURNING id;
            """
            cur.execute(query, (used, short_url))
            conn.commit()
            return cur.rowcount  # Number of rows updated
    except Exception as e:
        conn.rollback()
        print("Error updating URL entry:", e)


def delete_url_entry(conn, short_url):
    """Delete a URL entry."""
    try:
        with conn.cursor() as cur:
            query = "DELETE FROM urls WHERE short_url = %s RETURNING id;"
            cur.execute(query, (short_url,))
            conn.commit()
            return cur.rowcount  # Number of rows deleted
    except Exception as e:
        conn.rollback()
        print("Error deleting URL entry:", e)


def generate_random_url():
    """Generate a random 7-character alphanumeric URL."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=7))


def generate_all_possible_keys(num_of_keys):
    for x in range(num_of_keys):
        short_url = generate_random_url()
        print("Generated URL:", short_url)

        # Create operation
        id = create_url_entry(conn, short_url)
        print("Created URL entry with ID:", id)

        # Read operation
        url_entry = read_url_entry(conn, short_url)
        print("Read URL entry:", url_entry)


def create_urls_table(conn):
    """Create the urls table if it doesn't exist."""
    try:
        with conn.cursor() as cur:
            query = """
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    short_url CHAR(7) UNIQUE NOT NULL, 
                    used BOOLEAN DEFAULT FALSE
                );
            """
            cur.execute(query)
            conn.commit()
            print("URLs table created successfully")
    except Exception as e:
        conn.rollback()
        print("Error creating URLs table:", e)

def get_unused_short_url(conn):
    """Get an unused short URL from the database."""
    try:
        with conn.cursor() as cur:
            query = "SELECT short_url FROM urls WHERE used = FALSE LIMIT 1;"
            cur.execute(query)
            result = cur.fetchone()
            if result:
                return result[0].strip()  # Remove padding from CHAR(7)
            return None
    except Exception as e:
        print("Error getting unused short URL:", e)
        return None

def mark_url_used(conn, short_url):
    """Mark a short URL as used."""
    try:
        with conn.cursor() as cur:
            query = "UPDATE urls SET used = TRUE WHERE short_url = %s;"
            cur.execute(query, (short_url,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print("Error marking URL as used:", e)
        return False

# Example usage
if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        
        # create_urls_table(conn)
        # generate_all_possible_keys(100)
        
        # Create a random URL
        # short_url = generate_random_url()
        # print("Generated URL:", short_url)

        # # Create operation
        # id = create_url_entry(conn, short_url)
        # print("Created URL entry with ID:", id)

        # # Read operation
        # url_entry = read_url_entry(conn, short_url)
        # print("Read URL entry:", url_entry)

        # # Update operation
        # rows_updated = update_url_entry(conn, short_url, used=True)
        # print(f"Updated {rows_updated} row(s).")

        # # Delete operation
        # rows_deleted = delete_url_entry(conn, short_url)
        # print(f"Deleted {rows_deleted} row(s).")

        # Close connection
        conn.close()