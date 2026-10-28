"""Check a local HTTP service and save each result to CSV."""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import urlopen


def check_service(url, timeout=3):
    started = time.perf_counter()
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": url,
        "status": "DOWN",
        "http_code": "",
        "response_ms": "",
        "error": "",
    }
    try:
        with urlopen(url, timeout=timeout) as response:
            result["http_code"] = response.status
            result["status"] = "UP" if 200 <= response.status < 300 else "DOWN"
            if result["status"] == "DOWN":
                result["error"] = f"Unexpected HTTP status: {response.status}"
    except HTTPError as error:
        # A server can respond while the requested page is unhealthy.
        result["http_code"] = error.code
        result["error"] = f"HTTP {error.code}"
        error.close()
    except (URLError, TimeoutError, OSError) as error:
        result["error"] = str(getattr(error, "reason", error))
    result["response_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return result


def save_result(result, filename):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(result))
        if needs_header:
            writer.writeheader()
        writer.writerow(result)


def positive_number(value):
    import math
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Use a finite number greater than zero.")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000/")
    parser.add_argument("--interval", type=positive_number, default=5)
    parser.add_argument("--timeout", type=positive_number, default=3)
    parser.add_argument("--log", default="results/checks.csv")
    parser.add_argument("--once", action="store_true", help="Check once, then exit.")
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        parser.error("Use an http:// or https:// URL with a hostname.")
    try:
        while True:
            result = check_service(args.url, args.timeout)
            save_result(result, args.log)
            detail = result["error"] or f"HTTP {result['http_code']}"
            print(f"{result['timestamp']} {result['status']} {detail} "
                  f"({result['response_ms']} ms)", flush=True)
            if args.once:
                return 0 if result["status"] == "UP" else 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
