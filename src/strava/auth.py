"""
Token management. After the one-time scripts/get_token.py run, everything else
in the app calls get_access_token() -- it transparently refreshes when the
current access token is expired, so callers never think about OAuth.
"""
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

TOKENS_PATH = Path(__file__).resolve().parents[2] / ".strava_tokens.json"


def _load() -> dict:
    if not TOKENS_PATH.exists():
        raise FileNotFoundError(
            "No .strava_tokens.json found. Run: python scripts/get_token.py"
        )
    return json.loads(TOKENS_PATH.read_text())


def _refresh(tokens: dict) -> dict:
    resp = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    new = resp.json()
    tokens.update(
        access_token=new["access_token"],
        refresh_token=new["refresh_token"],  # Strava may rotate it
        expires_at=new["expires_at"],
    )
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))
    return tokens


def get_access_token() -> str:
    tokens = _load()
    # Refresh a minute early to avoid races near the boundary.
    if tokens["expires_at"] <= time.time() + 60:
        tokens = _refresh(tokens)
    return tokens["access_token"]
