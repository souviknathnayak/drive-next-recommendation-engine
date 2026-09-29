from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from .catalog import DEMO_CATALOG
from .engine import RecommendationAgent, fairness_audit, conformity_check

agent = RecommendationAgent()
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status": return self.reply({"monitor": agent.monitor.snapshot(), "conformity": conformity_check()})
        if self.path == "/":
            data = (Path(__file__).parent / "static" / "index.html").read_bytes(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(data); return
        self.send_error(404)
    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if self.path == "/api/recommend": return self.reply(agent.recommend(body.get("profile", {}), body.get("session_events", []), body.get("catalog", DEMO_CATALOG)))
            if self.path == "/api/fairness-audit": return self.reply(fairness_audit(body.get("rows", [])))
            self.send_error(404)
        except (ValueError, TypeError) as exc: self.reply({"error": str(exc)}, 400)
    def reply(self, value, status=200):
        data=json.dumps(value).encode(); self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *_): pass
if __name__ == "__main__":
    print("DriveNext listening at http://localhost:8080")
    ThreadingHTTPServer(("", 8080), Handler).serve_forever()
