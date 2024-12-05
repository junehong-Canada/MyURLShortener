from http.server import HTTPServer, BaseHTTPRequestHandler

# Testing POST Requests
# curl -X POST -d "key=value" http://localhost:8000

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # Handle GET requests
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"  # Serve a default page if '/' is requested
        
        try:
            # Open the requested file
            with open(self.path[1:], "rb") as file:  # Remove leading '/' from path
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            # Send a 404 response if file is not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    # Handle POST requests
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get size of the POST data
        post_data = self.rfile.read(content_length)  # Read POST data
        print("Received POST data:", post_data.decode("utf-8"))

        # Send a response
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST request received!")

# Start the HTTP server
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)  # '' means all available interfaces
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()