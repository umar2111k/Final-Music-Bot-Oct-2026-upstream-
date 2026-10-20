import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello Spark! Bot is alive and running.")

def run_server():
    # Koyeb/Render auto-assigns a PORT variable, default to 8000 if not found
    port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Web server started successfully on port {port}")
    httpd.serve_forever()

def keep_alive():
    # Run the web server in a background thread so it doesn't block the bot
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
