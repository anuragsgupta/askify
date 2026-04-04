"""
Share Routes — generate and validate shareable upload links.
"""
import uuid
import json
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from typing import Optional

from server.routes.upload import upload_file as _do_upload

router = APIRouter()

SHARE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "share_tokens.json")


def _load_tokens():
    if os.path.exists(SHARE_FILE):
        with open(SHARE_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_tokens(data):
    with open(SHARE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


@router.post("/share/create")
async def create_share_link():
    """Generate a unique shareable upload token."""
    token = uuid.uuid4().hex[:16]
    tokens = _load_tokens()
    tokens[token] = {
        "created": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(days=7)).isoformat(),
        "uses": 0,
        "active": True,
    }
    _save_tokens(tokens)

    return {
        "token": token,
        "expires_in": "7 days",
        "upload_url": f"/upload/{token}",
    }


@router.get("/share/validate/{token}")
async def validate_token(token: str):
    """Check if a share token is valid."""
    tokens = _load_tokens()
    if token not in tokens:
        raise HTTPException(status_code=404, detail="Invalid or expired share link.")

    info = tokens[token]
    if not info.get("active", False):
        raise HTTPException(status_code=410, detail="This share link has been deactivated.")

    # Check expiry
    try:
        expires = datetime.fromisoformat(info["expires"])
        if datetime.now() > expires:
            raise HTTPException(status_code=410, detail="This share link has expired.")
    except (ValueError, KeyError):
        pass

    return {"valid": True, "token": token}


@router.post("/share/upload/{token}")
async def shared_upload(
    token: str,
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None),
):
    """Upload a file using a shareable link token."""
    # Validate token
    tokens = _load_tokens()
    if token not in tokens:
        raise HTTPException(status_code=404, detail="Invalid share link.")

    info = tokens[token]
    if not info.get("active", False):
        raise HTTPException(status_code=410, detail="This share link has been deactivated.")

    try:
        expires = datetime.fromisoformat(info["expires"])
        if datetime.now() > expires:
            raise HTTPException(status_code=410, detail="This share link has expired.")
    except (ValueError, KeyError):
        pass

    # Perform the actual upload
    result = await _do_upload(file=file, x_api_key=x_api_key)

    # Increment usage counter
    tokens[token]["uses"] = tokens[token].get("uses", 0) + 1
    _save_tokens(tokens)

    return result


@router.get("/share/list")
async def list_share_links():
    """List all created share links."""
    tokens = _load_tokens()
    links = []
    for token, info in tokens.items():
        links.append({
            "token": token,
            "created": info.get("created"),
            "expires": info.get("expires"),
            "uses": info.get("uses", 0),
            "active": info.get("active", True),
        })
    return {"links": links}
