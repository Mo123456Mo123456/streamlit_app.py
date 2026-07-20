"""Silver — business logic on top of the database layer.

All functions take an sqlite3 connection as first argument so the same code
path is used by the app, the tests and the admin panel.
"""
import sqlite3
import time
import uuid
from pathlib import Path

from . import db

STORY_TTL = 24 * 3600
REPORT_REASONS = [
    "reason_abuse", "reason_impersonation", "reason_fraud", "reason_violence",
    "reason_sexual", "reason_hate", "reason_misinfo", "reason_privacy",
    "reason_ip", "reason_child", "reason_spam", "reason_other",
]


# ---------------------------------------------------------------- helpers
def _now() -> float:
    return time.time()


def save_upload(owner_id: int, uploaded_file) -> str:
    """Persist a Streamlit UploadedFile under data/media/, return relative path."""
    db.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(uploaded_file.name).suffix.lower()[:10] or ".bin"
    fname = f"{owner_id}_{uuid.uuid4().hex}{ext}"
    dest = db.MEDIA_DIR / fname
    dest.write_bytes(uploaded_file.getvalue())
    return str(dest)


def audit(conn, actor_id, action: str, detail: str = "") -> None:
    conn.execute(
        "INSERT INTO audit_logs (actor_id, action, detail, created_at) VALUES (?,?,?,?)",
        (actor_id, action, detail, _now()),
    )


# ---------------------------------------------------------------- follows / blocks
def follow(conn, follower_id: int, followee_id: int) -> None:
    if follower_id == followee_id:
        return
    conn.execute(
        "INSERT OR IGNORE INTO follows (follower_id, followee_id, created_at) VALUES (?,?,?)",
        (follower_id, followee_id, _now()),
    )
    notify(conn, followee_id, "follow", actor_id=follower_id)
    conn.commit()


def unfollow(conn, follower_id: int, followee_id: int) -> None:
    conn.execute("DELETE FROM follows WHERE follower_id=? AND followee_id=?", (follower_id, followee_id))
    conn.commit()


def is_following(conn, follower_id: int, followee_id: int) -> bool:
    return conn.execute(
        "SELECT 1 FROM follows WHERE follower_id=? AND followee_id=?", (follower_id, followee_id)
    ).fetchone() is not None


def are_friends(conn, a: int, b: int) -> bool:
    """Friends = mutual follow."""
    return is_following(conn, a, b) and is_following(conn, b, a)


def follower_counts(conn, user_id: int) -> tuple[int, int]:
    fers = conn.execute("SELECT COUNT(*) c FROM follows WHERE followee_id=?", (user_id,)).fetchone()["c"]
    fing = conn.execute("SELECT COUNT(*) c FROM follows WHERE follower_id=?", (user_id,)).fetchone()["c"]
    return fers, fing


def block(conn, blocker_id: int, blocked_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO blocks (blocker_id, blocked_id, created_at) VALUES (?,?,?)",
        (blocker_id, blocked_id, _now()),
    )
    conn.execute("DELETE FROM follows WHERE follower_id=? AND followee_id=?", (blocker_id, blocked_id))
    conn.execute("DELETE FROM follows WHERE follower_id=? AND followee_id=?", (blocked_id, blocker_id))
    conn.commit()


def unblock(conn, blocker_id: int, blocked_id: int) -> None:
    conn.execute("DELETE FROM blocks WHERE blocker_id=? AND blocked_id=?", (blocker_id, blocked_id))
    conn.commit()


def is_blocked_between(conn, a: int, b: int) -> bool:
    return conn.execute(
        "SELECT 1 FROM blocks WHERE (blocker_id=? AND blocked_id=?) OR (blocker_id=? AND blocked_id=?)",
        (a, b, b, a),
    ).fetchone() is not None


def blocked_ids(conn, user_id: int) -> set[int]:
    rows = conn.execute(
        "SELECT blocked_id AS other FROM blocks WHERE blocker_id=? "
        "UNION SELECT blocker_id FROM blocks WHERE blocked_id=?",
        (user_id, user_id),
    ).fetchall()
    return {r["other"] for r in rows}


