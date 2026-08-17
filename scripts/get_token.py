"""
One-time script: exchange a Strava OAuth 'code' for access + refresh tokens.

Strava OAuth (Authorization Code flow), the short version:
  1. You visit an /authorize URL in the browser and approve.
  2. Strava redirects to http://localhost/?code=XXXX  (the page won't load --
     that's fine; we only need the 'code' from the address bar).
  3. We POST that code to /oauth/token together with the client secret and get
     back an access_token (short-lived, ~6h) and a refresh_token (long-lived).
  4. From then on we never repeat this dance -- src/strava/auth.py uses the
     refresh_token to mint fresh access_tokens automatically.

Run:  python scripts/get_token.py
"""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
SCOPE = "activity:read_all"
TOKENS_PATH = Path(__file__).resolve().parent.parent / ".strava_tokens.json"


def main() -> None:
    authorize_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        "&redirect_uri=http://localhost"
        "&approval_prompt=force"
        f"&scope={SCOPE}"
    )
    print("\n1) Open this URL in your browser and click 'Authorize':\n")
    print(authorize_url)
    print(
        "\n2) Your browser will try to load http://localhost/?...&code=SOMECODE&..."
        "\n   The page will FAIL to load -- that's expected."
        "\n   Copy the value of 'code' from the address bar.\n"
    )
    code = input("Paste the code here: ").strip()

    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    resp.raise_for_status()
    tokens = resp.json()

    # Keep only what we need going forward.
    saved = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"],
    }
    TOKENS_PATH.write_text(json.dumps(saved, indent=2))
    athlete = tokens.get("athlete", {})
    print(f"\nSuccess. Tokens saved to {TOKENS_PATH.name}")
    print(f"Authorized athlete: {athlete.get('firstname')} {athlete.get('lastname')}")


if __name__ == "__main__":
    main()
