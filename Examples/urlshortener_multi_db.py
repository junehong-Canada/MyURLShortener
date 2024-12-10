from flask import Flask, request, jsonify
import redis
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import psycopg2
from pymongo import MongoClient
import boto3
from botocore.exceptions import ClientError
# pip install flask redis psycopg2-binary pymongo boto3

# export STORAGE_BACKEND=postgresql  # or mongodb or dynamodb
# export REDIS_HOST=localhost
# export REDIS_PORT=6379

app = Flask(__name__)

# Redis Configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Abstract Database Interface
class URLStorageBackend(ABC):
    @abstractmethod
    def store_url(self, short_id: str, long_url: str) -> bool:
        pass
    
    @abstractmethod
    def get_url(self, short_id: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def url_exists(self, long_url: str) -> Optional[str]:
        pass

# PostgreSQL Implementation
class PostgreSQLBackend(URLStorageBackend):
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('PG_DATABASE', 'urlshortener'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres'),
            host=os.getenv('PG_HOST', 'localhost')
        )
        self._create_table()
    
    def _create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS url_mappings (
                    short_id VARCHAR(50) PRIMARY KEY,
                    long_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.conn.commit()

    def store_url(self, short_id: str, long_url: str) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO url_mappings (short_id, long_url) VALUES (%s, %s)",
                    (short_id, long_url)
                )
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def get_url(self, short_id: str) -> Optional[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT long_url FROM url_mappings WHERE short_id = %s", (short_id,))
            result = cur.fetchone()
            return result[0] if result else None

    def url_exists(self, long_url: str) -> Optional[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT short_id FROM url_mappings WHERE long_url = %s", (long_url,))
            result = cur.fetchone()
            return result[0] if result else None

# MongoDB Implementation
class MongoDBBackend(URLStorageBackend):
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.urlshortener
        self.collection = self.db.url_mappings

    def store_url(self, short_id: str, long_url: str) -> bool:
        try:
            self.collection.insert_one({
                'short_id': short_id,
                'long_url': long_url
            })
            return True
        except Exception:
            return False

    def get_url(self, short_id: str) -> Optional[str]:
        result = self.collection.find_one({'short_id': short_id})
        return result['long_url'] if result else None

    def url_exists(self, long_url: str) -> Optional[str]:
        result = self.collection.find_one({'long_url': long_url})
        return result['short_id'] if result else None

# DynamoDB Implementation
class DynamoDBBackend(URLStorageBackend):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('url_mappings')
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        try:
            self.dynamodb.create_table(
                TableName='url_mappings',
                KeySchema=[
                    {'AttributeName': 'short_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'short_id', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

    def store_url(self, short_id: str, long_url: str) -> bool:
        try:
            self.table.put_item(
                Item={
                    'short_id': short_id,
                    'long_url': long_url
                }
            )
            return True
        except Exception:
            return False

    def get_url(self, short_id: str) -> Optional[str]:
        try:
            response = self.table.get_item(Key={'short_id': short_id})
            return response['Item']['long_url'] if 'Item' in response else None
        except Exception:
            return None

    def url_exists(self, long_url: str) -> Optional[str]:
        try:
            response = self.table.scan(
                FilterExpression='long_url = :url',
                ExpressionAttributeValues={':url': long_url}
            )
            items = response.get('Items', [])
            return items[0]['short_id'] if items else None
        except Exception:
            return None

# Database factory
def get_storage_backend() -> URLStorageBackend:
    backend_type = os.getenv('STORAGE_BACKEND', 'postgresql')
    backends = {
        'postgresql': PostgreSQLBackend,
        'mongodb': MongoDBBackend,
        'dynamodb': DynamoDBBackend
    }
    return backends[backend_type]()

# Initialize storage backend
storage = get_storage_backend()

# ... (keep the rate limiting code from the original file) ...

@app.route("/urls", methods=["POST"])
def create_short_url():
    # Rate limiting check (keep existing code)
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    data = request.get_json()
    if not data or 'longUrl' not in data:
        return jsonify({"error": "Invalid request. 'longUrl' field is required"}), 400
    
    long_url = data['longUrl']
    
    # Check Redis cache first
    existing_short_id = redis_client.get(f"url:{long_url}")
    if existing_short_id:
        return jsonify({"shortUrl": f"https://tiny.url/{existing_short_id}"}), 200
    
    # Check database
    existing_short_id = storage.url_exists(long_url)
    if existing_short_id:
        # Update Redis cache
        redis_client.setex(f"url:{long_url}", 3600, existing_short_id)
        redis_client.setex(f"id:{existing_short_id}", 3600, long_url)
        return jsonify({"shortUrl": f"https://tiny.url/{existing_short_id}"}), 200
    
    # Generate new short ID (implement your preferred method)
    short_id = generate_short_id()  # You'll need to implement this
    
    # Store in database
    if storage.store_url(short_id, long_url):
        # Update Redis cache
        redis_client.setex(f"url:{long_url}", 3600, short_id)
        redis_client.setex(f"id:{short_id}", 3600, long_url)
        return jsonify({"shortUrl": f"https://tiny.url/{short_id}"}), 201
    
    return jsonify({"error": "Failed to create short URL"}), 500

@app.route("/urls/<short_id>", methods=["GET"])
def redirect_to_long_url(short_id):
    # Rate limiting check (keep existing code)
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    # Check Redis cache first
    long_url = redis_client.get(f"id:{short_id}")
    if not long_url:
        # Check database
        long_url = storage.get_url(short_id)
        if long_url:
            # Update Redis cache
            redis_client.setex(f"id:{short_id}", 3600, long_url)
            redis_client.setex(f"url:{long_url}", 3600, short_id)
    
    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404
    
    return jsonify({"longUrl": long_url}), 301, {'Location': long_url} 

if __name__ == "__main__":
    app.run(port=8080, debug=True)