"""Silver — shared UI components (post cards, story bar, report dialogs)."""
import time

import streamlit as st

from . import services, theme
from .i18n import t, rel_time

SECTION_LABELS = {
    "circle": "sec_circle", "front": "sec_front", "interests": "sec_interests",
    "communities": "sec_communities", "nearby": "sec_nearby",
}


def goto(view: str, **params):
    st.session_state["view"] = view
    st.session_state["view_params"] = params
    st.rerun()


def render_post(conn, post, viewer_id: int, lang: str, key_prefix: str = "p"):
    """One post card with all interactions."""
    pid = post["id"]
    k = f"{key_prefix}_{pid}"
    with st.container(border=True):
        c1, c2 = st.columns([1, 8])
        with c1:
            st.markdown(theme.avatar_html(post["display_name"]), unsafe_allow_html=True)
        with c2:
            audiences = [r["audience"] for r in conn.execute(
                "SELECT audience FROM post_audiences WHERE post_id=?", (pid,)).fetchall()]
            tags = " ".join(
                f'<span class="silver-tag">{t(SECTION_LABELS.get(a, "sec_communities"), lang)}</span>'
                for a in audiences
            )
            when = rel_time(post["created_at"], time.time(), lang)
            ai_tag = f' <span class="silver-tag">🤖 {t("ai_flag", lang)}</span>' if post["ai_generated"] else ""
            st.markdown(
                f"**{post['display_name']}** <span class='silver-muted'>@{post['username']} · {when}</span><br>{tags}{ai_tag}",
                unsafe_allow_html=True,
            )
        if post["body"]:
            st.write(post["body"])
        for m in services.post_media(conn, pid):
            try:
                if m["kind"] == "image":
                    st.image(m["path"], use_container_width=True)
                else:
                    st.video(m["path"])
            except Exception:
                st.caption("⚠️ media unavailable")

        liked = services.user_liked(conn, viewer_id, pid)
        show_likes = conn.execute(
            "SELECT show_like_counts FROM user_settings WHERE user_id=?", (post["author_id"],)
        ).fetchone()
        like_n = post["likes"] if (show_likes is None or show_likes[0]) else ""
        b1, b2, b3, b4, b5 = st.columns(5)
        if b1.button(("💚" if liked else "🤍") + f" {like_n}", key=f"{k}_like"):
            services.toggle_like(conn, viewer_id, pid)
            st.rerun()
        if b2.button(f"💬 {post['comment_count']}", key=f"{k}_cmt"):
            st.session_state[f"{k}_show_comments"] = not st.session_state.get(f"{k}_show_comments", False)
        saved = conn.execute(
            "SELECT 1 FROM saved_posts WHERE user_id=? AND post_id=?", (viewer_id, pid)).fetchone()
        if b3.button("🔖" if not saved else "✅", key=f"{k}_save",
                     help=t("saved", lang) if not saved else t("unsave", lang)):
            services.toggle_save(conn, viewer_id, pid)
            st.rerun()
        if b4.button("📤", key=f"{k}_share", help=t("share_dm", lang)):
            st.session_state[f"{k}_show_share"] = not st.session_state.get(f"{k}_show_share", False)
        with b5.popover("⋯"):
            if post["author_id"] != viewer_id:
                if st.button(f"🚩 {t('report', lang)}", key=f"{k}_rep"):
                    st.session_state[f"{k}_show_report"] = True
                if st.button(f"⛔ {t('block', lang)}", key=f"{k}_blk"):
                    services.block(conn, viewer_id, post["author_id"])
                    st.rerun()
            if st.button(f"👤 @{post['username']}", key=f"{k}_prof"):
                goto("profile", user_id=post["author_id"])

        if st.session_state.get(f"{k}_show_comments"):
            for c in services.post_comments(conn, pid):
                st.markdown(
                    f"<span class='silver-muted'>{c['display_name']}:</span> {c['body']}",
                    unsafe_allow_html=True,
                )
            with st.form(key=f"{k}_cform", clear_on_submit=True, border=False):
                txt = st.text_input(t("write_comment", lang), key=f"{k}_ctxt", label_visibility="collapsed",
                                    placeholder=t("write_comment", lang))
                if st.form_submit_button(t("comment", lang)) and txt.strip():
                    services.add_comment(conn, pid, viewer_id, txt.strip())
                    st.rerun()

        if st.session_state.get(f"{k}_show_share"):
            _share_in_dm(conn, post, viewer_id, lang, k)

        if st.session_state.get(f"{k}_show_report"):
            report_form(conn, viewer_id, "post", pid, lang, k)


def _share_in_dm(conn, post, viewer_id, lang, k):
    friends = conn.execute(
        "SELECT u.id, pr.display_name FROM follows f JOIN users u ON u.id=f.followee_id "
        "JOIN profiles pr ON pr.user_id=u.id WHERE f.follower_id=? AND u.status='active'",
        (viewer_id,),
    ).fetchall()
    if not friends:
        st.caption(t("no_results", lang))
        return
    options = {f"{r['display_name']} (#{r['id']})": r["id"] for r in friends}
    sel = st.selectbox(t("share_dm", lang), list(options), key=f"{k}_share_sel")
    if st.button(t("send", lang), key=f"{k}_share_send"):
        target = options[sel]
        if services.can_message(conn, viewer_id, target):
            cid = services.get_or_create_direct(conn, viewer_id, target)
            services.send_message(conn, cid, viewer_id, body="", post_id=post["id"])
            st.success(t("post_published", lang))
            st.session_state[f"{k}_show_share"] = False
        else:
            st.warning(t("cannot_message", lang))


def report_form(conn, reporter_id: int, target_kind: str, target_id: int, lang: str, k: str):
    with st.form(key=f"{k}_repform", border=True):
        st.markdown(f"**🚩 {t('report', lang)}**")
        reason = st.selectbox(
            t("report_reason", lang), services.REPORT_REASONS,
            format_func=lambda r: t(r, lang), key=f"{k}_reason",
        )
        details = st.text_input(t("report_details", lang), key=f"{k}_details")
        if st.form_submit_button(t("send", lang)):
            services.create_report(conn, reporter_id, target_kind, target_id, reason, details)
            st.session_state[f"{k}_show_report"] = False
            st.success(t("report_sent", lang))
            st.rerun()


def story_bar(conn, user_id: int, lang: str):
    """Horizontal story strip with add button and rings."""
    stories = services.visible_stories(conn, user_id)
    by_author: dict[int, list] = {}
    for s in stories:
        by_author.setdefault(s["author_id"], []).append(s)

    cols = st.columns(min(8, 1 + max(1, len(by_author))))
    with cols[0]:
        if st.button("➕", key="story_add", help=t("add_story", lang)):
            goto("compose", tab="story")
        st.markdown(f"<div class='silver-muted' style='text-align:center'>{t('add_story', lang)}</div>",
                    unsafe_allow_html=True)
    for i, (author_id, group) in enumerate(list(by_author.items())[:7]):
        first = group[0]
        all_seen = all(s["seen"] for s in group)
        ring = "story-ring-seen" if all_seen else "story-ring-new"
        with cols[(i + 1) % len(cols)]:
            initial = (first["display_name"] or "?")[:1].upper()
            st.markdown(f"<div class='{ring}'>{initial}</div>", unsafe_allow_html=True)
            if st.button(first["display_name"][:12], key=f"story_open_{author_id}"):
                goto("story_view", author_id=author_id)
