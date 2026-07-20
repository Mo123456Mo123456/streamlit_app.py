"""Silver / سيلفر — social platform MVP.

Entry point: authentication, routing and the main navigation shell.
Run with:  streamlit run streamlit_app.py
"""
import streamlit as st

from silver import auth, db, services, theme
from silver.i18n import t
from silver import (
    views_auth, views_feed, views_social, views_discover, views_admin,
)

st.set_page_config(
    page_title="Silver | سيلفر",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_connection():
    conn = db.get_conn()
    db.init_db(conn)
    auth.ensure_admin(conn)
    return conn


conn = get_connection()

# ---------------------------------------------------------------- session
st.session_state.setdefault("lang", "ar")
st.session_state.setdefault("view", "home")
st.session_state.setdefault("view_params", {})
lang = st.session_state["lang"]
theme.apply(lang)

user_id = st.session_state.get("user_id")
user = auth.get_user(conn, user_id) if user_id else None
if user is not None and user["status"] != "active":
    st.session_state.pop("user_id", None)
    user = None

# ---------------------------------------------------------------- anonymous
if user is None:
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🌐 " + ("EN" if lang == "ar" else "ع")):
            st.session_state["lang"] = "en" if lang == "ar" else "ar"
            st.rerun()
    views_auth.auth_view(conn, lang)
    st.stop()

# ---------------------------------------------------------------- onboarding
has_interests = conn.execute(
    "SELECT 1 FROM user_interests WHERE user_id=? LIMIT 1", (user["id"],)
).fetchone()
if st.session_state["view"] == "onboarding" or not has_interests:
    views_auth.onboarding_view(conn, user["id"], lang)
    st.stop()

# ---------------------------------------------------------------- navigation
unread_n = services.unread_count(conn, user["id"])
unread_dm = sum(c["unread"] for c in services.user_conversations(conn, user["id"]))

with st.sidebar:
    theme.header()
    st.caption(t("tagline", lang))
    st.markdown(f"**{user['display_name']}** · @{user['username']}")
    st.divider()

    NAV = [
        ("home", "🏠", t("home", lang), ""),
        ("discover", "🔍", t("discover", lang), ""),
        ("compose", "➕", t("create", lang), ""),
        ("messages", "✉️", t("messages", lang), f" ({unread_dm})" if unread_dm else ""),
        ("notifications", "🔔", t("notifications", lang), f" ({unread_n})" if unread_n else ""),
        ("communities", "👥", t("communities", lang), ""),
        ("profile", "👤", t("profile", lang), ""),
        ("settings", "⚙️", t("settings", lang), ""),
    ]
    if user["role"] in views_admin.ADMIN_ROLES:
        NAV.append(("admin", "🛡", t("admin", lang), ""))

    for view_name, icon, label, badge in NAV:
        current = st.session_state["view"] == view_name
        if st.button(f"{icon} {label}{badge}", key=f"nav_{view_name}",
                     type="primary" if current else "secondary",
                     use_container_width=True):
            st.session_state["view"] = view_name
            st.session_state["view_params"] = {}
            st.rerun()

    st.divider()
    if st.button("🌐 " + ("English" if lang == "ar" else "العربية"), use_container_width=True):
        new_lang = "en" if lang == "ar" else "ar"
        conn.execute("UPDATE user_settings SET language=? WHERE user_id=?", (new_lang, user["id"]))
        conn.commit()
        st.session_state["lang"] = new_lang
        st.rerun()
    if st.button("🚪 " + t("logout", lang), use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ---------------------------------------------------------------- routing
view = st.session_state["view"]
params = st.session_state.get("view_params", {})

if view == "home":
    views_feed.home_view(conn, user["id"], lang)
elif view == "compose":
    views_feed.compose_view(conn, user["id"], lang, tab=params.get("tab", "post"))
elif view == "story_view":
    views_feed.story_view(conn, user["id"], lang, params.get("author_id", user["id"]))
elif view == "discover":
    views_discover.discover_view(conn, user["id"], lang)
elif view == "communities":
    views_discover.communities_view(conn, user["id"], lang)
elif view == "community":
    views_discover.community_view(conn, user["id"], lang, params.get("community_id"))
elif view == "live_room":
    views_discover.live_room_view(conn, user["id"], lang, params.get("stream_id"))
elif view == "messages":
    views_social.messages_view(conn, user["id"], lang)
elif view == "chat":
    views_social.chat_view(conn, user["id"], lang, params.get("conversation_id"))
elif view == "notifications":
    views_social.notifications_view(conn, user["id"], lang)
elif view == "profile":
    views_social.profile_view(conn, user["id"], lang, params.get("user_id"))
elif view == "settings":
    views_social.settings_view(conn, user["id"], lang)
elif view == "admin":
    views_admin.admin_view(conn, user, lang)
else:
    views_feed.home_view(conn, user["id"], lang)
