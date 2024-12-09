from cassandra.cluster import Cluster   # pip install cassandra-driver
from cassandra.auth import PlainTextAuthProvider

#
# cassandra.DependencyException: Unable to load a default connection class
#

# Connect to Cassandra
def connect_to_cassandra():
    cluster = Cluster(['127.0.0.1'])  # Replace with your Cassandra node IP
    session = cluster.connect()
    session.set_keyspace('test_keyspace')  # Replace with your keyspace
    return session

# Create a Keyspace and Table
def setup_database(session):
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS test_keyspace 
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    
    session.set_keyspace('test_keyspace')
    
    session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY,
        name TEXT,
        email TEXT
    );
    """)

# Insert data into Cassandra (CREATE)
def insert_user(session, user_id, name, email):
    session.execute("""
    INSERT INTO users (id, name, email) VALUES (%s, %s, %s);
    """, (user_id, name, email))
    print(f"User {name} added.")

# Retrieve data from Cassandra (READ)
def get_users(session):
    rows = session.execute("SELECT * FROM users;")
    for row in rows:
        print(f"ID: {row.id}, Name: {row.name}, Email: {row.email}")

# Update data in Cassandra (UPDATE)
def update_user_email(session, user_id, new_email):
    session.execute("""
    UPDATE users SET email = %s WHERE id = %s;
    """, (new_email, user_id))
    print(f"User with ID {user_id} updated email to {new_email}.")

# Delete data from Cassandra (DELETE)
def delete_user(session, user_id):
    session.execute("""
    DELETE FROM users WHERE id = %s;
    """, (user_id,))
    print(f"User with ID {user_id} deleted.")

# Main Function to Demonstrate CRUD
if __name__ == "__main__":
    import uuid

    # Connect to Cassandra and set up the database
    session = connect_to_cassandra()
    setup_database(session)

    # Insert a new user
    user_id = uuid.uuid4()
    insert_user(session, user_id, "John Doe", "john.doe@example.com")

    # Read and display all users
    print("\nAll Users:")
    get_users(session)

    # Update the user's email
    update_user_email(session, user_id, "john.new@example.com")

    # Read and display all users again
    print("\nAll Users After Update:")
    get_users(session)

    # Delete the user
    delete_user(session, user_id)

    # Read and display all users after deletion
    print("\nAll Users After Deletion:")
    get_users(session)

    # Close the session
    session.cluster.shutdown()
    session.shutdown()