# ---------------------------------------------------------------- posts
def create_post(conn, author_id: int, body: str, kind: str, audiences: list[str],
                category_id=None, community_id=None, city: str = "",
                ai_generated: bool = False, media_files=None,
                variant_public: str = "", variant_private: str = "") -> int:
    cur = conn.execute(
        "INSERT INTO posts (author_id, kind, body, category_id, community_id, city, ai_generated, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (author_id, kind, body, category_id, community_id, city, int(ai_generated), _now()),
    )
    pid = cur.lastrowid
    for aud in set(audiences or ["front"]):
        conn.execute("INSERT OR IGNORE INTO post_audiences (post_id, audience) VALUES (?,?)", (pid, aud))
    if variant_public:
        conn.execute("INSERT INTO post_variants (post_id, variant, body) VALUES (?,?,?)", (pid, "public", variant_public))
    if variant_private:
        conn.execute("INSERT INTO post_variants (post_id, variant, body) VALUES (?,?,?)", (pid, "private", variant_private))
    for mf in media_files or []:
        mkind = "video" if mf["path"].lower().endswith((".mp4", ".mov", ".webm", ".m4v")) else "image"
        conn.execute(
            "INSERT INTO media (owner_id, post_id, kind, path, created_at) VALUES (?,?,?,?,?)",
            (author_id, pid, mf.get("kind", mkind), mf["path"], _now()),
        )
    conn.commit()
    return pid


_POST_SELECT = (
    "SELECT p.*, pr.display_name, u.username, "
    "(SELECT COUNT(*) FROM reactions r WHERE r.post_id=p.id) AS likes, "
    "(SELECT COUNT(*) FROM comments c WHERE c.post_id=p.id AND c.hidden=0) AS comment_count "
    "FROM posts p JOIN users u ON u.id=p.author_id JOIN profiles pr ON pr.user_id=p.author_id "
    "WHERE p.hidden=0 AND u.status='active' "
)


def _exclude(user_id: int, excluded: set[int]) -> str:
    if not excluded:
        return ""
    ids = ",".join(str(i) for i in excluded)
    return f" AND p.author_id NOT IN ({ids}) "


def feed_circle(conn, user_id: int, limit=30):
    """Posts targeted at 'circle' from mutual follows + own."""
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id AND a.audience='circle') "
        "AND (p.author_id=? OR (p.author_id IN (SELECT followee_id FROM follows WHERE follower_id=?) "
        "     AND p.author_id IN (SELECT follower_id FROM follows WHERE followee_id=?))) "
        "ORDER BY p.created_at DESC LIMIT ?",
        (user_id, user_id, user_id, limit),
    ).fetchall()


def feed_front(conn, user_id: int, limit=30):
    """Public 'front' posts from followed accounts + own."""
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id AND a.audience='front') "
        "AND (p.author_id=? OR p.author_id IN (SELECT followee_id FROM follows WHERE follower_id=?)) "
        "ORDER BY p.created_at DESC LIMIT ?",
        (user_id, user_id, limit),
    ).fetchall()


def feed_interests(conn, user_id: int, limit=30):
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id AND a.audience IN ('interests','front')) "
        "AND p.category_id IN (SELECT category_id FROM user_interests WHERE user_id=?) "
        "ORDER BY p.created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def feed_communities(conn, user_id: int, limit=30):
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND p.community_id IN (SELECT community_id FROM community_members WHERE user_id=? AND status='active') "
        "ORDER BY p.created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def feed_nearby(conn, user_id: int, city: str, limit=30):
    if not city:
        return []
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id AND a.audience IN ('nearby','front')) "
        "AND LOWER(p.city)=LOWER(?) AND p.author_id != ? "
        "ORDER BY p.created_at DESC LIMIT ?",
        (city, user_id, limit),
    ).fetchall()


def user_posts(conn, author_id: int, viewer_id: int, limit=50):
    """Posts on a profile: own = everything; friends see circle; others see front."""
    if viewer_id == author_id:
        cond = "1=1"
    elif are_friends(conn, viewer_id, author_id):
        cond = ("EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id "
                "AND a.audience IN ('front','circle','interests','nearby'))")
    else:
        cond = ("EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id "
                "AND a.audience IN ('front','interests','nearby'))")
    return conn.execute(
        _POST_SELECT + f"AND p.author_id=? AND {cond} ORDER BY p.created_at DESC LIMIT ?",
        (author_id, limit),
    ).fetchall()


