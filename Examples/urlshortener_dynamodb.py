import boto3
from datetime import datetime
from typing import Dict, Optional, List
from boto3.dynamodb.conditions import Key

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
            {'AttributeName': 'shortUrlId', 'KeyType': 'HASH'}  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'shortUrlId', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    print("Creating table...")
    table.wait_until_exists()
    print(f"Table {table_name} created successfully.")

def create_url(short_url_id: str, long_url: str, 
               title: Optional[str] = None, tags: Optional[List[str]] = None,
               expire_date: Optional[str] = None) -> Dict:
    """Create a new URL mapping"""
    table = dynamodb.Table('UrlShortener')
    
    item = {
        'shortUrlId': short_url_id,
        'longUrl': long_url,
        'creationDate': datetime.now().isoformat(),
        'clicks': 0,
        'isActive': True,
        'metadata': {
            'title': title,
            'tags': tags if tags else [],
            'expireDate': expire_date
        }
    }
    
    table.put_item(Item=item)
    return item


def get_short_url_id(long_url: str) -> Optional[str]:
    """Get short URL ID by long URL"""
    table = dynamodb.Table('UrlShortener')
    
    response = table.query(
        IndexName='longUrlIndex',
        KeyConditionExpression=Key('longUrl').eq(long_url)
    )
    
    items = response['Items']
    if items:
        return items[0]['shortUrlId']
    else:
        return None


def get_url_by_id(short_url_id: str) -> Optional[Dict]:
    """Read a URL mapping by short URL ID"""
    table = dynamodb.Table('UrlShortener')
    
    response = table.get_item(
        Key={
            'shortUrlId': short_url_id
        }
    )
    
    return response.get('Item')

def update_url(short_url_id: str, 
               long_url: Optional[str] = None,
               title: Optional[str] = None, 
               tags: Optional[List[str]] = None,
               expire_date: Optional[str] = None,
               is_active: Optional[bool] = None) -> Dict:
    """Update a URL mapping"""
    table = dynamodb.Table('UrlShortener')
    
    update_expr = ['SET']
    expr_values = {}
    expr_names = {}
    
    if long_url is not None:
        update_expr.append('#lu = :lu')
        expr_values[':lu'] = long_url
        expr_names['#lu'] = 'longUrl'
        
    if title is not None:
        update_expr.append('#md.#t = :t')
        expr_values[':t'] = title
        expr_names['#md'] = 'metadata'
        expr_names['#t'] = 'title'
        
    if tags is not None:
        update_expr.append('#md.#tg = :tg')
        expr_values[':tg'] = tags
        expr_names['#tg'] = 'tags'
        
    if expire_date is not None:
        update_expr.append('#md.#ed = :ed')
        expr_values[':ed'] = expire_date
        expr_names['#ed'] = 'expireDate'
        
    if is_active is not None:
        update_expr.append('#ia = :ia')
        expr_values[':ia'] = is_active
        expr_names['#ia'] = 'isActive'

    response = table.update_item(
        Key={
            'shortUrlId': short_url_id
        },
        UpdateExpression=' '.join(update_expr),
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names,
        ReturnValues='ALL_NEW'
    )
    
    return response['Attributes']

def delete_url(short_url_id: str):
    """Delete a URL mapping"""
    table = dynamodb.Table('UrlShortener')
    
    table.delete_item(
        Key={
            'shortUrlId': short_url_id
        }
    )

def increment_clicks(short_url_id: str):
    """Increment the click count for a URL"""
    table = dynamodb.Table('UrlShortener')
    
    table.update_item(
        Key={
            'shortUrlId': short_url_id
        },
        UpdateExpression='SET clicks = clicks + :inc',
        ExpressionAttributeValues={
            ':inc': 1
        }
    )

# Example usage
if __name__ == "__main__":
    # Create table if needed
    create_url_table()
    
    # Example CRUD operations
    short_id = "3ad32p9"
    
    # Create
    url = create_url(
        short_id,
        "https://example.com/very-long-url",
        title="Example Web Page",
        tags=["example", "web"],
        expire_date="2025-03-08T12:00:00Z"
    )
    print("Created URL:", url)
    
    # Read
    retrieved_url = get_url_by_id(short_id)
    print("Retrieved URL:", retrieved_url)
    
    # Update
    updated_url = update_url(
        short_id,
        title="Updated Example Page",
        tags=["example", "web", "updated"]
    )
    print("Updated URL:", updated_url)
    
    # Increment clicks
    increment_clicks(short_id)
    
    # Delete
    delete_url(short_id)
    print("URL deleted")