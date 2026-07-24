import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# START_URL = "http://localhost:7071/api/StartChaining"
START_URL = "http://localhost:7071/api/StartFanOutFanIn"
MAX_POLLS = 20
POLL_INTERVAL_SECONDS = 0.5


def http_json(method: str, url: str) -> dict:
    request = Request(url, method=method)
    with urlopen(request) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def main() -> int:
    try:
        post_response = http_json("POST", START_URL)
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        print(f"Failed to start orchestration: {exc}", file=sys.stderr)
        return 1

    status_url = post_response.get("statusQueryGetUri")
    if not status_url:
        print("Missing statusQueryGetUri in starter response", file=sys.stderr)
        return 1

    for _ in range(MAX_POLLS):
        try:
            status = http_json("GET", status_url)
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            print(f"Failed to query orchestration status: {exc}", file=sys.stderr)
            return 1

        runtime_status = status.get("runtimeStatus")

        if runtime_status == "Completed":
            print(json.dumps(status.get("output"), indent=2))
            return 0

        if runtime_status in {"Failed", "Terminated"}:
            print(json.dumps(status, indent=2))
            return 1

        time.sleep(POLL_INTERVAL_SECONDS)

    print("Timed out waiting for orchestration completion", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
