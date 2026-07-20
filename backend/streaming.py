"""Silver — live A/V transport via LiveKit (or compatible WebRTC SFU).

When LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET are set, the API
issues room access tokens so mobile/web clients can publish and subscribe
real audio/video for a stream. Without them the app still works — live
rooms fall back to chat + presence only.

LiveKit access tokens are standard HS256 JWTs signed with the API secret.
"""
import base64
import hashlib
import hmac
import json
import os
import time


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _jwt_hs256(payload: dict, secret: str) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64(json.dumps(payload).encode())
    signing_input = f"{header}.{body}".encode()
    sig = _b64(hmac.new(secret.encode(), signing_input, hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"


def is_configured() -> bool:
    return bool(
        os.environ.get("LIVEKIT_URL")
        and os.environ.get("LIVEKIT_API_KEY")
        and os.environ.get("LIVEKIT_API_SECRET")
    )


def rtc_token(stream_id: int, identity: str, name: str, is_host: bool,
              can_publish: bool) -> dict:
    """Build a LiveKit join token for the stream's room."""
    if not is_configured():
        return {"enabled": False}
    now = int(time.time())
    payload = {
        "iss": os.environ["LIVEKIT_API_KEY"],
        "sub": identity,
        "name": name,
        "nbf": now - 10,
        "exp": now + 4 * 3600,
        "video": {
            "room": f"silver-stream-{stream_id}",
            "roomJoin": True,
            "roomAdmin": is_host,
            "canPublish": can_publish,
            "canSubscribe": True,
        },
    }
    return {
        "enabled": True,
        "url": os.environ["LIVEKIT_URL"],
        "room": f"silver-stream-{stream_id}",
        "token": _jwt_hs256(payload, os.environ["LIVEKIT_API_SECRET"]),
    }
