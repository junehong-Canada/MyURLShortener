import boto3    # pip install boto3
from botocore.exceptions import ClientError

# Initialize the DynamoDB resource
print("Initialize the DynamoDB resource")
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000", region_name='us-east-1')  # Update with your region
print("Initialize the DynamoDB resource done...")
table_name = 'TestTable'  # Replace with your table name

# Ensure the table exists (for demonstration purposes)
def create_table():
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},  # String type
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            }
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            print(f"Unexpected error: {e}")

# 1. CREATE: Add an item to the table
def create_item():
    table = dynamodb.Table(table_name)
    try:
        table.put_item(
            Item={
                'id': '123',  # Primary key
                'name': 'Alice',
                'age': 25,
                'city': 'New York'
            }
        )
        print("Item created successfully.")
    except ClientError as e:
        print(f"Failed to create item: {e}")

# 2. READ: Retrieve items from the table
def read_items():
    table = dynamodb.Table(table_name)
    try:
        # Get a single item
        response = table.get_item(Key={'id': '123'})
        print("Single item:", response.get('Item'))
        
        # Scan the table for all items
        response = table.scan()
        print("All items:", response['Items'])
    except ClientError as e:
        print(f"Failed to read items: {e}")

# 3. UPDATE: Modify an existing item
def update_item():
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={'id': '123'},  # Primary key of the item to update
            UpdateExpression="SET age = :new_age",
            ExpressionAttributeValues={':new_age': 26},
            ReturnValues="UPDATED_NEW"
        )
        print("Updated item:", response)
    except ClientError as e:
        print(f"Failed to update item: {e}")

# 4. DELETE: Remove an item from the table
def delete_item():
    table = dynamodb.Table(table_name)
    try:
        response = table.delete_item(Key={'id': '123'})
        print("Item deleted successfully.")
    except ClientError as e:
        print(f"Failed to delete item: {e}")

# Main function to demonstrate CRUD operations
if __name__ == "__main__":
    print("Main")
    create_table()   # Run once to create the table
    create_item()
    read_items()
    update_item()
    read_items()
    delete_item()
    read_items()