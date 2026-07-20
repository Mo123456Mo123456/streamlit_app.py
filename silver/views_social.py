"""Silver — messages, notifications, profile, settings."""
import time

import streamlit as st

from . import auth, services, theme, components
from .i18n import t, rel_time


# ---------------------------------------------------------------- messages
def messages_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader("💬 " + t("messages", lang))

    requests = services.user_conversations(conn, user_id, requests=True)
    if requests:
        with st.expander(f"📥 {t('message_requests', lang)} ({len(requests)})"):
            for c in requests:
                peer = services.conversation_peer(conn, c["id"], user_id)
                if not peer:
                    continue
                col1, col2, col3 = st.columns([4, 1, 1])
                col1.markdown(f"**{peer['display_name']}** — {c['last_body'] or ''}")
                if col2.button(t("accept", lang), key=f"req_ok_{c['id']}"):
                    services.accept_request(conn, c["id"])
                    st.rerun()
                if col3.button(t("block", lang), key=f"req_no_{c['id']}"):
                    services.block(conn, user_id, peer["id"])
                    st.rerun()

    with st.expander("✉️ " + t("new_message", lang)):
        q = st.text_input(t("search", lang), key="dm_search")
        if q:
            for u in services.search_users(conn, user_id, q):
                if u["id"] == user_id:
                    continue
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{u['display_name']}** @{u['username']}")
                if c2.button(t("message_btn", lang), key=f"dm_new_{u['id']}"):
                    if services.can_message(conn, user_id, u["id"]):
                        cid = services.get_or_create_direct(conn, user_id, u["id"])
                        components.goto("chat", conversation_id=cid)
                    else:
                        st.warning(t("cannot_message", lang))

    convs = services.user_conversations(conn, user_id)
    if not convs:
        st.caption(t("no_conversations", lang))
    for c in convs:
        peer = services.conversation_peer(conn, c["id"], user_id)
        if not peer:
            continue
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            unread = f" · 🟢 {c['unread']}" if c["unread"] else ""
            pin = "📌 " if c["pinned"] else ""
            col1.markdown(f"{pin}**{peer['display_name']}**{unread}<br>"
                          f"<span class='silver-muted'>{(c['last_body'] or '')[:60]}</span>",
                          unsafe_allow_html=True)
            if col2.button(t("messages", lang), key=f"open_{c['id']}"):
                components.goto("chat", conversation_id=c["id"])


def chat_view(conn, user_id: int, lang: str, conversation_id: int):
    peer = services.conversation_peer(conn, conversation_id, user_id)
    if peer is None:
        components.goto("messages")
        return
    c1, c2, c3 = st.columns([1, 4, 1])
    if c1.button("← " + t("back", lang)):
        components.goto("messages")
    c2.subheader(peer["display_name"])
    with c3.popover("⋯"):
        member = conn.execute(
            "SELECT * FROM conversation_members WHERE conversation_id=? AND user_id=?",
            (conversation_id, user_id)).fetchone()
        if st.button(("📌 " if not member["pinned"] else "📍 ") + "Pin", key="chat_pin"):
            conn.execute("UPDATE conversation_members SET pinned=1-pinned WHERE conversation_id=? AND user_id=?",
                         (conversation_id, user_id))
            conn.commit()
            st.rerun()
        if st.button("🔕 Mute", key="chat_mute"):
            conn.execute("UPDATE conversation_members SET muted=1-muted WHERE conversation_id=? AND user_id=?",
                         (conversation_id, user_id))
            conn.commit()
            st.rerun()
        if st.button("🗄 Archive", key="chat_arch"):
            conn.execute("UPDATE conversation_members SET archived=1 WHERE conversation_id=? AND user_id=?",
                         (conversation_id, user_id))
            conn.commit()
            components.goto("messages")
        if st.button(f"⛔ {t('block', lang)}", key="chat_block"):
            services.block(conn, user_id, peer["id"])
            components.goto("messages")
        if st.button(f"🚩 {t('report', lang)}", key="chat_report"):
            st.session_state["chat_show_report"] = True

    if st.session_state.get("chat_show_report"):
        components.report_form(conn, user_id, "user", peer["id"], lang, "chat")

    services.mark_conversation_read(conn, conversation_id, user_id)
    for m in services.conversation_messages(conn, conversation_id):
        role = "user" if m["sender_id"] == user_id else "assistant"
        with st.chat_message(role, avatar="🟢" if role == "user" else "⚪"):
            if m["story_id"]:
                st.caption("↩️ " + t("reply_story", lang))
            if m["post_id"]:
                shared = services.get_post(conn, m["post_id"])
                if shared:
                    st.caption(f"📤 @{shared['username']}: {(shared['body'] or '')[:80]}")
            if m["body"]:
                st.write(m["body"])
            if m["media_path"]:
                try:
                    if m["media_path"].lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        st.image(m["media_path"])
                    else:
                        st.video(m["media_path"])
                except Exception:
                    st.caption("⚠️ media unavailable")
            st.caption(rel_time(m["created_at"], time.time(), lang))

    up = st.file_uploader(t("upload_media", lang), type=["png", "jpg", "jpeg", "webp", "mp4", "mov"],
                          key=f"chat_up_{conversation_id}")
    txt = st.chat_input(t("type_message", lang))
    if txt:
        if not services.can_message(conn, user_id, peer["id"]):
            st.warning(t("cannot_message", lang))
        else:
            path = services.save_upload(user_id, up) if up else ""
            services.send_message(conn, conversation_id, user_id, txt, media_path=path)
            st.rerun()


