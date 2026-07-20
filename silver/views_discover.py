"""Silver — discover page, short videos, communities, live rooms."""
import time

import streamlit as st

from . import auth, services, theme, components
from .i18n import t, rel_time


def discover_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader("🔍 " + t("discover", lang))
    query = st.text_input(t("search", lang), placeholder=t("search_ph", lang), key="disc_q")

    if query.strip():
        _search_results(conn, user_id, lang, query.strip())
        return

    live = services.live_streams_now(conn)
    if live:
        st.markdown(f"**📡 {t('live_now', lang)}**")
        for s in live:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(
                    f"<span class='live-badge'>LIVE</span> **{s['title']}** — {s['display_name']} "
                    f"<span class='silver-muted'>· {s['viewer_count']} {t('viewers', lang)}</span>",
                    unsafe_allow_html=True)
                if c2.button("▶", key=f"disc_live_{s['id']}"):
                    components.goto("live_room", stream_id=s["id"])

    tabs = st.tabs([t("trending", lang), t("videos", lang), t("suggested_users", lang),
                    t("suggested_communities", lang), t("nearby_content", lang)])
    with tabs[0]:
        for p in services.trending_posts(conn, user_id):
            components.render_post(conn, p, user_id, lang, key_prefix="trend")
    with tabs[1]:
        vids = services.short_videos(conn, user_id)
        if not vids:
            st.caption(t("no_posts", lang))
        for p in vids:
            components.render_post(conn, p, user_id, lang, key_prefix="vid")
    with tabs[2]:
        for u in services.suggested_users(conn, user_id):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{u['display_name']}** @{u['username']}"
                        + (f" · 📍 {u['city']}" if u["city"] else ""))
            if c2.button(t("follow", lang), key=f"sug_f_{u['id']}", type="primary"):
                services.follow(conn, user_id, u["id"])
                st.rerun()
    with tabs[3]:
        for c in services.list_communities(conn):
            _community_row(conn, c, user_id, lang, "sugc")
    with tabs[4]:
        me = auth.get_user(conn, user_id)
        posts = services.feed_nearby(conn, user_id, me["city"] or "")
        if not me["city"]:
            st.info(t("your_city", lang))
        elif not posts:
            st.caption(t("no_posts", lang))
        for p in posts:
            components.render_post(conn, p, user_id, lang, key_prefix="near")


def _search_results(conn, user_id, lang, query):
    users = services.search_users(conn, user_id, query)
    posts = services.search_posts(conn, user_id, query)
    comms = services.list_communities(conn, query)
    if not (users or posts or comms):
        st.caption(t("no_results", lang))
    if users:
        st.markdown(f"**👤 {t('suggested_users', lang)}**")
        for u in users:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{u['display_name']}** @{u['username']}")
            if c2.button("→", key=f"s_u_{u['id']}"):
                components.goto("profile", user_id=u["id"])
    if comms:
        st.markdown(f"**👥 {t('communities', lang)}**")
        for c in comms:
            _community_row(conn, c, user_id, lang, "s_c")
    if posts:
        st.markdown(f"**📝 {t('posts', lang)}**")
        for p in posts:
            components.render_post(conn, p, user_id, lang, key_prefix="s_p")


# ---------------------------------------------------------------- communities
def _community_row(conn, c, user_id, lang, kp):
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        member_count = c["member_count"] if "member_count" in c.keys() else ""
        kind_label = {"public": "kind_public_c", "approval": "kind_approval", "invite": "kind_invite"}[c["kind"]]
        c1.markdown(f"**{c['name']}** <span class='silver-tag'>{t(kind_label, lang)}</span> "
                    f"<span class='silver-muted'>· {member_count} {t('members', lang)}</span><br>"
                    f"<span class='silver-muted'>{c['description'][:80]}</span>",
                    unsafe_allow_html=True)
        role = services.community_role(conn, c["id"], user_id)
        if role:
            if c2.button("→", key=f"{kp}_open_{c['id']}"):
                components.goto("community", community_id=c["id"])
        else:
            if c2.button(t("join", lang), key=f"{kp}_join_{c['id']}", type="primary"):
                res = services.join_community(conn, c["id"], user_id)
                if res == "active":
                    st.toast(t("joined", lang))
                elif res == "pending":
                    st.toast(t("join_requested", lang))
                st.rerun()


