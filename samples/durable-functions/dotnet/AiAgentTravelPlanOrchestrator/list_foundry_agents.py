import argparse
import json
import os
import sys

import requests
from azure.identity import DefaultAzureCredential

# Debug defaults for local F5 runs in VS Code.
# Replace these with your real values when running in debug mode.
DEBUG_FOUNDRY_ENDPOINT = "https://foundry1704.services.ai.azure.com"
DEBUG_FOUNDRY_PROJECT_NAME = "proj-default"
DEBUG_API_VERSION = "v1"
DEBUG_OUTPUT_FILE = "foundry_agents.json"

API_VERSION_CANDIDATES = [
    "v1",
    "2025-05-01",
    "2024-10-21",
    "2024-05-01-preview",
]


def get_access_token() -> str:
    """Authenticate with the currently logged-in Azure identity and get a bearer token."""
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    scopes = [
        "https://ai.azure.com/.default",
        "https://cognitiveservices.azure.com/.default",
    ]

    last_error = None
    for scope in scopes:
        try:
            token = credential.get_token(scope)
            return token.token
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise RuntimeError(
        "Failed to get an access token for AI Foundry. "
        "Make sure you are logged in (for example with 'az login') and have access to the project."
    ) from last_error


def _try_list_agents(
    endpoint: str, project_name: str, access_token: str, api_version: str
) -> requests.Response:
    url = f"{endpoint.rstrip('/')}/api/projects/{project_name}/agents"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    params = {"api-version": api_version}

    return requests.get(url, headers=headers, params=params, timeout=30)


def list_agents(
    endpoint: str, project_name: str, access_token: str, preferred_api_version: str
) -> tuple[dict, str]:
    versions_to_try = [preferred_api_version] + [
        version for version in API_VERSION_CANDIDATES if version != preferred_api_version
    ]

    last_http_error: requests.HTTPError | None = None

    for api_version in versions_to_try:
        response = _try_list_agents(endpoint, project_name, access_token, api_version)

        if response.ok:
            return response.json(), api_version

        is_unsupported = (
            response.status_code == 400
            and "UnsupportedApiVersion" in (response.text or "")
        )

        if is_unsupported:
            continue

        response.raise_for_status()

    # If we reach this point, every attempted version returned UnsupportedApiVersion.
    if response is not None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            last_http_error = exc

    if last_http_error is not None:
        raise last_http_error

    raise RuntimeError("Failed to list agents for unknown reasons")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List Azure AI Foundry agents using your logged-in Azure identity."
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("FOUNDRY_ENDPOINT") or DEBUG_FOUNDRY_ENDPOINT,
        help="Foundry endpoint, e.g. https://YOUR_ENDPOINT",
    )
    parser.add_argument(
        "--project",
        default=os.getenv("FOUNDRY_PROJECT_NAME") or DEBUG_FOUNDRY_PROJECT_NAME,
        help="Foundry project name",
    )
    parser.add_argument(
        "--api-version",
        default=os.getenv("FOUNDRY_API_VERSION") or DEBUG_API_VERSION,
        help="API version for the agents endpoint (for example: v1 or 2025-05-01)",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("FOUNDRY_OUTPUT_FILE") or DEBUG_OUTPUT_FILE,
        help="Path to save the JSON response (default: foundry_agents.json)",
    )
    return parser.parse_args()


def save_json_to_file(payload: dict, output_path: str) -> str:
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2)
    return os.path.abspath(output_path)


def main() -> int:
    args = parse_args()

    if (
        not args.endpoint
        or not args.project
        or args.endpoint == "https://YOUR_ENDPOINT"
        or args.project == "YOUR_PROJECT_NAME"
    ):
        print(
            "Missing endpoint/project. Provide --endpoint and --project, "
            "or set FOUNDRY_ENDPOINT and FOUNDRY_PROJECT_NAME, "
            "or update DEBUG_FOUNDRY_ENDPOINT and DEBUG_FOUNDRY_PROJECT_NAME in the script.",
            file=sys.stderr,
        )
        return 1

    try:
        token = get_access_token()
        payload, api_version_used = list_agents(
            args.endpoint, args.project, token, args.api_version
        )
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body = exc.response.text if exc.response is not None else str(exc)
        print(f"HTTP error ({status}): {body}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 3

    try:
        saved_path = save_json_to_file(payload, args.output)
    except Exception as exc:  # noqa: BLE001
        print(f"Error saving JSON file: {exc}", file=sys.stderr)
        return 4

    print(f"API version used: {api_version_used}")
    print(f"Saved JSON response to: {saved_path}")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