# ---------------------------------------------------------------- notifications
NOTIF_TEXT = {
    "follow": "notif_follow", "like": "notif_like", "comment": "notif_comment",
    "message": "notif_message", "live": "notif_live", "community": "notif_community",
    "report": "notif_report",
}


def notifications_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader("🔔 " + t("notifications", lang))
    if st.button(t("mark_read", lang)):
        services.mark_all_read(conn, user_id)
        st.rerun()
    notifs = services.user_notifications(conn, user_id)
    if not notifs:
        st.caption(t("no_notifications", lang))
    for n in notifs:
        icon = {"follow": "👤", "like": "💚", "comment": "💬", "message": "✉️",
                "live": "📡", "community": "👥", "report": "🚩", "security": "🔐"}.get(n["kind"], "🔔")
        actor = n["actor_name"] or ""
        text = t(NOTIF_TEXT.get(n["kind"], "notifications"), lang)
        unread = "" if n["read"] else " 🟢"
        when = rel_time(n["created_at"], time.time(), lang)
        st.markdown(f"{icon} **{actor}** {text}{unread} — "
                    f"<span class='silver-muted'>{when}</span>", unsafe_allow_html=True)


# ---------------------------------------------------------------- profile
def profile_view(conn, viewer_id: int, lang: str, user_id: int | None = None):
    target_id = user_id or viewer_id
    user = auth.get_user(conn, target_id)
    if user is None or user["status"] != "active":
        st.caption(t("no_results", lang))
        return
    own = target_id == viewer_id

    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        with c1:
            if user["avatar_path"]:
                try:
                    st.image(user["avatar_path"], width=90)
                except Exception:
                    st.markdown(theme.avatar_html(user["display_name"]), unsafe_allow_html=True)
            else:
                st.markdown(theme.avatar_html(user["display_name"]), unsafe_allow_html=True)
        with c2:
            st.markdown(f"### {user['display_name']}")
            st.caption(f"@{user['username']}" + (f" · 📍 {user['city']}" if user["city"] else ""))
            if user["bio"]:
                st.write(user["bio"])
            if user["link"]:
                st.markdown(f"🔗 {user['link']}")
        fers, fing = services.follower_counts(conn, target_id)
        n_posts = conn.execute("SELECT COUNT(*) c FROM posts WHERE author_id=? AND hidden=0",
                               (target_id,)).fetchone()["c"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(t("followers", lang), fers)
        m2.metric(t("following", lang), fing)
        m3.metric(t("posts", lang), n_posts)
        m4.metric(t("communities", lang), len(services.user_communities(conn, target_id)))

        if own:
            if st.button("✏️ " + t("edit_profile", lang)):
                st.session_state["edit_profile"] = not st.session_state.get("edit_profile", False)
        else:
            b1, b2, b3, b4 = st.columns(4)
            following = services.is_following(conn, viewer_id, target_id)
            if b1.button(t("unfollow", lang) if following else t("follow", lang),
                         type="secondary" if following else "primary"):
                (services.unfollow if following else services.follow)(conn, viewer_id, target_id)
                st.rerun()
            if b2.button("✉️ " + t("message_btn", lang)):
                if services.can_message(conn, viewer_id, target_id):
                    cid = services.get_or_create_direct(conn, viewer_id, target_id)
                    components.goto("chat", conversation_id=cid)
                else:
                    st.warning(t("cannot_message", lang))
            blocked = conn.execute("SELECT 1 FROM blocks WHERE blocker_id=? AND blocked_id=?",
                                   (viewer_id, target_id)).fetchone()
            if b3.button(t("unblock", lang) if blocked else t("block", lang)):
                (services.unblock if blocked else services.block)(conn, viewer_id, target_id)
                st.rerun()
            if b4.button("🚩 " + t("report", lang)):
                st.session_state["profile_show_report"] = True
        if st.session_state.get("profile_show_report") and not own:
            components.report_form(conn, viewer_id, "user", target_id, lang, "prof")

    if own and st.session_state.get("edit_profile"):
        _edit_profile_form(conn, user, lang)

    featured = services.featured_stories(conn, target_id)
    if featured:
        st.markdown(f"**⭐ {t('featured_stories', lang)}**")
        cols = st.columns(min(6, len(featured)))
        for i, s in enumerate(featured):
            with cols[i % len(cols)]:
                st.markdown(f"<div class='story-ring-new'>⭐</div>", unsafe_allow_html=True)
                st.caption((s["body"] or "")[:20])

    tab_names = [t("posts", lang), t("videos", lang), t("live", lang), t("communities", lang)]
    if own:
        tab_names.append(t("saved_posts", lang))
    tabs = st.tabs(tab_names)
    with tabs[0]:
        posts = services.user_posts(conn, target_id, viewer_id)
        if not posts:
            st.caption(t("no_posts", lang))
        for p in posts:
            components.render_post(conn, p, viewer_id, lang, key_prefix="prof")
    with tabs[1]:
        vids = [p for p in services.user_posts(conn, target_id, viewer_id)
                if p["kind"] in ("video", "short_video")]
        if not vids:
            st.caption(t("no_posts", lang))
        for p in vids:
            components.render_post(conn, p, viewer_id, lang, key_prefix="profv")
    with tabs[2]:
        for s in services.saved_streams(conn, target_id):
            st.markdown(f"📼 **{s['title']}** — <span class='silver-muted'>{s['description']}</span>",
                        unsafe_allow_html=True)
        if not services.saved_streams(conn, target_id):
            st.caption(t("no_posts", lang))
    with tabs[3]:
        for c in services.user_communities(conn, target_id):
            st.markdown(f"👥 **{c['name']}** — {c['role']}")
    if own:
        with tabs[4]:
            saved = services.saved_posts(conn, viewer_id)
            if not saved:
                st.caption(t("no_posts", lang))
            for p in saved:
                components.render_post(conn, p, viewer_id, lang, key_prefix="saved")


def _edit_profile_form(conn, user, lang):
    with st.form("edit_profile_form"):
        name = st.text_input(t("display_name", lang), value=user["display_name"])
        bio = st.text_area(t("bio", lang), value=user["bio"], max_chars=200)
        city = st.text_input(t("your_city", lang), value=user["city"])
        link = st.text_input("🔗", value=user["link"])
        avatar = st.file_uploader(t("upload_media", lang), type=["png", "jpg", "jpeg", "webp"])
        if st.form_submit_button(t("save", lang), type="primary"):
            avatar_path = services.save_upload(user["id"], avatar) if avatar else user["avatar_path"]
            conn.execute(
                "UPDATE profiles SET display_name=?, bio=?, city=?, link=?, avatar_path=? WHERE user_id=?",
                (name.strip() or user["display_name"], bio.strip(), city.strip(), link.strip(),
                 avatar_path, user["id"]),
            )
            conn.commit()
            st.session_state["edit_profile"] = False
            st.rerun()


# ---------------------------------------------------------------- settings
def settings_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader("⚙️ " + t("settings", lang))
    s = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    user = auth.get_user(conn, user_id)

    new_lang = st.radio(t("language", lang), ["ar", "en"],
                        format_func=lambda l: "العربية" if l == "ar" else "English",
                        index=0 if lang == "ar" else 1, horizontal=True)
    if new_lang != lang:
        conn.execute("UPDATE user_settings SET language=? WHERE user_id=?", (new_lang, user_id))
        conn.commit()
        st.session_state["lang"] = new_lang
        st.rerun()

    st.markdown(f"**{t('privacy', lang)}**")
    is_private = st.toggle(t("private_toggle", lang), value=bool(user["is_private"]))
    show_likes = st.toggle(t("show_likes", lang), value=bool(s["show_like_counts"]))
    wcm = st.selectbox(
        t("who_can_message", lang), ["everyone", "followers", "friends", "nobody"],
        index=["everyone", "followers", "friends", "nobody"].index(s["who_can_message"]),
        format_func=lambda v: t("wcm_" + v, lang),
    )

    st.markdown(f"**{t('notif_settings', lang)}**")
    nf = st.toggle(t("notif_follow", lang), value=bool(s["notif_follows"]))
    nl = st.toggle(t("notif_like", lang), value=bool(s["notif_likes"]))
    nc = st.toggle(t("notif_comment", lang), value=bool(s["notif_comments"]))
    nm = st.toggle(t("notif_message", lang), value=bool(s["notif_messages"]))
    nv = st.toggle(t("notif_live", lang), value=bool(s["notif_live"]))

    if st.button(t("save", lang), type="primary"):
        conn.execute("UPDATE profiles SET is_private=? WHERE user_id=?", (int(is_private), user_id))
        conn.execute(
            "UPDATE user_settings SET who_can_message=?, show_like_counts=?, notif_follows=?, "
            "notif_likes=?, notif_comments=?, notif_messages=?, notif_live=? WHERE user_id=?",
            (wcm, int(show_likes), int(nf), int(nl), int(nc), int(nm), int(nv), user_id),
        )
        conn.commit()
        st.success("✓")

    with st.expander("🔐 " + t("change_password", lang)):
        with st.form("pwd_form"):
            old = st.text_input(t("old_password", lang), type="password")
            new = st.text_input(t("new_password", lang), type="password")
            if st.form_submit_button(t("change_password", lang)):
                err = auth.change_password(conn, user_id, old, new)
                if err:
                    st.error(t(err, lang))
                else:
                    st.success(t("password_changed", lang))

    with st.expander("⛔ " + t("blocked_users", lang)):
        rows = conn.execute(
            "SELECT b.blocked_id, pr.display_name FROM blocks b "
            "JOIN profiles pr ON pr.user_id=b.blocked_id WHERE b.blocker_id=?", (user_id,)).fetchall()
        for r in rows:
            c1, c2 = st.columns([4, 1])
            c1.write(r["display_name"])
            if c2.button(t("unblock", lang), key=f"unb_{r['blocked_id']}"):
                services.unblock(conn, user_id, r["blocked_id"])
                st.rerun()

    with st.expander("🗑 " + t("delete_account", lang)):
        sure = st.checkbox(t("delete_confirm", lang))
        if st.button(t("delete_account", lang), disabled=not sure):
            auth.delete_account(conn, user_id)
            st.session_state.clear()
            st.rerun()
