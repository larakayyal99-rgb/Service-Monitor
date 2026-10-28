# Service Monitor

A small Python tool that checks an HTTP service and saves the results to a CSV file. This is a local lab project for learning about service availability, logging, and troubleshooting.

## What it does

- Checks a URL once or repeatedly.
- Records the time, HTTP code, response time, and any connection error.
- Marks 2xx responses as UP and other responses as DOWN.
- Returns exit code 0 for a successful one-time check and 1 for a failed check.

A 404 means the server answered but the requested page was not found. A connection error means no HTTP response was received. The CSV keeps that distinction even though both count as DOWN for this check.

## Run it

Python 3.10 or newer is required. No extra packages are needed.

First, open a terminal in the extracted project folder, the folder containing `monitor.py`, `demo`, and `tests`.

If your terminal opens in your home folder, use `cd` to navigate to the project folder. Its location depends on where you saved it.

Repeat this step for the second terminal before starting the monitor.
```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory demo
```

Keep that terminal open. In another terminal, open the same project folder and run:

```bash
python3 monitor.py
```

The monitor checks every five seconds and appends results to `results/checks.csv`. Stop either command with Ctrl+C.

For one check:

```bash
python3 monitor.py --once
```

## Try a failure and recovery

1. Start the service and monitor. Look for UP and HTTP 200.
2. Stop only the service with Ctrl+C. Leave the monitor running.
3. Wait for a DOWN result.
4. Restart the service using the original command.
5. Look for UP again and compare the CSV rows.

To check a missing page:

```bash
python3 monitor.py --url http://127.0.0.1:8000/missing --once
```

See the recorded results in [LAB-NOTES.md](LAB-NOTES.md), or repeat the steps to reproduce them.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The four tests cover a healthy response, a missing page, an unavailable service, and CSV appending. They use a temporary local server and do not need internet access.

## Limits

This is a single-process learning tool, not production monitoring. Timing measures the HTTP request through response headers, not a full-page download. Checks run sequentially; the interval is the pause after each check. There are no alerts, retries, uptime calculations, or response-body checks. Use one monitor process per CSV file.

## Project status

Tested on Ubuntu through WSL with Python 3.14.4. Manual checks covered a healthy service, a stopped server, recovery after restart, and a missing page. All four automated tests passed. See [Lab results](LAB-NOTES.md) for the observations.