def short_videos(conn, user_id: int, limit=30):
    ex = _exclude(user_id, blocked_ids(conn, user_id))
    return conn.execute(
        _POST_SELECT + ex + "AND p.kind IN ('short_video','video') ORDER BY "
        "(p.category_id IN (SELECT category_id FROM user_interests WHERE user_id=?)) DESC, "
        "likes DESC, p.created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def post_media(conn, post_id: int):
    return conn.execute("SELECT * FROM media WHERE post_id=?", (post_id,)).fetchall()


def get_post(conn, post_id: int):
    return conn.execute(_POST_SELECT + "AND p.id=?", (post_id,)).fetchone()


def toggle_like(conn, user_id: int, post_id: int) -> bool:
    existing = conn.execute(
        "SELECT 1 FROM reactions WHERE user_id=? AND post_id=?", (user_id, post_id)
    ).fetchone()
    if existing:
        conn.execute("DELETE FROM reactions WHERE user_id=? AND post_id=?", (user_id, post_id))
        conn.commit()
        return False
    conn.execute(
        "INSERT INTO reactions (user_id, post_id, kind, created_at) VALUES (?,?,?,?)",
        (user_id, post_id, "like", _now()),
    )
    post = conn.execute("SELECT author_id FROM posts WHERE id=?", (post_id,)).fetchone()
    if post and post["author_id"] != user_id:
        notify(conn, post["author_id"], "like", actor_id=user_id, ref_id=post_id)
    conn.commit()
    return True


def user_liked(conn, user_id: int, post_id: int) -> bool:
    return conn.execute("SELECT 1 FROM reactions WHERE user_id=? AND post_id=?", (user_id, post_id)).fetchone() is not None


def toggle_save(conn, user_id: int, post_id: int) -> bool:
    if conn.execute("SELECT 1 FROM saved_posts WHERE user_id=? AND post_id=?", (user_id, post_id)).fetchone():
        conn.execute("DELETE FROM saved_posts WHERE user_id=? AND post_id=?", (user_id, post_id))
        conn.commit()
        return False
    conn.execute("INSERT INTO saved_posts (user_id, post_id, created_at) VALUES (?,?,?)", (user_id, post_id, _now()))
    conn.commit()
    return True


def saved_posts(conn, user_id: int, limit=50):
    return conn.execute(
        _POST_SELECT + "AND p.id IN (SELECT post_id FROM saved_posts WHERE user_id=?) "
        "ORDER BY p.created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def add_comment(conn, post_id: int, author_id: int, body: str, parent_id=None) -> int:
    cur = conn.execute(
        "INSERT INTO comments (post_id, author_id, parent_id, body, created_at) VALUES (?,?,?,?,?)",
        (post_id, author_id, parent_id, body, _now()),
    )
    post = conn.execute("SELECT author_id FROM posts WHERE id=?", (post_id,)).fetchone()
    if post and post["author_id"] != author_id:
        notify(conn, post["author_id"], "comment", actor_id=author_id, ref_id=post_id, body=body[:80])
    conn.commit()
    return cur.lastrowid


def post_comments(conn, post_id: int):
    return conn.execute(
        "SELECT c.*, pr.display_name, u.username FROM comments c "
        "JOIN users u ON u.id=c.author_id JOIN profiles pr ON pr.user_id=c.author_id "
        "WHERE c.post_id=? AND c.hidden=0 ORDER BY c.created_at",
        (post_id,),
    ).fetchall()


# ---------------------------------------------------------------- stories
def create_story(conn, author_id: int, body: str, audience: str, media_path: str = "") -> int:
    now = _now()
    cur = conn.execute(
        "INSERT INTO stories (author_id, body, audience, created_at, expires_at) VALUES (?,?,?,?,?)",
        (author_id, body, audience, now, now + STORY_TTL),
    )
    sid = cur.lastrowid
    if media_path:
        kind = "video" if media_path.lower().endswith((".mp4", ".mov", ".webm")) else "image"
        conn.execute(
            "INSERT INTO media (owner_id, story_id, kind, path, created_at) VALUES (?,?,?,?,?)",
            (author_id, sid, kind, media_path, now),
        )
    conn.commit()
    return sid


def visible_stories(conn, viewer_id: int):
    """Active stories the viewer may see, grouped by author, with seen flag."""
    now = _now()
    ex = blocked_ids(conn, viewer_id)
    rows = conn.execute(
        "SELECT s.*, pr.display_name, u.username, "
        "EXISTS(SELECT 1 FROM story_views v WHERE v.story_id=s.id AND v.viewer_id=?) AS seen "
        "FROM stories s JOIN users u ON u.id=s.author_id JOIN profiles pr ON pr.user_id=s.author_id "
        "WHERE s.expires_at > ? AND u.status='active' ORDER BY s.created_at DESC",
        (viewer_id, now),
    ).fetchall()
    out = []
    for s in rows:
        a = s["author_id"]
        if a in ex:
            continue
        if a == viewer_id:
            out.append(s)
        elif s["audience"] == "public":
            out.append(s)
        elif s["audience"] == "followers" and is_following(conn, viewer_id, a):
            out.append(s)
        elif s["audience"] == "circle" and are_friends(conn, viewer_id, a):
            out.append(s)
    return out


def mark_story_viewed(conn, story_id: int, viewer_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO story_views (story_id, viewer_id, viewed_at) VALUES (?,?,?)",
        (story_id, viewer_id, _now()),
    )
    conn.commit()


def story_media(conn, story_id: int):
    return conn.execute("SELECT * FROM media WHERE story_id=?", (story_id,)).fetchone()


def story_view_count(conn, story_id: int) -> int:
    return conn.execute("SELECT COUNT(*) c FROM story_views WHERE story_id=?", (story_id,)).fetchone()["c"]


def feature_story(conn, story_id: int) -> None:
    conn.execute("UPDATE stories SET featured=1 WHERE id=?", (story_id,))
    conn.commit()


def featured_stories(conn, author_id: int):
    return conn.execute(
        "SELECT * FROM stories WHERE author_id=? AND featured=1 ORDER BY created_at DESC", (author_id,)
    ).fetchall()


# ---------------------------------------------------------------- messaging
def can_message(conn, sender_id: int, recipient_id: int) -> bool:
    if sender_id == recipient_id or is_blocked_between(conn, sender_id, recipient_id):
        return False
    setting = conn.execute(
        "SELECT who_can_message FROM user_settings WHERE user_id=?", (recipient_id,)
    ).fetchone()
    pref = setting["who_can_message"] if setting else "everyone"
    if pref == "nobody":
        return False
    if pref == "friends":
        return are_friends(conn, sender_id, recipient_id)
    if pref == "followers":
        return is_following(conn, recipient_id, sender_id)  # recipient follows sender
    return True


def get_or_create_direct(conn, a: int, b: int) -> int:
    row = conn.execute(
        "SELECT c.id FROM conversations c "
        "JOIN conversation_members m1 ON m1.conversation_id=c.id AND m1.user_id=? "
        "JOIN conversation_members m2 ON m2.conversation_id=c.id AND m2.user_id=? "
        "WHERE c.kind='direct'",
        (a, b),
    ).fetchone()
    if row:
        return row["id"]
    # Message request when the recipient doesn't follow the sender.
    is_request = 0 if is_following(conn, b, a) else 1
    cur = conn.execute(
        "INSERT INTO conversations (kind, is_request, created_at) VALUES ('direct',?,?)",
        (is_request, _now()),
    )
    cid = cur.lastrowid
    conn.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (?,?)", (cid, a))
    conn.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (?,?)", (cid, b))
    conn.commit()
    return cid


def send_message(conn, conversation_id: int, sender_id: int, body: str,
                 media_path: str = "", reply_to_id=None, story_id=None, post_id=None) -> int:
    cur = conn.execute(
        "INSERT INTO messages (conversation_id, sender_id, body, media_path, reply_to_id, story_id, post_id, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (conversation_id, sender_id, body, media_path, reply_to_id, story_id, post_id, _now()),
    )
    others = conn.execute(
        "SELECT user_id FROM conversation_members WHERE conversation_id=? AND user_id!=?",
        (conversation_id, sender_id),
    ).fetchall()
    for o in others:
        notify(conn, o["user_id"], "message", actor_id=sender_id, ref_id=conversation_id, body=body[:80])
    conn.commit()
    return cur.lastrowid


def user_conversations(conn, user_id: int, requests: bool = False):
    return conn.execute(
        "SELECT c.*, m.pinned, m.muted, m.last_read_at, "
        "(SELECT body FROM messages WHERE conversation_id=c.id AND deleted=0 ORDER BY created_at DESC LIMIT 1) AS last_body, "
        "(SELECT created_at FROM messages WHERE conversation_id=c.id ORDER BY created_at DESC LIMIT 1) AS last_at, "
        "(SELECT COUNT(*) FROM messages ms WHERE ms.conversation_id=c.id AND ms.created_at > m.last_read_at AND ms.sender_id != ?) AS unread "
        "FROM conversations c JOIN conversation_members m ON m.conversation_id=c.id "
        "WHERE m.user_id=? AND m.archived=0 AND c.is_request=? "
        "ORDER BY m.pinned DESC, last_at DESC",
        (user_id, user_id, int(requests)),
    ).fetchall()


def conversation_peer(conn, conversation_id: int, user_id: int):
    return conn.execute(
        "SELECT u.id, u.username, pr.display_name FROM conversation_members m "
        "JOIN users u ON u.id=m.user_id JOIN profiles pr ON pr.user_id=u.id "
        "WHERE m.conversation_id=? AND m.user_id!=? LIMIT 1",
        (conversation_id, user_id),
    ).fetchone()


def conversation_messages(conn, conversation_id: int, limit=100):
    return conn.execute(
        "SELECT m.*, pr.display_name FROM messages m JOIN profiles pr ON pr.user_id=m.sender_id "
        "WHERE m.conversation_id=? AND m.deleted=0 ORDER BY m.created_at LIMIT ?",
        (conversation_id, limit),
    ).fetchall()


def mark_conversation_read(conn, conversation_id: int, user_id: int) -> None:
    conn.execute(
        "UPDATE conversation_members SET last_read_at=? WHERE conversation_id=? AND user_id=?",
        (_now(), conversation_id, user_id),
    )
    conn.commit()


def accept_request(conn, conversation_id: int) -> None:
    conn.execute("UPDATE conversations SET is_request=0 WHERE id=?", (conversation_id,))
    conn.commit()


def delete_message(conn, message_id: int, user_id: int) -> None:
    conn.execute("UPDATE messages SET deleted=1 WHERE id=? AND sender_id=?", (message_id, user_id))
    conn.commit()


# ---------------------------------------------------------------- communities
def create_community(conn, owner_id: int, name: str, description: str, kind: str, category_id=None) -> int:
    cur = conn.execute(
        "INSERT INTO communities (name, description, kind, category_id, owner_id, created_at) VALUES (?,?,?,?,?,?)",
        (name, description, kind, category_id, owner_id, _now()),
    )
    cid = cur.lastrowid
    conn.execute(
        "INSERT INTO community_members (community_id, user_id, role, status, joined_at) VALUES (?,?,?,?,?)",
        (cid, owner_id, "owner", "active", _now()),
    )
    conn.commit()
    return cid


def join_community(conn, community_id: int, user_id: int) -> str:
    c = conn.execute("SELECT * FROM communities WHERE id=?", (community_id,)).fetchone()
    if c is None:
        return "missing"
    status = "active" if c["kind"] == "public" else "pending"
    if c["kind"] == "invite":
        return "invite_only"
    conn.execute(
        "INSERT OR IGNORE INTO community_members (community_id, user_id, role, status, joined_at) VALUES (?,?,?,?,?)",
        (community_id, user_id, "member", status, _now()),
    )
    conn.commit()
    return status


def leave_community(conn, community_id: int, user_id: int) -> None:
    conn.execute("DELETE FROM community_members WHERE community_id=? AND user_id=? AND role!='owner'",
                 (community_id, user_id))
    conn.commit()


def community_role(conn, community_id: int, user_id: int) -> str | None:
    r = conn.execute(
        "SELECT role, status FROM community_members WHERE community_id=? AND user_id=?",
        (community_id, user_id),
    ).fetchone()
    if r is None or r["status"] != "active":
        return None
    return r["role"]


def community_members(conn, community_id: int, status="active"):
    return conn.execute(
        "SELECT cm.*, u.username, pr.display_name FROM community_members cm "
        "JOIN users u ON u.id=cm.user_id JOIN profiles pr ON pr.user_id=cm.user_id "
        "WHERE cm.community_id=? AND cm.status=? ORDER BY cm.joined_at",
        (community_id, status),
    ).fetchall()


def approve_member(conn, community_id: int, user_id: int) -> None:
    conn.execute(
        "UPDATE community_members SET status='active' WHERE community_id=? AND user_id=?",
        (community_id, user_id),
    )
    notify(conn, user_id, "community", ref_id=community_id)
    conn.commit()


def user_communities(conn, user_id: int):
    return conn.execute(
        "SELECT c.*, cm.role FROM communities c JOIN community_members cm ON cm.community_id=c.id "
        "WHERE cm.user_id=? AND cm.status='active' ORDER BY c.name",
        (user_id,),
    ).fetchall()


def list_communities(conn, query: str = "", limit=30):
    q = f"%{query}%"
    return conn.execute(
        "SELECT c.*, (SELECT COUNT(*) FROM community_members m WHERE m.community_id=c.id AND m.status='active') AS member_count "
        "FROM communities c WHERE c.name LIKE ? OR c.description LIKE ? ORDER BY member_count DESC LIMIT ?",
        (q, q, limit),
    ).fetchall()


def community_posts(conn, community_id: int, limit=50):
    return conn.execute(
        _POST_SELECT + "AND p.community_id=? ORDER BY p.created_at DESC LIMIT ?",
        (community_id, limit),
    ).fetchall()


# ---------------------------------------------------------------- live streams
def start_stream(conn, host_id: int, title: str, description: str, category_id=None,
                 comments_enabled=True, guests_enabled=True, save_recording=True,
                 cover_path: str = "") -> int:
    cur = conn.execute(
        "INSERT INTO live_streams (host_id, title, description, category_id, cover_path, "
        "comments_enabled, guests_enabled, save_recording, started_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (host_id, title, description, category_id, cover_path,
         int(comments_enabled), int(guests_enabled), int(save_recording), _now()),
    )
    sid = cur.lastrowid
    followers = conn.execute("SELECT follower_id FROM follows WHERE followee_id=?", (host_id,)).fetchall()
    for f in followers:
        notify(conn, f["follower_id"], "live", actor_id=host_id, ref_id=sid)
    conn.commit()
    return sid


def live_streams_now(conn, limit=20):
    return conn.execute(
        "SELECT s.*, pr.display_name, u.username, "
        "(SELECT COUNT(*) FROM live_viewers v WHERE v.stream_id=s.id) AS viewer_count "
        "FROM live_streams s JOIN users u ON u.id=s.host_id JOIN profiles pr ON pr.user_id=s.host_id "
        "WHERE s.status='live' AND u.status='active' ORDER BY s.started_at DESC LIMIT ?",
        (limit,),
    ).fetchall()


def get_stream(conn, stream_id: int):
    return conn.execute(
        "SELECT s.*, pr.display_name, u.username, "
        "(SELECT COUNT(*) FROM live_viewers v WHERE v.stream_id=s.id) AS viewer_count "
        "FROM live_streams s JOIN users u ON u.id=s.host_id JOIN profiles pr ON pr.user_id=s.host_id "
        "WHERE s.id=?",
        (stream_id,),
    ).fetchone()


def join_stream(conn, stream_id: int, user_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO live_viewers (stream_id, user_id, joined_at) VALUES (?,?,?)",
        (stream_id, user_id, _now()),
    )
    conn.commit()


def live_comment(conn, stream_id: int, author_id: int, body: str) -> None:
    conn.execute(
        "INSERT INTO live_comments (stream_id, author_id, body, created_at) VALUES (?,?,?,?)",
        (stream_id, author_id, body, _now()),
    )
    conn.commit()


def stream_comments(conn, stream_id: int, limit=100):
    return conn.execute(
        "SELECT lc.*, pr.display_name FROM live_comments lc "
        "JOIN profiles pr ON pr.user_id=lc.author_id "
        "WHERE lc.stream_id=? AND lc.hidden=0 ORDER BY lc.pinned DESC, lc.created_at DESC LIMIT ?",
        (stream_id, limit),
    ).fetchall()


def request_guest(conn, stream_id: int, user_id: int) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO live_guests (stream_id, user_id, status, requested_at) VALUES (?,?,'requested',?)",
        (stream_id, user_id, _now()),
    )
    conn.commit()


