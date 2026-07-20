"""Silver — Expo push notifications (best-effort, fire-and-forget).

Devices register their Expo push token via POST /devices; this module
delivers pushes through Expo's push API. Failures are swallowed — push
is an enhancement, never a blocker for the request path.
"""
import json
import threading
import urllib.request

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


def _deliver(messages: list[dict]) -> None:
    try:
        req = urllib.request.Request(
            EXPO_PUSH_URL,
            data=json.dumps(messages).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5).read()
    except Exception:
        pass  # best-effort only


def push_to_user(conn, user_id: int, title: str, body: str) -> None:
    """Send a push to all of a user's registered devices (async thread)."""
    rows = conn.execute(
        "SELECT push_token FROM devices WHERE user_id=?", (user_id,)
    ).fetchall()
    messages = [
        {"to": r["push_token"], "title": title, "body": body, "sound": "default"}
        for r in rows
        if r["push_token"].startswith("ExponentPushToken")
    ]
    if messages:
        threading.Thread(target=_deliver, args=(messages,), daemon=True).start()
