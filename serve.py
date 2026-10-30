"""Simple HTTP Server & API Bridge for AURA Clinical Triage Frontend.
Runs with standard library (no extra dependencies required).

Usage:
    python serve.py
    Opens http://localhost:8000
"""
import http.server
import json
import os
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


class TriageHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/triage":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                query = data.get("query", "")
                
                # Import agent dynamically to bridge directly into main agent execution
                try:
                    from main import run_agent
                    dry_run = bool(data.get("dry_run", False)) or bool(os.environ.get("AGENTX_DRY_RUN", False))
                    answer, trace = run_agent(query, dry_run=dry_run, verbose=False)
                    response = {"status": "ok", "answer": answer, "trace": trace}
                except Exception as e:
                    response = {"status": "error", "error": f"{type(e).__name__}: {str(e)}"}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run():
    os.chdir(BASE_DIR)
    print(f"\n========================================================")
    print(f"  🏥 AURA Clinical Triage Claymorphism UI Server")
    print(f"  Serving at: http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop.")
    print(f"========================================================\n")
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, TriageHTTPHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    run()