def set_guest_status(conn, stream_id: int, user_id: int, status: str) -> None:
    conn.execute("UPDATE live_guests SET status=? WHERE stream_id=? AND user_id=?", (status, stream_id, user_id))
    if status == "approved":
        notify(conn, user_id, "live", ref_id=stream_id, body="guest_approved")
    conn.commit()


def stream_guests(conn, stream_id: int, status=None):
    if status:
        return conn.execute(
            "SELECT g.*, pr.display_name FROM live_guests g JOIN profiles pr ON pr.user_id=g.user_id "
            "WHERE g.stream_id=? AND g.status=?", (stream_id, status)).fetchall()
    return conn.execute(
        "SELECT g.*, pr.display_name FROM live_guests g JOIN profiles pr ON pr.user_id=g.user_id "
        "WHERE g.stream_id=?", (stream_id,)).fetchall()


def end_stream(conn, stream_id: int, keep_recording: bool) -> None:
    conn.execute(
        "UPDATE live_streams SET status='ended', ended_at=?, save_recording=? WHERE id=?",
        (_now(), int(keep_recording), stream_id),
    )
    conn.commit()


def saved_streams(conn, host_id: int):
    return conn.execute(
        "SELECT * FROM live_streams WHERE host_id=? AND status='ended' AND save_recording=1 "
        "ORDER BY started_at DESC",
        (host_id,),
    ).fetchall()


