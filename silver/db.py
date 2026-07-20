"""Silver — database layer.

SQLite for the MVP; the schema mirrors the production design so it can be
migrated to PostgreSQL without structural changes.
"""
import os
import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(os.environ.get("SILVER_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
MEDIA_DIR = DATA_DIR / "media"
DB_PATH = DATA_DIR / "silver.db"

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- user | creator | community_mod | platform_mod | admin
    status TEXT NOT NULL DEFAULT 'active', -- active | suspended | closed
    created_at REAL NOT NULL,
    last_login_at REAL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    bio TEXT DEFAULT '',
    city TEXT DEFAULT '',
    link TEXT DEFAULT '',
    avatar_path TEXT DEFAULT '',
    cover_path TEXT DEFAULT '',
    is_private INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS follows (
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    followee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name_ar TEXT NOT NULL,
    name_en TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_interests (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, category_id)
);

-- The five social sections are fixed rows here for referential clarity.
CREATE TABLE IF NOT EXISTS social_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE, -- circle | front | interests | communities | nearby
    name_ar TEXT NOT NULL,
    name_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL DEFAULT 'text', -- text | image | video | short_video | poll
    body TEXT DEFAULT '',
    category_id INTEGER REFERENCES categories(id),
    community_id INTEGER REFERENCES communities(id),
    city TEXT DEFAULT '',
    ai_generated INTEGER NOT NULL DEFAULT 0,
    hidden INTEGER NOT NULL DEFAULT 0, -- moderation hide
    created_at REAL NOT NULL
);

-- One post can target several sections at once (the adaptive post).
CREATE TABLE IF NOT EXISTS post_audiences (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    audience TEXT NOT NULL, -- circle | front | interests | nearby | community
    PRIMARY KEY (post_id, audience)
);

CREATE TABLE IF NOT EXISTS post_variants (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    variant TEXT NOT NULL, -- public | private
    body TEXT NOT NULL,
    PRIMARY KEY (post_id, variant)
);

CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
    kind TEXT NOT NULL, -- image | video | audio | file
    path TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT DEFAULT '',
    audience TEXT NOT NULL DEFAULT 'circle', -- circle | followers | public
    featured INTEGER NOT NULL DEFAULT 0, -- kept on profile after expiry
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS story_views (
    story_id INTEGER NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    viewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    viewed_at REAL NOT NULL,
    PRIMARY KEY (story_id, viewer_id)
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    hidden INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS reactions (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    kind TEXT NOT NULL DEFAULT 'like',
    created_at REAL NOT NULL,
    PRIMARY KEY (user_id, post_id)
);

CREATE TABLE IF NOT EXISTS saved_posts (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    PRIMARY KEY (user_id, post_id)
);

CREATE TABLE IF NOT EXISTS communities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'public', -- public | approval | invite
    category_id INTEGER REFERENCES categories(id),
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS community_members (
    community_id INTEGER NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member', -- owner | manager | moderator | member
    status TEXT NOT NULL DEFAULT 'active', -- active | pending | banned
    joined_at REAL NOT NULL,
    PRIMARY KEY (community_id, user_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL DEFAULT 'direct', -- direct | group
    title TEXT DEFAULT '',
    is_request INTEGER NOT NULL DEFAULT 0, -- message request not yet accepted
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_members (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    muted INTEGER NOT NULL DEFAULT 0,
    pinned INTEGER NOT NULL DEFAULT 0,
    archived INTEGER NOT NULL DEFAULT 0,
    last_read_at REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (conversation_id, user_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT DEFAULT '',
    media_path TEXT DEFAULT '',
    reply_to_id INTEGER REFERENCES messages(id),
    story_id INTEGER REFERENCES stories(id), -- set when the message replies to a story
    post_id INTEGER REFERENCES posts(id),    -- set when a post is shared in DM
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL, -- follow | like | comment | mention | message | community | live | security | report
    actor_id INTEGER REFERENCES users(id),
    ref_id INTEGER, -- post/comment/community/stream id depending on kind
    body TEXT DEFAULT '',
    read INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS live_streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    category_id INTEGER REFERENCES categories(id),
    cover_path TEXT DEFAULT '',
    comments_enabled INTEGER NOT NULL DEFAULT 1,
    guests_enabled INTEGER NOT NULL DEFAULT 1,
    save_recording INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'live', -- live | ended
    started_at REAL NOT NULL,
    ended_at REAL
);

CREATE TABLE IF NOT EXISTS live_guests (
    stream_id INTEGER NOT NULL REFERENCES live_streams(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'requested', -- requested | approved | rejected | removed
    requested_at REAL NOT NULL,
    PRIMARY KEY (stream_id, user_id)
);

CREATE TABLE IF NOT EXISTS live_viewers (
    stream_id INTEGER NOT NULL REFERENCES live_streams(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at REAL NOT NULL,
    PRIMARY KEY (stream_id, user_id)
);

CREATE TABLE IF NOT EXISTS live_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_id INTEGER NOT NULL REFERENCES live_streams(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    pinned INTEGER NOT NULL DEFAULT 0,
    hidden INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_kind TEXT NOT NULL, -- post | comment | user | stream | message
    target_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    details TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open', -- open | resolved | dismissed
    resolved_by INTEGER REFERENCES users(id),
    created_at REAL NOT NULL,
    resolved_at REAL
);

CREATE TABLE IF NOT EXISTS blocks (
    blocker_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    PRIMARY KEY (blocker_id, blocked_id)
);

CREATE TABLE IF NOT EXISTS mutes (
    muter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    muted_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    PRIMARY KEY (muter_id, muted_id)
);

CREATE TABLE IF NOT EXISTS moderation_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moderator_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL, -- hide_post | warn_user | suspend_user | close_account | dismiss_report ...
    target_kind TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    note TEXT DEFAULT '',
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    language TEXT NOT NULL DEFAULT 'ar',
    who_can_message TEXT NOT NULL DEFAULT 'everyone', -- everyone | followers | friends | nobody
    show_activity INTEGER NOT NULL DEFAULT 1,
    show_like_counts INTEGER NOT NULL DEFAULT 1,
    notif_follows INTEGER NOT NULL DEFAULT 1,
    notif_likes INTEGER NOT NULL DEFAULT 1,
    notif_comments INTEGER NOT NULL DEFAULT 1,
    notif_messages INTEGER NOT NULL DEFAULT 1,
    notif_live INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    detail TEXT DEFAULT '',
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id, created_at);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, read, created_at);
CREATE INDEX IF NOT EXISTS idx_stories_expiry ON stories(expires_at);
"""

SECTIONS = [
    ("circle", "دائرتي", "My Circle"),
    ("front", "واجهتي", "My Front"),
    ("interests", "اهتماماتي", "My Interests"),
    ("communities", "مجتمعاتي", "My Communities"),
    ("nearby", "محيطي", "My Surroundings"),
]

DEFAULT_CATEGORIES = [
    ("tech", "التقنية", "Technology"),
    ("cars", "السيارات", "Cars"),
    ("travel", "السفر", "Travel"),
    ("photography", "التصوير", "Photography"),
    ("gaming", "الألعاب", "Gaming"),
    ("sports", "الرياضة", "Sports"),
    ("education", "التعليم", "Education"),
    ("entertainment", "الترفيه", "Entertainment"),
    ("business", "الأعمال", "Business"),
    ("talk", "حوار", "Talk"),
    ("daily", "يوميات", "Daily life"),
    ("news", "أخبار مجتمعية", "Community news"),
]


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    now = time.time()
    for slug, ar, en in SECTIONS:
        conn.execute(
            "INSERT OR IGNORE INTO social_sections (slug, name_ar, name_en) VALUES (?,?,?)",
            (slug, ar, en),
        )
    for slug, ar, en in DEFAULT_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (slug, name_ar, name_en) VALUES (?,?,?)",
            (slug, ar, en),
        )
    conn.commit()
    _ = now


def now() -> float:
    return time.time()