def communities_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader("👥 " + t("communities", lang))
    with st.expander("➕ " + t("create_community", lang)):
        with st.form("comm_form"):
            name = st.text_input(t("community_name", lang))
            desc = st.text_area(t("bio", lang), height=68)
            kind = st.radio(t("community_kind", lang), ["public", "approval", "invite"],
                            format_func=lambda k: t({"public": "kind_public_c", "approval": "kind_approval",
                                                     "invite": "kind_invite"}[k], lang), horizontal=True)
            if st.form_submit_button(t("create_community", lang), type="primary") and name.strip():
                cid = services.create_community(conn, user_id, name.strip(), desc.strip(), kind)
                components.goto("community", community_id=cid)

    mine = services.user_communities(conn, user_id)
    if mine:
        st.markdown(f"**{t('sec_communities', lang)}**")
        for c in mine:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{c['name']}** — <span class='silver-muted'>{c['role']}</span>",
                        unsafe_allow_html=True)
            if c2.button("→", key=f"my_c_{c['id']}"):
                components.goto("community", community_id=c["id"])
    st.markdown(f"**{t('suggested_communities', lang)}**")
    for c in services.list_communities(conn):
        if not any(m["id"] == c["id"] for m in mine):
            _community_row(conn, c, user_id, lang, "all_c")


def community_view(conn, user_id: int, lang: str, community_id: int):
    c = conn.execute("SELECT * FROM communities WHERE id=?", (community_id,)).fetchone()
    if c is None:
        components.goto("communities")
        return
    if st.button("← " + t("back", lang)):
        components.goto("communities")
    st.subheader(f"👥 {c['name']}")
    st.caption(c["description"])
    role = services.community_role(conn, community_id, user_id)
    members = services.community_members(conn, community_id)
    st.markdown(f"<span class='silver-tag'>{len(members)} {t('members', lang)}</span>",
                unsafe_allow_html=True)

    if role is None:
        if st.button(t("join", lang), type="primary"):
            res = services.join_community(conn, community_id, user_id)
            st.toast(t("joined" if res == "active" else "join_requested", lang))
            st.rerun()
        return

    if role in ("owner", "manager", "moderator"):
        pending = services.community_members(conn, community_id, status="pending")
        if pending:
            with st.expander(f"⏳ {t('pending_requests', lang)} ({len(pending)})"):
                for m in pending:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(m["display_name"])
                    if c2.button(t("accept", lang), key=f"cm_ok_{m['user_id']}"):
                        services.approve_member(conn, community_id, m["user_id"])
                        st.rerun()
                    if c3.button(t("reject", lang), key=f"cm_no_{m['user_id']}"):
                        conn.execute("DELETE FROM community_members WHERE community_id=? AND user_id=?",
                                     (community_id, m["user_id"]))
                        conn.commit()
                        st.rerun()

    with st.form("comm_post_form", clear_on_submit=True):
        body = st.text_area(t("post_in_community", lang), height=80)
        media = st.file_uploader(t("upload_media", lang),
                                 type=["png", "jpg", "jpeg", "webp", "mp4", "mov"])
        if st.form_submit_button(t("publish", lang), type="primary") and (body.strip() or media):
            media_files = [{"path": services.save_upload(user_id, media)}] if media else []
            has_video = any(m["path"].lower().endswith((".mp4", ".mov")) for m in media_files)
            kind = "video" if has_video else ("image" if media_files else "text")
            services.create_post(conn, user_id, body.strip(), kind, ["communities"],
                                 community_id=community_id, category_id=c["category_id"])
            st.rerun()

    for p in services.community_posts(conn, community_id):
        components.render_post(conn, p, user_id, lang, key_prefix=f"comm{community_id}")

    if role != "owner":
        if st.button(t("leave", lang)):
            services.leave_community(conn, community_id, user_id)
            components.goto("communities")


