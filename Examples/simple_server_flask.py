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

if __name__ == "__main__":
    app.run(port=8000, debug=True)