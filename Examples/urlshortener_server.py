from flask import Flask, request, jsonify   # pip install flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Flask Web Server!"

@app.route("/data", methods=["POST"])
def handle_post():
    data = request.get_json()
    print("Received data:", data)
    return jsonify({"message": "Data received", "data": data}), 200

# Store URL mappings in memory (in production, use a database)
url_mappings = {}
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
    
    # Check if URL already exists
    for short, long in url_mappings.items():
        if long == long_url:
            return jsonify({"error": "URL already exists", "shortUrl": f"https://tiny.url/{short}"}), 409
    
    # Generate short URL (simple implementation using length of dictionary)
    # In production, use a more robust method
    short_id = hex(len(url_mappings))[2:]
    short_url = f"https://tiny.url/{short_id}"
    
    # Store the mapping
    url_mappings[short_id] = long_url
    
    return jsonify({"shortUrl": short_url}), 201

@app.route("/urls/<short_id>", methods=["GET"])
def redirect_to_long_url(short_id):
    # Check rate limit
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    # Check if short URL ID exists in mappings
    if short_id not in url_mappings:
        return jsonify({"error": "Short URL not found"}), 404
        
    # Get the long URL from mappings
    long_url = url_mappings[short_id]
    
    # Return 301 redirect to long URL
    # Using 301 for permanent redirect (browsers will cache)
    # Could use 302 instead if you want to track analytics
    return jsonify({"longUrl": long_url}), 301, {'Location': long_url}


if __name__ == "__main__":
    app.run(port=8080, debug=True)