# ---------------------------------------------------------------- notifications
def notify(conn, user_id: int, kind: str, actor_id=None, ref_id=None, body: str = "") -> None:
    prefs = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    if prefs:
        gate = {
            "follow": prefs["notif_follows"], "like": prefs["notif_likes"],
            "comment": prefs["notif_comments"], "message": prefs["notif_messages"],
            "live": prefs["notif_live"],
        }.get(kind, 1)
        if not gate:
            return
    conn.execute(
        "INSERT INTO notifications (user_id, kind, actor_id, ref_id, body, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, kind, actor_id, ref_id, body, _now()),
    )


def user_notifications(conn, user_id: int, limit=50):
    return conn.execute(
        "SELECT n.*, pr.display_name AS actor_name FROM notifications n "
        "LEFT JOIN profiles pr ON pr.user_id=n.actor_id "
        "WHERE n.user_id=? ORDER BY n.created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def unread_count(conn, user_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) c FROM notifications WHERE user_id=? AND read=0", (user_id,)
    ).fetchone()["c"]


def mark_all_read(conn, user_id: int) -> None:
    conn.execute("UPDATE notifications SET read=1 WHERE user_id=?", (user_id,))
    conn.commit()


# ---------------------------------------------------------------- search
def search_users(conn, viewer_id: int, query: str, limit=20):
    q = f"%{query}%"
    ex = blocked_ids(conn, viewer_id)
    rows = conn.execute(
        "SELECT u.id, u.username, pr.display_name, pr.bio, pr.city FROM users u "
        "JOIN profiles pr ON pr.user_id=u.id "
        "WHERE u.status='active' AND (u.username LIKE ? OR pr.display_name LIKE ?) LIMIT ?",
        (q, q, limit),
    ).fetchall()
    return [r for r in rows if r["id"] not in ex]


