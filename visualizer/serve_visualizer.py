"""
Visualizer HTTP Server

Simple HTTP server that serves the visualizer frontend and provides
API endpoints for state polling.

Endpoints:
- GET /              → serves commodity_trading.html
- GET /api/state     → returns current visualizer state as JSON
- GET /api/outputs   → returns module outputs (if available)
"""

import json
import os
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


# Get the visualizer directory
VISUALIZER_DIR = Path(__file__).parent
PROJECT_ROOT = VISUALIZER_DIR.parent
CONTEXT_DIR = PROJECT_ROOT / "context"
MODULES_DIR = PROJECT_ROOT / "modules"


class VisualizerHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for visualizer."""

    def __init__(self, *args, **kwargs):
        # Set directory to visualizer folder
        super().__init__(*args, directory=str(VISUALIZER_DIR), **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # API endpoints
        if path == "/api/state":
            self._serve_state()
        elif path == "/api/outputs":
            self._serve_outputs()
        elif path == "/" or path == "/index.html":
            self._serve_file("commodity_trading.html")
        else:
            # Serve static files
            super().do_GET()

    def _serve_state(self):
        """Serve the visualizer state JSON."""
        state_file = CONTEXT_DIR / "visualizer_state.json"

        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self._send_json(state)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            # Return empty state if file doesn't exist
            self._send_json({
                "status": "idle",
                "commodity": "",
                "agents": {},
                "chat_log": [],
                "progress": 0,
                "message": "Waiting for analysis to start..."
            })

    def _serve_outputs(self):
        """Serve module outputs."""
        outputs = {}

        # Check for module output files
        if MODULES_DIR.exists():
            for commodity_dir in MODULES_DIR.iterdir():
                if commodity_dir.is_dir():
                    commodity_outputs = {}
                    for output_file in commodity_dir.glob("*_output.json"):
                        try:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                module_name = output_file.stem.replace("_output", "")
                                commodity_outputs[module_name] = data
                        except Exception:
                            pass
                    if commodity_outputs:
                        outputs[commodity_dir.name] = commodity_outputs

        self._send_json(outputs)

    def _serve_file(self, filename: str):
        """Serve a specific file."""
        filepath = VISUALIZER_DIR / filename

        if filepath.exists():
            self.send_response(200)
            self.send_header("Content-Type", self._get_content_type(filename))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()

            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, f"File not found: {filename}")

    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(json_bytes)

    def _get_content_type(self, filename: str) -> str:
        """Get content type for file."""
        ext = Path(filename).suffix.lower()
        content_types = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }
        return content_types.get(ext, "application/octet-stream")

    def log_message(self, format, *args):
        """Suppress default logging (too noisy with polling)."""
        pass


def start_server(port: int = 8765, open_browser: bool = True):
    """Start the HTTP server."""
    # Ensure context directory exists
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

    server = HTTPServer(('localhost', port), VisualizerHandler)
    print(f"[Visualizer] Server running at http://localhost:{port}")

    if open_browser:
        webbrowser.open(f"http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Visualizer] Server stopped")
        server.shutdown()


def start_server_thread(port: int = 8765) -> threading.Thread:
    """Start server in background thread."""
    # Ensure context directory exists
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

    server = HTTPServer(('localhost', port), VisualizerHandler)

    def run():
        print(f"[Visualizer] Server running at http://localhost:{port}")
        server.serve_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Commodity Trading Visualizer Server")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")

    args = parser.parse_args()
    start_server(args.port, open_browser=not args.no_browser)
