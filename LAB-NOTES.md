# Lab results

Tested on 28 October 2026 using Ubuntu through WSL on Windows, with Python 3.14.4.

## Manual checks

I ran the local web server and monitor in separate terminals. I stopped the server while leaving the monitor running, then restarted it.

| Check | Observed result |
| --- | --- |
| Service running | UP, HTTP 200 |
| Server stopped | DOWN, connection refused |
| Server restarted | UP, HTTP 200 |
| Request to /missing | DOWN, HTTP 404 |
| CSV output | HTTP 200 and 404 results saved with timestamps and response times |

The monitor recorded a refused connection at 14:01:01 UTC and a successful HTTP 200 response at 14:01:52 UTC. These are check timestamps, not exact server stop/start times.

The missing-page check returned HTTP 404 at 14:02:49 UTC, with a recorded response time of 12.94 ms. This showed the difference between a server that cannot be reached and a server that responds but cannot find the requested page.

## Automated tests

Command:

```bash
python3 -m unittest discover -s tests -v
```

Result: all four tests passed in 0.514 seconds.

- Healthy service response
- Missing page response
- Unavailable service
- CSV appending without repeated headers

## Evidence

These results were transcribed from terminal output and screenshots provided during the lab. The original CSV remains on the learner's device and is not bundled here.
