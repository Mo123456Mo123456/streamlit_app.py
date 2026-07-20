"""Silver — admin / moderation panel (web dashboard)."""
import time

import streamlit as st

from . import services, theme
from .i18n import t, rel_time

ADMIN_ROLES = ("admin", "platform_mod")


def admin_view(conn, user, lang: str):
    if user["role"] not in ADMIN_ROLES:
        st.error(t("no_permission", lang))
        return
    theme.header()
    st.subheader("🛡 " + t("admin", lang))

    tabs = st.tabs([t("stats", lang), t("open_reports", lang), t("manage_users", lang),
                    t("moderate_streams", lang), t("manage_categories", lang), t("audit_log", lang)])

    with tabs[0]:
        s = services.admin_stats(conn)
        r1 = st.columns(5)
        r1[0].metric(t("users_count", lang), s["users"])
        r1[1].metric(t("active_users", lang), s["active_users"])
        r1[2].metric(t("posts_count", lang), s["posts"])
        r1[3].metric(t("videos", lang), s["videos"])
        r1[4].metric(t("stories", lang), s["stories"])
        r2 = st.columns(5)
        r2[0].metric(t("streams_count", lang), s["streams"])
        r2[1].metric(t("messages_count", lang), s["messages"])
        r2[2].metric(t("communities", lang), s["communities"])
        r2[3].metric(t("open_reports", lang), s["open_reports"])
        r2[4].metric(t("suspended_accounts", lang), s["suspended"])

    with tabs[1]:
        reports = services.open_reports(conn)
        if not reports:
            st.caption("✓ " + t("resolved", lang))
        for r in reports:
            with st.container(border=True):
                st.markdown(
                    f"**#{r['id']}** · {r['target_kind']} {r['target_id']} · "
                    f"**{t(r['reason'], lang)}** — {r['reporter_name']} · "
                    f"<span class='silver-muted'>{rel_time(r['created_at'], time.time(), lang)}</span>",
                    unsafe_allow_html=True)
                if r["details"]:
                    st.caption(r["details"])
                _report_preview(conn, r)
                c = st.columns(5)
                actions = [
                    ("dismiss_report", t("dismiss", lang)),
                    ("hide_post" if r["target_kind"] == "post" else "hide_comment", t("hide_content", lang)),
                    ("warn_user", t("warn", lang)),
                    ("suspend_user", t("suspend", lang)),
                    ("close_account", t("close_account_a", lang)),
                ]
                for col, (action, label) in zip(c, actions):
                    if col.button(label, key=f"rep_{r['id']}_{action}"):
                        services.resolve_report(conn, r["id"], user["id"], action)
                        st.rerun()

    with tabs[2]:
        q = st.text_input(t("search", lang), key="adm_uq")
        rows = conn.execute(
            "SELECT u.id, u.username, u.email, u.role, u.status, pr.display_name FROM users u "
            "JOIN profiles pr ON pr.user_id=u.id "
            "WHERE u.username LIKE ? OR u.email LIKE ? OR pr.display_name LIKE ? "
            "ORDER BY u.created_at DESC LIMIT 50",
            (f"%{q}%", f"%{q}%", f"%{q}%"),
        ).fetchall()
        for u in rows:
            c1, c2, c3 = st.columns([4, 1, 1])
            status_icon = {"active": "🟢", "suspended": "🟡", "closed": "🔴"}[u["status"]]
            c1.markdown(f"{status_icon} **{u['display_name']}** @{u['username']} · "
                        f"<span class='silver-muted'>{u['email']} · {u['role']}</span>",
                        unsafe_allow_html=True)
            if u["id"] != user["id"]:
                if u["status"] == "active":
                    if c2.button(t("suspend", lang), key=f"adm_susp_{u['id']}"):
                        conn.execute("UPDATE users SET status='suspended' WHERE id=?", (u["id"],))
                        services.audit(conn, user["id"], "suspend_user", f"user {u['id']}")
                        conn.commit()
                        st.rerun()
                elif u["status"] == "suspended":
                    if c2.button(t("unsuspend", lang), key=f"adm_unsusp_{u['id']}"):
                        conn.execute("UPDATE users SET status='active' WHERE id=?", (u["id"],))
                        services.audit(conn, user["id"], "unsuspend_user", f"user {u['id']}")
                        conn.commit()
                        st.rerun()
                new_role = c3.selectbox(
                    "role", ["user", "creator", "platform_mod", "admin"],
                    index=["user", "creator", "platform_mod", "admin"].index(u["role"])
                    if u["role"] in ("user", "creator", "platform_mod", "admin") else 0,
                    key=f"adm_role_{u['id']}", label_visibility="collapsed")
                if new_role != u["role"]:
                    conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, u["id"]))
                    services.audit(conn, user["id"], "change_role", f"user {u['id']} -> {new_role}")
                    conn.commit()
                    st.rerun()

    with tabs[3]:
        for s in services.live_streams_now(conn):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"📡 **{s['title']}** — {s['display_name']} · {s['viewer_count']} 👁")
            if c2.button("⏹", key=f"adm_end_{s['id']}", help=t("end_stream", lang)):
                services.end_stream(conn, s["id"], keep_recording=False)
                services.audit(conn, user["id"], "force_end_stream", f"stream {s['id']}")
                st.rerun()

    with tabs[4]:
        for c in services.categories(conn, active_only=False):
            c1, c2 = st.columns([4, 1])
            state = "🟢" if c["is_active"] else "⚪"
            c1.write(f"{state} {c['name_ar']} / {c['name_en']} ({c['slug']})")
            if c2.button("🔁", key=f"cat_{c['id']}"):
                conn.execute("UPDATE categories SET is_active=1-is_active WHERE id=?", (c["id"],))
                conn.commit()
                st.rerun()
        with st.form("new_cat"):
            slug = st.text_input("slug")
            ar = st.text_input("name (ar)")
            en = st.text_input("name (en)")
            if st.form_submit_button("➕") and slug and ar and en:
                conn.execute("INSERT OR IGNORE INTO categories (slug, name_ar, name_en) VALUES (?,?,?)",
                             (slug.strip(), ar.strip(), en.strip()))
                conn.commit()
                st.rerun()

    with tabs[5]:
        logs = conn.execute(
            "SELECT a.*, pr.display_name FROM audit_logs a "
            "LEFT JOIN profiles pr ON pr.user_id=a.actor_id "
            "ORDER BY a.created_at DESC LIMIT 100").fetchall()
        for lg in logs:
            st.markdown(f"`{lg['action']}` — {lg['display_name'] or '—'} · {lg['detail']} · "
                        f"<span class='silver-muted'>{rel_time(lg['created_at'], time.time(), lang)}</span>",
                        unsafe_allow_html=True)


def _report_preview(conn, r):
    """Show the reported content so the moderator has context."""
    kind, tid = r["target_kind"], r["target_id"]
    if kind == "post":
        p = conn.execute("SELECT body FROM posts WHERE id=?", (tid,)).fetchone()
        if p:
            st.info((p["body"] or "(media)")[:200])
    elif kind == "comment":
        c = conn.execute("SELECT body FROM comments WHERE id=?", (tid,)).fetchone()
        if c:
            st.info(c["body"][:200])
    elif kind == "user":
        u = conn.execute("SELECT username FROM users WHERE id=?", (tid,)).fetchone()
        if u:
            st.info(f"@{u['username']}")
    elif kind == "stream":
        s = conn.execute("SELECT title FROM live_streams WHERE id=?", (tid,)).fetchone()
        if s:
            st.info(s["title"])
