import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from monitor import check_service, save_result


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path == "/" else 404)
        self.end_headers()
        self.wfile.write(b"Local test service")

    def log_message(self, *args):
        pass


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_healthy_service(self):
        result = check_service(self.url)
        self.assertEqual((result["status"], result["http_code"]), ("UP", 200))
        self.assertEqual(result["error"], "")

    def test_missing_page_is_down(self):
        result = check_service(self.url + "/missing")
        self.assertEqual((result["status"], result["http_code"]), ("DOWN", 404))

    def test_unavailable_service(self):
        # Reserve a port without listening, so a TCP connection is refused.
        with socket.socket() as reserved:
            reserved.bind(("127.0.0.1", 0))
            result = check_service(f"http://127.0.0.1:{reserved.getsockname()[1]}")
        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(result["http_code"], "")
        self.assertTrue(result["error"])

    def test_csv_appends_without_repeating_header(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "checks.csv"
            for _ in range(2):
                save_result(check_service(self.url), path)
            with path.open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["status"] == "UP" for row in rows))


if __name__ == "__main__":
    unittest.main()
