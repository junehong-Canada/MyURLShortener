from flask import Flask, request, jsonify   # pip install flask
import os  # Add this import

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Flask Web Server!"

@app.route("/data", methods=["POST"])
def handle_post():
    data = request.get_json()
    print("Received data:", data)
    return jsonify({"message": "Data received", "data": data}), 200


# MongoDB configuration
from pymongo import MongoClient
from urlshortener_mongodb import create_url, get_url_by_id, increment_clicks
from urlshortener_postgresql import get_unused_short_url, mark_url_used
import psycopg2
import redis  # Add this import

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.urlshortener
url_mappings = db.url_mappings

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Connect to PostgreSQL
# conn = psycopg2.connect(
#     dbname="urlshortener",
#     user="postgres",
#     password="postgres",
#     host="localhost"
# )
conn = psycopg2.connect(
    dbname="mydb",
    user="admin",
    password="password",
    host="localhost"
)

# Rate limiting configuration
from datetime import datetime, timedelta
from collections import defaultdict

# Store request counts per IP with timestamps
# Format: {ip_address: [(timestamp1, count1), (timestamp2, count2), ...]}
request_history = defaultdict(list)

# Rate limit settings
RATE_LIMIT = 10  # requests
TIME_WINDOW = 60  # seconds

def is_rate_limited(ip_address):
    """Check if an IP address has exceeded the rate limit."""
    now = datetime.now()
    cutoff_time = now - timedelta(seconds=TIME_WINDOW)
    
    # Clean up old entries
    request_history[ip_address] = [
        (timestamp, count) for timestamp, count in request_history[ip_address] 
        if timestamp > cutoff_time
    ]
    
    # Calculate total requests in time window
    total_requests = sum(count for _, count in request_history[ip_address])
    
    # Update request history
    if request_history[ip_address]:
        last_timestamp, count = request_history[ip_address][-1]
        if last_timestamp.timestamp() // 1 == now.timestamp() // 1:
            request_history[ip_address][-1] = (last_timestamp, count + 1)
        else:
            request_history[ip_address].append((now, 1))
    else:
        request_history[ip_address].append((now, 1))
    
    return total_requests >= RATE_LIMIT

@app.route("/urls", methods=["POST"])
def create_short_url():
    # Check rate limit
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    data = request.get_json()
    
    # Validate request
    if not data or 'longUrl' not in data:
        return jsonify({"error": "Invalid request. 'longUrl' field is required"}), 400
    
    long_url = data['longUrl']
    
    # Check Redis cache first
    cached_short_id = redis_client.get(f"long_url:{long_url}")
    if cached_short_id:
        short_id = str(cached_short_id)
        return jsonify({"shortUrl": f"{os.getenv('BASE_URL', 'http://localhost:8080/urls')}/{short_id}"}), 200
    
    # Check if URL already exists in MongoDB
    existing_url = db.urls.find_one({"longUrl": long_url})
    if existing_url:
        short_id = existing_url['shortUrlId']
        # Cache the mapping
        redis_client.setex(
            f"long_url:{long_url}", 
            timedelta(days=7), 
            short_id
        )
        redis_client.setex(
            f"short_url:{short_id}", 
            timedelta(days=7), 
            long_url
        )
        return jsonify({"shortUrl": f"{os.getenv('BASE_URL', 'http://localhost:8080/urls')}/{short_id}"}), 200
    
    # Get unused short URL from PostgreSQL
    short_id = get_unused_short_url(conn)
    if not short_id:
        return jsonify({"error": "No available short URLs"}), 500
    mark_url_used(conn, short_id)
    
    # Store URL in MongoDB
    create_url(
        db,
        short_id,
        long_url,
        user_id="anonymous",  # Could be enhanced with user authentication
        title=None,
        tags=None,
        expire_date=datetime.now() + timedelta(days=365*5)  # URLs expire after 5 years
    )
    
    # Cache the new mapping
    redis_client.setex(
        f"long_url:{long_url}", 
        timedelta(days=7), 
        short_id
    )
    redis_client.setex(
        f"short_url:{short_id}", 
        timedelta(days=7), 
        long_url
    )
    
    short_url = f"{os.getenv('BASE_URL', 'http://localhost:8080/urls')}/{short_id}"
    return jsonify({"shortUrl": short_url}), 201

@app.route("/urls/<short_id>", methods=["GET"])
def redirect_to_long_url(short_id):
    # Check rate limit
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    # Check Redis cache first
    cached_long_url = redis_client.get(f"short_url:{short_id}")
    if cached_long_url:
        long_url = cached_long_url if isinstance(cached_long_url, str) else cached_long_url.decode('utf-8')
        # Increment click count asynchronously
        increment_clicks(db, short_id)
        return jsonify({"longUrl": long_url}), 301, {'Location': long_url}

    print("short_id: ", short_id)
    # Get URL from MongoDB if not in cache
    url_mapping = get_url_by_id(db, short_id)
    if not url_mapping:
        return jsonify({"error": "Short URL not found"}), 404
    
    # Cache the mapping
    long_url = url_mapping['longUrl']
    redis_client.setex(
        f"short_url:{short_id}", 
        timedelta(days=7), 
        long_url
    )
    redis_client.setex(
        f"long_url:{long_url}", 
        timedelta(days=7), 
        short_id
    )

    # Increment click count
    increment_clicks(db, short_id)
    
    print("long_url: ", long_url)
    
    # Return 301 redirect to long URL
    # Using 301 for permanent redirect (browsers will cache)
    # Could use 302 instead if you want to track analytics
    return jsonify({"longUrl": long_url}), 301, {'Location': long_url}


if __name__ == "__main__":
    app.run(port=8080, debug=True)