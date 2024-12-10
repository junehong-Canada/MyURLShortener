from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import json

# Load .env file
load_dotenv()

# Environment Variables
DYNAMODB_HOST = os.getenv("DYNAMODB_HOST", "localhost")
DYNAMODB_PORT = os.getenv("DYNAMODB_PORT", "8000")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "short_urls_table")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your_access_key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your_secret_key")

# DynamoDB Connection
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=f"http://{DYNAMODB_HOST}:{DYNAMODB_PORT}",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


# Create (Insert)
def create_short_url(short_url_id, long_url, user_id, metadata, clicks=0, is_active=True):
    try:
        item = {
            "shortUrlId": short_url_id,
            "longUrl": long_url,
            "creationDate": datetime.now().isoformat() + "Z",
            "userId": user_id,
            "clicks": clicks,
            "metadata": metadata,
            "isActive": is_active
        }
        table.put_item(Item=item)
        print(f"Item created: {item}")
        return item
    except ClientError as e:
        print(f"Error creating item: {e.response['Error']['Message']}")


# Read (Retrieve)
def get_short_url(short_url_id):
    try:
        response = table.get_item(Key={"shortUrlId": short_url_id})
        if "Item" in response:
            return response["Item"]
        else:
            print(f"No item found with shortUrlId: {short_url_id}")
            return None
    except ClientError as e:
        print(f"Error retrieving item: {e.response['Error']['Message']}")


# Update
def update_short_url(short_url_id, updates):
    try:
        update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
        expression_values = {f":{k}": v for k, v in updates.items()}

        response = table.update_item(
            Key={"shortUrlId": short_url_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        print(f"Item updated: {response['Attributes']}")
        return response["Attributes"]
    except ClientError as e:
        print(f"Error updating item: {e.response['Error']['Message']}")


# Delete
def delete_short_url(short_url_id):
    try:
        response = table.delete_item(Key={"shortUrlId": short_url_id})
        print(f"Item deleted: {short_url_id}")
        return response
    except ClientError as e:
        print(f"Error deleting item: {e.response['Error']['Message']}")


# Main: Testing the CRUD Operations
if __name__ == "__main__":
    # Test metadata
    test_metadata = {
        "title": "Example Web Page",
        "tags": ["example", "web", "url shortener"],
        "expireDate": "2025-03-08T12:00:00Z"
    }

    # Test data
    short_url_id = "3ad32p9"
    long_url = "https://example.com/very-long-url"
    user_id = "user123"

    # Test Create
    print("\nCreating item:")
    create_short_url(short_url_id, long_url, user_id, test_metadata, clicks=1023)

    # Test Read
    print("\nReading item:")
    item = get_short_url(short_url_id)
    print(item)

    # Test Update
    print("\nUpdating item:")
    updates = {"clicks": 1050, "isActive": False}
    updated_item = update_short_url(short_url_id, updates)
    print(updated_item)

    # Test Delete
    print("\nDeleting item:")
    delete_short_url(short_url_id)