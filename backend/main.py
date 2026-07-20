"""Silver — standalone REST API backend for the native mobile apps.

FastAPI over the same database layer and business logic (silver.services)
used by the web MVP, so web and mobile stay in sync.

Run:  uvicorn backend.main:app --host 0.0.0.0 --port 8000
"""
import os
import sys
import time
from pathlib import Path
from typing import Optional

import base64
import hashlib
import hmac
import json

from fastapi import (
    Depends, FastAPI, File, Header, HTTPException, UploadFile, WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from silver import ai, auth as auth_mod, db, services  # noqa: E402
from backend import streaming  # noqa: E402
from backend.push import push_to_user  # noqa: E402
from backend.realtime import manager  # noqa: E402

JWT_SECRET = os.environ.get("SILVER_JWT_SECRET", "dev-secret-change-me")
JWT_TTL = 30 * 24 * 3600

app = FastAPI(title="Silver API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Serve uploaded media files.
db.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(db.MEDIA_DIR)), name="media")

_boot = db.get_conn()
db.init_db(_boot)
auth_mod.ensure_admin(_boot)
_boot.close()


def get_db():
    conn = db.get_conn()
    try:
        yield conn
    finally:
        conn.close()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(user_id: int) -> str:
    """Compact HMAC-SHA256 signed token (JWT-style: payload.signature)."""
    payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + JWT_TTL}).encode())
    sig = _b64(hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def decode_token(token: str) -> dict:
    try:
        payload_b64, sig = token.split(".")
        expected = _b64(hmac.new(JWT_SECRET.encode(), payload_b64.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad signature")
        payload = json.loads(_unb64(payload_b64))
        if payload["exp"] < time.time():
            raise ValueError("expired")
        return payload
    except Exception:
        raise HTTPException(401, "invalid token")


def current_user(authorization: str = Header(default=""), conn=Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing token")
    payload = decode_token(authorization[7:])
    user = auth_mod.get_user(conn, int(payload["sub"]))
    if user is None or user["status"] != "active":
        raise HTTPException(403, "account unavailable")
    return user


def admin_user(user=Depends(current_user)):
    if user["role"] not in ("admin", "platform_mod"):
        raise HTTPException(403, "admin only")
    return user


class _Upload:
    """Adapter: FastAPI UploadFile → the interface services.save_upload expects."""
    def __init__(self, uf: UploadFile, data: bytes):
        self.name = uf.filename or "file.bin"
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


def row(r) -> Optional[dict]:
    return dict(r) if r is not None else None


def rows(rs) -> list[dict]:
    return [dict(r) for r in rs]


def media_urls(conn, post_id: int) -> list[dict]:
    out = []
    for m in services.post_media(conn, post_id):
        out.append({"kind": m["kind"], "url": f"/media/{Path(m['path']).name}"})
    return out


def post_payload(conn, p, viewer_id: int) -> dict:
    d = dict(p)
    d["media"] = media_urls(conn, p["id"])
    d["liked"] = services.user_liked(conn, viewer_id, p["id"])
    d["audiences"] = [r["audience"] for r in conn.execute(
        "SELECT audience FROM post_audiences WHERE post_id=?", (p["id"],)).fetchall()]
    return d


# ---------------------------------------------------------------- auth
class RegisterIn(BaseModel):
    username: str
    email: str
    password: str
    display_name: str


class LoginIn(BaseModel):
    identifier: str
    password: str


@app.post("/auth/register")
def register(body: RegisterIn, conn=Depends(get_db)):
    uid, err = auth_mod.register(conn, body.username, body.email, body.password, body.display_name)
    if uid is None:
        raise HTTPException(400, err)
    return {"token": make_token(uid), "user": row(auth_mod.get_user(conn, uid))}


@app.post("/auth/login")
def login(body: LoginIn, conn=Depends(get_db)):
    user, err = auth_mod.login(conn, body.identifier, body.password)
    if user is None:
        raise HTTPException(401, err)
    return {"token": make_token(user["id"]), "user": row(auth_mod.get_user(conn, user["id"]))}


# ---------------------------------------------------------------- me / profile
class ProfileIn(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    link: Optional[str] = None


class SettingsIn(BaseModel):
    language: Optional[str] = None
    who_can_message: Optional[str] = None
    show_like_counts: Optional[bool] = None
    notif_follows: Optional[bool] = None
    notif_likes: Optional[bool] = None
    notif_comments: Optional[bool] = None
    notif_messages: Optional[bool] = None
    notif_live: Optional[bool] = None


class InterestsIn(BaseModel):
    category_ids: list[int]


@app.get("/me")
def me(user=Depends(current_user), conn=Depends(get_db)):
    settings = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user["id"],)).fetchone()
    interests = [r["category_id"] for r in conn.execute(
        "SELECT category_id FROM user_interests WHERE user_id=?", (user["id"],)).fetchall()]
    return {"user": row(user), "settings": row(settings), "interests": interests}


@app.put("/me")
def update_me(body: ProfileIn, user=Depends(current_user), conn=Depends(get_db)):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE profiles SET {sets} WHERE user_id=?", (*fields.values(), user["id"]))
        conn.commit()
    return {"ok": True}


@app.put("/me/settings")
def update_settings(body: SettingsIn, user=Depends(current_user), conn=Depends(get_db)):
    fields = {k: (int(v) if isinstance(v, bool) else v)
              for k, v in body.model_dump().items() if v is not None}
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE user_settings SET {sets} WHERE user_id=?", (*fields.values(), user["id"]))
        conn.commit()
    return {"ok": True}


@app.put("/me/interests")
def set_interests(body: InterestsIn, user=Depends(current_user), conn=Depends(get_db)):
    conn.execute("DELETE FROM user_interests WHERE user_id=?", (user["id"],))
    for cid in body.category_ids:
        conn.execute("INSERT OR IGNORE INTO user_interests (user_id, category_id) VALUES (?,?)",
                     (user["id"], cid))
    conn.commit()
    return {"ok": True}


@app.get("/categories")
def get_categories(conn=Depends(get_db)):
    return rows(services.categories(conn))


# ---------------------------------------------------------------- media
@app.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(current_user)):
    data = await file.read()
    if len(data) > 200 * 1024 * 1024:
        raise HTTPException(413, "file too large")
    path = services.save_upload(user["id"], _Upload(file, data))
    return {"path": path, "url": f"/media/{Path(path).name}"}


# ---------------------------------------------------------------- posts & feeds
class PostIn(BaseModel):
    body: str = ""
    kind: str = "text"
    audiences: list[str] = ["front"]
    category_id: Optional[int] = None
    community_id: Optional[int] = None
    ai_generated: bool = False
    media_paths: list[str] = []


class CommentIn(BaseModel):
    body: str


@app.get("/feed/{section}")
def feed(section: str, user=Depends(current_user), conn=Depends(get_db)):
    loaders = {
        "circle": lambda: services.feed_circle(conn, user["id"]),
        "front": lambda: services.feed_front(conn, user["id"]),
        "interests": lambda: services.feed_interests(conn, user["id"]),
        "communities": lambda: services.feed_communities(conn, user["id"]),
        "nearby": lambda: services.feed_nearby(conn, user["id"], user["city"] or ""),
        "videos": lambda: services.short_videos(conn, user["id"]),
        "trending": lambda: services.trending_posts(conn, user["id"]),
    }
    if section not in loaders:
        raise HTTPException(404, "unknown section")
    return [post_payload(conn, p, user["id"]) for p in loaders[section]()]


@app.post("/posts")
def create_post(body: PostIn, user=Depends(current_user), conn=Depends(get_db)):
    if body.community_id and services.community_role(conn, body.community_id, user["id"]) is None:
        raise HTTPException(403, "not a member of the community")
    media_files = [{"path": p} for p in body.media_paths]
    pid = services.create_post(
        conn, user["id"], body.body, body.kind, body.audiences,
        category_id=body.category_id, community_id=body.community_id,
        city=user["city"] or "", ai_generated=body.ai_generated, media_files=media_files,
    )
    return post_payload(conn, services.get_post(conn, pid), user["id"])


@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int, user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.post_comments(conn, post_id))


@app.post("/posts/{post_id}/comments")
def comment(post_id: int, body: CommentIn, user=Depends(current_user), conn=Depends(get_db)):
    if services.get_post(conn, post_id) is None:
        raise HTTPException(404, "post not found")
    cid = services.add_comment(conn, post_id, user["id"], body.body)
    return {"id": cid}


@app.post("/posts/{post_id}/like")
def like(post_id: int, user=Depends(current_user), conn=Depends(get_db)):
    return {"liked": services.toggle_like(conn, user["id"], post_id)}


@app.post("/posts/{post_id}/save")
def save(post_id: int, user=Depends(current_user), conn=Depends(get_db)):
    return {"saved": services.toggle_save(conn, user["id"], post_id)}


@app.get("/saved")
def get_saved(user=Depends(current_user), conn=Depends(get_db)):
    return [post_payload(conn, p, user["id"]) for p in services.saved_posts(conn, user["id"])]


class SuggestIn(BaseModel):
    text: str


@app.post("/assistant/suggest")
def assistant_suggest(body: SuggestIn, user=Depends(current_user), conn=Depends(get_db)):
    return {
        "section": ai.suggest_section(body.text, False, user["city"] or ""),
        "category": ai.suggest_category(body.text),
        "keywords": ai.suggest_keywords(body.text),
        "title": ai.suggest_title(body.text),
        "warnings": ai.sensitive_warnings(body.text),
    }


# ---------------------------------------------------------------- stories
class StoryIn(BaseModel):
    body: str = ""
    audience: str = "circle"
    media_path: str = ""


@app.get("/stories")
def stories(user=Depends(current_user), conn=Depends(get_db)):
    out = []
    for s in services.visible_stories(conn, user["id"]):
        d = dict(s)
        m = services.story_media(conn, s["id"])
        d["media_url"] = f"/media/{Path(m['path']).name}" if m else None
        d["media_kind"] = m["kind"] if m else None
        out.append(d)
    return out


@app.post("/stories")
def create_story(body: StoryIn, user=Depends(current_user), conn=Depends(get_db)):
    sid = services.create_story(conn, user["id"], body.body, body.audience, body.media_path)
    return {"id": sid}


@app.post("/stories/{story_id}/view")
def view_story(story_id: int, user=Depends(current_user), conn=Depends(get_db)):
    services.mark_story_viewed(conn, story_id, user["id"])
    return {"views": services.story_view_count(conn, story_id)}


# ---------------------------------------------------------------- users / follows
@app.get("/users/search")
def user_search(q: str, user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.search_users(conn, user["id"], q))


@app.get("/users/suggested")
def user_suggested(user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.suggested_users(conn, user["id"]))


@app.get("/users/{user_id}")
def get_profile(user_id: int, user=Depends(current_user), conn=Depends(get_db)):
    target = auth_mod.get_user(conn, user_id)
    if target is None or target["status"] != "active":
        raise HTTPException(404, "user not found")
    fers, fing = services.follower_counts(conn, user_id)
    posts = services.user_posts(conn, user_id, user["id"])
    d = {k: target[k] for k in ("id", "username", "display_name", "bio", "city", "link",
                                "avatar_path", "is_private")}
    d.update({
        "followers": fers, "following": fing,
        "is_following": services.is_following(conn, user["id"], user_id),
        "is_friend": services.are_friends(conn, user["id"], user_id),
        "posts": [post_payload(conn, p, user["id"]) for p in posts],
    })
    return d


@app.post("/users/{user_id}/follow")
def follow(user_id: int, user=Depends(current_user), conn=Depends(get_db)):
    if services.is_following(conn, user["id"], user_id):
        services.unfollow(conn, user["id"], user_id)
        return {"following": False}
    services.follow(conn, user["id"], user_id)
    push_to_user(conn, user_id, "Silver", f"👤 {user['display_name']}")
    return {"following": True}


@app.post("/users/{user_id}/block")
def block(user_id: int, user=Depends(current_user), conn=Depends(get_db)):
    services.block(conn, user["id"], user_id)
    return {"ok": True}


@app.delete("/users/{user_id}/block")
def unblock(user_id: int, user=Depends(current_user), conn=Depends(get_db)):
    services.unblock(conn, user["id"], user_id)
    return {"ok": True}


# ---------------------------------------------------------------- messaging
class MessageIn(BaseModel):
    body: str = ""
    media_path: str = ""
    story_id: Optional[int] = None
    post_id: Optional[int] = None


class ConversationIn(BaseModel):
    user_id: int


@app.get("/conversations")
def conversations(requests: bool = False, user=Depends(current_user), conn=Depends(get_db)):
    out = []
    for c in services.user_conversations(conn, user["id"], requests=requests):
        d = dict(c)
        d["peer"] = row(services.conversation_peer(conn, c["id"], user["id"]))
        out.append(d)
    return out


@app.post("/conversations")
def open_conversation(body: ConversationIn, user=Depends(current_user), conn=Depends(get_db)):
    if not services.can_message(conn, user["id"], body.user_id):
        raise HTTPException(403, "cannot message this user")
    cid = services.get_or_create_direct(conn, user["id"], body.user_id)
    return {"id": cid}


@app.get("/conversations/{cid}/messages")
def get_messages(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    member = conn.execute(
        "SELECT 1 FROM conversation_members WHERE conversation_id=? AND user_id=?",
        (cid, user["id"])).fetchone()
    if member is None:
        raise HTTPException(403, "not a member")
    services.mark_conversation_read(conn, cid, user["id"])
    return rows(services.conversation_messages(conn, cid))


@app.post("/conversations/{cid}/messages")
async def post_message(cid: int, body: MessageIn, user=Depends(current_user), conn=Depends(get_db)):
    peer = services.conversation_peer(conn, cid, user["id"])
    if peer is None:
        raise HTTPException(403, "not a member")
    if not services.can_message(conn, user["id"], peer["id"]):
        raise HTTPException(403, "cannot message this user")
    mid = services.send_message(conn, cid, user["id"], body.body,
                                media_path=body.media_path,
                                story_id=body.story_id, post_id=body.post_id)
    # Realtime + push delivery to the recipient.
    await manager.send_to_user(peer["id"], {
        "type": "message", "conversation_id": cid, "message_id": mid,
        "from": user["display_name"],
    })
    push_to_user(conn, peer["id"], user["display_name"], body.body[:120] or "📎")
    return {"id": mid}


@app.post("/conversations/{cid}/accept")
def accept_conversation(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    services.accept_request(conn, cid)
    return {"ok": True}


# ---------------------------------------------------------------- communities
class CommunityIn(BaseModel):
    name: str
    description: str = ""
    kind: str = "public"
    category_id: Optional[int] = None


@app.get("/communities")
def communities(q: str = "", user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.list_communities(conn, q))


@app.get("/communities/mine")
def my_communities(user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.user_communities(conn, user["id"]))


@app.post("/communities")
def create_community(body: CommunityIn, user=Depends(current_user), conn=Depends(get_db)):
    cid = services.create_community(conn, user["id"], body.name, body.description,
                                    body.kind, body.category_id)
    return {"id": cid}


@app.post("/communities/{cid}/join")
def join_community(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    res = services.join_community(conn, cid, user["id"])
    if res == "missing":
        raise HTTPException(404, "community not found")
    return {"status": res}


@app.post("/communities/{cid}/leave")
def leave_community(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    services.leave_community(conn, cid, user["id"])
    return {"ok": True}


@app.get("/communities/{cid}/posts")
def community_posts(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    return [post_payload(conn, p, user["id"]) for p in services.community_posts(conn, cid)]


@app.get("/communities/{cid}")
def community_detail(cid: int, user=Depends(current_user), conn=Depends(get_db)):
    c = conn.execute("SELECT * FROM communities WHERE id=?", (cid,)).fetchone()
    if c is None:
        raise HTTPException(404, "community not found")
    d = dict(c)
    d["members"] = rows(services.community_members(conn, cid))
    d["my_role"] = services.community_role(conn, cid, user["id"])
    return d


# ---------------------------------------------------------------- live
class StreamIn(BaseModel):
    title: str
    description: str = ""
    category_id: Optional[int] = None
    comments_enabled: bool = True
    guests_enabled: bool = True
    save_recording: bool = True


class LiveCommentIn(BaseModel):
    body: str


class GuestActionIn(BaseModel):
    user_id: int
    status: str  # approved | rejected | removed


@app.get("/live")
def live_now(user=Depends(current_user), conn=Depends(get_db)):
    return rows(services.live_streams_now(conn))


@app.post("/live")
def start_live(body: StreamIn, user=Depends(current_user), conn=Depends(get_db)):
    sid = services.start_stream(conn, user["id"], body.title, body.description,
                                body.category_id, body.comments_enabled,
                                body.guests_enabled, body.save_recording)
    for f in conn.execute("SELECT follower_id FROM follows WHERE followee_id=?",
                          (user["id"],)).fetchall():
        push_to_user(conn, f["follower_id"], "📡 Silver",
                     f"{user['display_name']}: {body.title[:80]}")
    return {"id": sid}


@app.get("/live/{sid}")
def stream_detail(sid: int, user=Depends(current_user), conn=Depends(get_db)):
    s = services.get_stream(conn, sid)
    if s is None:
        raise HTTPException(404, "stream not found")
    if s["host_id"] != user["id"] and s["status"] == "live":
        services.join_stream(conn, sid, user["id"])
        s = services.get_stream(conn, sid)
    d = dict(s)
    d["comments"] = rows(services.stream_comments(conn, sid))
    d["guests"] = rows(services.stream_guests(conn, sid))
    return d


@app.post("/live/{sid}/comments")
async def live_comment(sid: int, body: LiveCommentIn, user=Depends(current_user), conn=Depends(get_db)):
    s = services.get_stream(conn, sid)
    if s is None or s["status"] != "live" or not s["comments_enabled"]:
        raise HTTPException(403, "comments unavailable")
    services.live_comment(conn, sid, user["id"], body.body)
    await manager.broadcast_stream(sid, {
        "type": "live_comment", "stream_id": sid,
        "display_name": user["display_name"], "body": body.body,
    })
    return {"ok": True}


@app.get("/live/{sid}/rtc-token")
def live_rtc_token(sid: int, user=Depends(current_user), conn=Depends(get_db)):
    """LiveKit join token for real A/V — host and approved guests can publish."""
    s = services.get_stream(conn, sid)
    if s is None:
        raise HTTPException(404, "stream not found")
    is_host = s["host_id"] == user["id"]
    approved = any(
        g["user_id"] == user["id"] and g["status"] == "approved"
        for g in services.stream_guests(conn, sid)
    )
    return streaming.rtc_token(
        sid, identity=f"user-{user['id']}", name=user["display_name"],
        is_host=is_host, can_publish=is_host or approved,
    )


@app.post("/live/{sid}/guest-request")
def guest_request(sid: int, user=Depends(current_user), conn=Depends(get_db)):
    s = services.get_stream(conn, sid)
    if s is None or not s["guests_enabled"]:
        raise HTTPException(403, "guests disabled")
    services.request_guest(conn, sid, user["id"])
    return {"ok": True}


@app.post("/live/{sid}/guest-action")
def guest_action(sid: int, body: GuestActionIn, user=Depends(current_user), conn=Depends(get_db)):
    s = services.get_stream(conn, sid)
    if s is None or s["host_id"] != user["id"]:
        raise HTTPException(403, "host only")
    services.set_guest_status(conn, sid, body.user_id, body.status)
    return {"ok": True}


@app.post("/live/{sid}/end")
def end_live(sid: int, keep_recording: bool = True, user=Depends(current_user), conn=Depends(get_db)):
    s = services.get_stream(conn, sid)
    if s is None or s["host_id"] != user["id"]:
        raise HTTPException(403, "host only")
    services.end_stream(conn, sid, keep_recording)
    return {"ok": True}


# ---------------------------------------------------------------- notifications
@app.get("/notifications")
def notifications(user=Depends(current_user), conn=Depends(get_db)):
    return {"unread": services.unread_count(conn, user["id"]),
            "items": rows(services.user_notifications(conn, user["id"]))}


@app.post("/notifications/read")
def notifications_read(user=Depends(current_user), conn=Depends(get_db)):
    services.mark_all_read(conn, user["id"])
    return {"ok": True}


# ---------------------------------------------------------------- reports
class ReportIn(BaseModel):
    target_kind: str
    target_id: int
    reason: str
    details: str = ""


@app.post("/reports")
def create_report(body: ReportIn, user=Depends(current_user), conn=Depends(get_db)):
    if body.reason not in services.REPORT_REASONS:
        raise HTTPException(400, "unknown reason")
    rid = services.create_report(conn, user["id"], body.target_kind, body.target_id,
                                 body.reason, body.details)
    return {"id": rid}


# ---------------------------------------------------------------- search / discover
@app.get("/search")
def search(q: str, user=Depends(current_user), conn=Depends(get_db)):
    return {
        "users": rows(services.search_users(conn, user["id"], q)),
        "posts": [post_payload(conn, p, user["id"]) for p in services.search_posts(conn, user["id"], q)],
        "communities": rows(services.list_communities(conn, q)),
    }


# ---------------------------------------------------------------- admin
class ResolveIn(BaseModel):
    action: str
    note: str = ""


@app.get("/admin/stats")
def admin_stats(user=Depends(admin_user), conn=Depends(get_db)):
    return services.admin_stats(conn)


@app.get("/admin/reports")
def admin_reports(user=Depends(admin_user), conn=Depends(get_db)):
    return rows(services.open_reports(conn))


@app.post("/admin/reports/{rid}/resolve")
def admin_resolve(rid: int, body: ResolveIn, user=Depends(admin_user), conn=Depends(get_db)):
    services.resolve_report(conn, rid, user["id"], body.action, body.note)
    return {"ok": True}


# ---------------------------------------------------------------- devices (push)
class DeviceIn(BaseModel):
    push_token: str
    platform: str = "unknown"


@app.post("/devices")
def register_device(body: DeviceIn, user=Depends(current_user), conn=Depends(get_db)):
    conn.execute(
        "INSERT OR IGNORE INTO devices (user_id, push_token, platform, created_at) VALUES (?,?,?,?)",
        (user["id"], body.push_token, body.platform, time.time()),
    )
    conn.commit()
    return {"ok": True}


# ---------------------------------------------------------------- websockets
def _ws_user(token: str):
    """Authenticate a websocket by token query param; returns user id or None."""
    try:
        payload = decode_token(token)
        return int(payload["sub"])
    except HTTPException:
        return None


@app.websocket("/ws")
async def ws_user(ws: WebSocket, token: str = ""):
    """Per-user channel: message/notification events are pushed here."""
    uid = _ws_user(token)
    if uid is None:
        await ws.close(code=4401)
        return
    await manager.connect_user(uid, ws)
    try:
        while True:
            await ws.receive_text()  # pings / keepalive from the client
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect_user(uid, ws)


@app.websocket("/ws/live/{stream_id}")
async def ws_live(ws: WebSocket, stream_id: int, token: str = ""):
    """Per-stream channel: live chat events are broadcast here."""
    uid = _ws_user(token)
    if uid is None:
        await ws.close(code=4401)
        return
    await manager.connect_stream(stream_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect_stream(stream_id, ws)


@app.get("/health")
def health():
    return {"status": "ok", "app": "silver-api",
            "livekit_configured": streaming.is_configured()}
