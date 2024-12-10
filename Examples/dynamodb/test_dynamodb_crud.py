import pytest
import os
from moto import mock_dynamodb
import boto3
from datetime import datetime
# pip install pytest moto boto3 python-dotenv
# pytest test_dynamodb_crud.py
from dynamodb_crud import (
    create_short_url,
    get_short_url,
    update_short_url,
    delete_short_url,
)

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "short_urls_table")


# Fixtures
@pytest.fixture
def mock_dynamodb_table():
    """Set up a mocked DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[{"AttributeName": "shortUrlId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "shortUrlId", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.meta.client.get_waiter("table_exists").wait(TableName=DYNAMODB_TABLE_NAME)
        yield table


# Test Data
@pytest.fixture
def sample_item():
    """Provide a sample item for tests."""
    return {
        "shortUrlId": "3ad32p9",
        "longUrl": "https://example.com/very-long-url",
        "creationDate": datetime.utcnow().isoformat() + "Z",
        "userId": "user123",
        "clicks": 1023,
        "metadata": {
            "title": "Example Web Page",
            "tags": ["example", "web", "url shortener"],
            "expireDate": "2025-03-08T12:00:00Z",
        },
        "isActive": True,
    }


# Tests
def test_create_short_url(mock_dynamodb_table, sample_item):
    """Test creating an item in DynamoDB."""
    result = create_short_url(
        short_url_id=sample_item["shortUrlId"],
        long_url=sample_item["longUrl"],
        user_id=sample_item["userId"],
        metadata=sample_item["metadata"],
        clicks=sample_item["clicks"],
        is_active=sample_item["isActive"],
    )
    assert result["shortUrlId"] == sample_item["shortUrlId"]
    assert result["longUrl"] == sample_item["longUrl"]


def test_get_short_url(mock_dynamodb_table, sample_item):
    """Test retrieving an item from DynamoDB."""
    # Insert item directly into mocked table
    mock_dynamodb_table.put_item(Item=sample_item)

    # Retrieve item
    result = get_short_url(sample_item["shortUrlId"])
    assert result["shortUrlId"] == sample_item["shortUrlId"]
    assert result["longUrl"] == sample_item["longUrl"]


def test_update_short_url(mock_dynamodb_table, sample_item):
    """Test updating an item in DynamoDB."""
    # Insert item directly into mocked table
    mock_dynamodb_table.put_item(Item=sample_item)

    # Update the item
    updates = {"clicks": 1050, "isActive": False}
    updated_item = update_short_url(sample_item["shortUrlId"], updates)

    assert updated_item["clicks"] == 1050
    assert updated_item["isActive"] is False


def test_delete_short_url(mock_dynamodb_table, sample_item):
    """Test deleting an item from DynamoDB."""
    # Insert item directly into mocked table
    mock_dynamodb_table.put_item(Item=sample_item)

    # Delete the item
    delete_short_url(sample_item["shortUrlId"])

    # Ensure the item no longer exists
    result = get_short_url(sample_item["shortUrlId"])
    assert result is None