# ---------------------------------------------------------------- live room
def live_room_view(conn, user_id: int, lang: str, stream_id: int):
    s = services.get_stream(conn, stream_id)
    if s is None:
        components.goto("discover")
        return
    if st.button("← " + t("back", lang)):
        components.goto("discover")

    is_host = s["host_id"] == user_id
    if not is_host and s["status"] == "live":
        services.join_stream(conn, stream_id, user_id)
        s = services.get_stream(conn, stream_id)

    badge = '<span class="live-badge">LIVE</span>' if s["status"] == "live" else f"📼 {t('stream_ended', lang)}"
    st.markdown(f"{badge} **{s['title']}**", unsafe_allow_html=True)
    st.caption(f"{s['display_name']} @{s['username']} · 👁 {s['viewer_count']} {t('viewers', lang)}")
    if s["description"]:
        st.write(s["description"])
    st.info(t("live_note", lang))

    if s["status"] == "live":
        c1, c2, c3 = st.columns(3)
        if not is_host:
            if not services.is_following(conn, user_id, s["host_id"]):
                if c1.button(t("follow", lang), type="primary"):
                    services.follow(conn, user_id, s["host_id"])
                    st.rerun()
            if s["guests_enabled"] and c2.button("🎙 " + t("join_as_guest", lang)):
                services.request_guest(conn, stream_id, user_id)
                st.toast("✓")
            if c3.button("🚩 " + t("report", lang)):
                st.session_state["live_show_report"] = True
        if st.session_state.get("live_show_report"):
            components.report_form(conn, user_id, "stream", stream_id, lang, "live")

        if is_host:
            _host_tools(conn, s, lang)

        approved = services.stream_guests(conn, stream_id, "approved")
        if approved:
            st.markdown("🎙 **" + ", ".join(g["display_name"] for g in approved) + "**")

        st.markdown(f"**💬 {t('live_chat', lang)}**")
        if s["comments_enabled"]:
            with st.form("live_chat_form", clear_on_submit=True, border=False):
                msg = st.text_input(t("type_message", lang), label_visibility="collapsed",
                                    placeholder=t("type_message", lang))
                col_a, col_b = st.columns([1, 1])
                if col_a.form_submit_button(t("send", lang), type="primary") and msg.strip():
                    services.live_comment(conn, stream_id, user_id, msg.strip())
                    st.rerun()
                if col_b.form_submit_button("🔄 " + t("refresh", lang)):
                    st.rerun()
        for cm in services.stream_comments(conn, stream_id):
            pin = "📌 " if cm["pinned"] else ""
            st.markdown(f"{pin}**{cm['display_name']}**: {cm['body']} "
                        f"<span class='silver-muted'>{rel_time(cm['created_at'], time.time(), lang)}</span>",
                        unsafe_allow_html=True)


def _host_tools(conn, s, lang):
    stream_id = s["id"]
    with st.expander("🛠 Host tools", expanded=True):
        requested = services.stream_guests(conn, stream_id, "requested")
        if requested:
            st.markdown(f"**{t('guest_requests', lang)}**")
            for g in requested:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(g["display_name"])
                if c2.button(t("accept", lang), key=f"g_ok_{g['user_id']}"):
                    services.set_guest_status(conn, stream_id, g["user_id"], "approved")
                    st.rerun()
                if c3.button(t("reject", lang), key=f"g_no_{g['user_id']}"):
                    services.set_guest_status(conn, stream_id, g["user_id"], "rejected")
                    st.rerun()
        keep = st.toggle(t("save_recording", lang), value=bool(s["save_recording"]))
        if st.button("⏹ " + t("end_stream", lang), type="primary"):
            services.end_stream(conn, stream_id, keep)
            st.rerun()
