import argparse
import sys
import time
from datetime import datetime

import requests


def poll(base_url, interval):
    url = f"{base_url}/internal/daemon"
    print(f"Polling {url} every {interval}s. Ctrl+C to stop.\n")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            response = requests.post(url)
            print(f"[{timestamp}] {response.status_code} {response.json()}")
        except requests.exceptions.ConnectionError:
            print(f"[{timestamp}] Error: could not connect to {url}. Is the server running?")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repeatedly POST to /internal/daemon.")
    parser.add_argument(
        "-u", "--url",
        default="http://127.0.0.1:5000",
        help="Base URL of the Flask app (default: http://127.0.0.1:5000)",
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=30,
        help="Seconds between requests (default: 30)",
    )
    args = parser.parse_args()

    try:
        poll(args.url, args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