def search_posts(conn, viewer_id: int, query: str, limit=20):
    q = f"%{query}%"
    ex = _exclude(viewer_id, blocked_ids(conn, viewer_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND p.body LIKE ? AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id "
        "AND a.audience IN ('front','interests','nearby')) ORDER BY p.created_at DESC LIMIT ?",
        (q, limit),
    ).fetchall()


def suggested_users(conn, user_id: int, limit=10):
    ex = blocked_ids(conn, user_id) | {user_id}
    rows = conn.execute(
        "SELECT u.id, u.username, pr.display_name, pr.city, "
        "(SELECT COUNT(*) FROM follows f WHERE f.followee_id=u.id) AS followers "
        "FROM users u JOIN profiles pr ON pr.user_id=u.id "
        "WHERE u.status='active' AND u.id NOT IN (SELECT followee_id FROM follows WHERE follower_id=?) "
        "ORDER BY followers DESC LIMIT ?",
        (user_id, limit + len(ex)),
    ).fetchall()
    return [r for r in rows if r["id"] not in ex][:limit]


def trending_posts(conn, viewer_id: int, limit=15):
    ex = _exclude(viewer_id, blocked_ids(conn, viewer_id))
    return conn.execute(
        _POST_SELECT + ex +
        "AND EXISTS (SELECT 1 FROM post_audiences a WHERE a.post_id=p.id AND a.audience IN ('front','interests','nearby')) "
        "ORDER BY likes DESC, comment_count DESC, p.created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()


# ---------------------------------------------------------------- reports & moderation
def create_report(conn, reporter_id: int, target_kind: str, target_id: int,
                  reason: str, details: str = "") -> int:
    cur = conn.execute(
        "INSERT INTO reports (reporter_id, target_kind, target_id, reason, details, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (reporter_id, target_kind, target_id, reason, details, _now()),
    )
    conn.commit()
    return cur.lastrowid


def open_reports(conn):
    return conn.execute(
        "SELECT r.*, pr.display_name AS reporter_name FROM reports r "
        "JOIN profiles pr ON pr.user_id=r.reporter_id "
        "WHERE r.status='open' ORDER BY r.created_at",
    ).fetchall()


def resolve_report(conn, report_id: int, moderator_id: int, action: str, note: str = "") -> None:
    report = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    if report is None:
        return
    status = "dismissed" if action == "dismiss_report" else "resolved"
    if action == "hide_post" and report["target_kind"] == "post":
        conn.execute("UPDATE posts SET hidden=1 WHERE id=?", (report["target_id"],))
    elif action == "hide_comment" and report["target_kind"] == "comment":
        conn.execute("UPDATE comments SET hidden=1 WHERE id=?", (report["target_id"],))
    elif action == "suspend_user":
        uid = _report_target_user(conn, report)
        if uid:
            conn.execute("UPDATE users SET status='suspended' WHERE id=?", (uid,))
    elif action == "close_account":
        uid = _report_target_user(conn, report)
        if uid:
            conn.execute("UPDATE users SET status='closed' WHERE id=?", (uid,))
    elif action == "warn_user":
        uid = _report_target_user(conn, report)
        if uid:
            notify(conn, uid, "security", body="warning")
    conn.execute(
        "UPDATE reports SET status=?, resolved_by=?, resolved_at=? WHERE id=?",
        (status, moderator_id, _now(), report_id),
    )
    conn.execute(
        "INSERT INTO moderation_actions (moderator_id, action, target_kind, target_id, note, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (moderator_id, action, report["target_kind"], report["target_id"], note, _now()),
    )
    audit(conn, moderator_id, action, f"report #{report_id} ({report['target_kind']} {report['target_id']})")
    if status == "resolved":
        notify(conn, report["reporter_id"], "report", ref_id=report_id)
    conn.commit()


def _report_target_user(conn, report) -> int | None:
    kind, tid = report["target_kind"], report["target_id"]
    if kind == "user":
        return tid
    if kind == "post":
        r = conn.execute("SELECT author_id a FROM posts WHERE id=?", (tid,)).fetchone()
    elif kind == "comment":
        r = conn.execute("SELECT author_id a FROM comments WHERE id=?", (tid,)).fetchone()
    elif kind == "stream":
        r = conn.execute("SELECT host_id a FROM live_streams WHERE id=?", (tid,)).fetchone()
    elif kind == "message":
        r = conn.execute("SELECT sender_id a FROM messages WHERE id=?", (tid,)).fetchone()
    else:
        r = None
    return r["a"] if r else None


# ---------------------------------------------------------------- admin stats
def admin_stats(conn) -> dict:
    week_ago = _now() - 7 * 86400
    def one(sql, *args):
        return conn.execute(sql, args).fetchone()[0]
    return {
        "users": one("SELECT COUNT(*) FROM users"),
        "active_users": one("SELECT COUNT(*) FROM users WHERE last_login_at > ?", week_ago),
        "posts": one("SELECT COUNT(*) FROM posts"),
        "videos": one("SELECT COUNT(*) FROM posts WHERE kind IN ('video','short_video')"),
        "streams": one("SELECT COUNT(*) FROM live_streams"),
        "messages": one("SELECT COUNT(*) FROM messages"),
        "open_reports": one("SELECT COUNT(*) FROM reports WHERE status='open'"),
        "suspended": one("SELECT COUNT(*) FROM users WHERE status='suspended'"),
        "communities": one("SELECT COUNT(*) FROM communities"),
        "stories": one("SELECT COUNT(*) FROM stories"),
    }


def categories(conn, active_only=True):
    sql = "SELECT * FROM categories" + (" WHERE is_active=1" if active_only else "") + " ORDER BY id"
    return conn.execute(sql).fetchall()


def category_name(cat_row, lang: str) -> str:
    return cat_row["name_ar"] if lang == "ar" else cat_row["name_en"]
