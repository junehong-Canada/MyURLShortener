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

@app.route("/urls", methods=["POST"])
def create_short_url():
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
    app.run(port=8000, debug=True)