import boto3

# DynamoDB Client
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000", region_name='us-east-1')

def create_url_table():
    table_name = 'UrlShortener'

    # Check if table already exists
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]
    if table_name in existing_tables:
        print(f"Table {table_name} already exists.")
        return

    # Define table schema
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'shortUrlId', 'KeyType': 'HASH'},  # Partition key
            {'AttributeName': 'userId', 'KeyType': 'RANGE'}     # Sort key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'shortUrlId', 'AttributeType': 'S'},
            {'AttributeName': 'userId', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    print("Creating table...")
    table.wait_until_exists()
    print(f"Table {table_name} created successfully.")

def insert_sample_item():
    table = dynamodb.Table('UrlShortener')

    sample_item = {
        "shortUrlId": "3ad32p9",
        "longUrl": "https://example.com/very-long-url",
        "creationDate": "2024-03-08T12:00:00Z",
        "userId": "user123",
        "clicks": 1023,
        "metadata": {
            "title": "Example Web Page",
            "tags": ["example", "web", "url shortener"],
            "expireDate": "2025-03-08T12:00:00Z"
        },
        "isActive": True
    }

    table.put_item(Item=sample_item)
    print("Sample item inserted successfully.")

# Run the function to insert the item
if __name__ == "__main__":
    insert_sample_item()

# Run the table creation function
# if __name__ == "__main__":
#     create_url_table()

# Ensure AWS Credentials:
# aws configure

# List Tables:
# aws dynamodb list-tables

# Scan Table:
# aws dynamodb scan --table-name URLShortener

# •	Global Secondary Indexes (GSI):
# Add GSIs to support queries by userId, metadata.title, or other fields.
# •	Serverless Deployment:
# Integrate with AWS SAM or AWS CDK for a fully automated deployment.