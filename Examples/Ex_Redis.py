import redis    # pip install redis
# docker run --name my-redis -p 6379:6379 --restart always --detach redis

# Connect to Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        if r.ping():
            print("Connected to Redis successfully.")
        return r
    except redis.ConnectionError as e:
        print("Error connecting to Redis:", e)
        return None

# 1. CREATE: Add a new key-value pair
def create_record(redis_client, key, value):
    try:
        redis_client.set(key, value)
        print(f"Record created: {key} -> {value}")
    except Exception as e:
        print("Error creating record:", e)

# 2. READ: Retrieve a value by key
def read_record(redis_client, key):
    try:
        value = redis_client.get(key)
        if value:
            print(f"Record read: {key} -> {value}")
        else:
            print(f"Record with key '{key}' not found.")
    except Exception as e:
        print("Error reading record:", e)

# 3. UPDATE: Modify an existing key-value pair
def update_record(redis_client, key, new_value):
    try:
        if redis_client.exists(key):
            redis_client.set(key, new_value)
            print(f"Record updated: {key} -> {new_value}")
        else:
            print(f"Record with key '{key}' does not exist.")
    except Exception as e:
        print("Error updating record:", e)

# 4. DELETE: Remove a key-value pair
def delete_record(redis_client, key):
    try:
        if redis_client.delete(key):
            print(f"Record deleted: {key}")
        else:
            print(f"Record with key '{key}' does not exist.")
    except Exception as e:
        print("Error deleting record:", e)

# Main function to demonstrate CRUD operations
if __name__ == "__main__":
    redis_client = connect_redis()
    if redis_client:
        # Create records
        create_record(redis_client, "name", "Alice")
        create_record(redis_client, "age", "25")
        create_record(redis_client, "city", "New York")
        
        # Read records
        read_record(redis_client, "name")
        read_record(redis_client, "age")
        read_record(redis_client, "city")
        read_record(redis_client, "nonexistent_key")  # Demonstrate missing key
        
        # Update records
        update_record(redis_client, "age", "26")
        update_record(redis_client, "country", "USA")  # Demonstrate missing key
        
        # Delete records
        delete_record(redis_client, "city")
        delete_record(redis_client, "nonexistent_key")  # Demonstrate missing key
        
        # Final read to check updates
        read_record(redis_client, "age")
        read_record(redis_client, "city")