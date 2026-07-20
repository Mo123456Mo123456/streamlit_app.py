"""Silver — home feed (five sections), story viewer, compose."""
import streamlit as st

from . import ai, auth, services, theme, components
from .i18n import t

SECTION_TABS = [
    ("circle", "sec_circle"), ("front", "sec_front"), ("interests", "sec_interests"),
    ("communities", "sec_communities"), ("nearby", "sec_nearby"),
]


def home_view(conn, user_id: int, lang: str):
    theme.header()
    components.story_bar(conn, user_id, lang)
    st.divider()
    labels = [t(key, lang) for _, key in SECTION_TABS]
    tabs = st.tabs(labels)
    me = auth.get_user(conn, user_id)
    loaders = {
        "circle": lambda: services.feed_circle(conn, user_id),
        "front": lambda: services.feed_front(conn, user_id),
        "interests": lambda: services.feed_interests(conn, user_id),
        "communities": lambda: services.feed_communities(conn, user_id),
        "nearby": lambda: services.feed_nearby(conn, user_id, me["city"]),
    }
    for (slug, _), tab in zip(SECTION_TABS, tabs):
        with tab:
            posts = loaders[slug]()
            if slug == "nearby" and not me["city"]:
                st.info(t("your_city", lang))
            if not posts:
                st.caption(t("no_posts", lang))
            for p in posts:
                components.render_post(conn, p, user_id, lang, key_prefix=f"feed_{slug}")


def story_view(conn, user_id: int, lang: str, author_id: int):
    stories = [s for s in services.visible_stories(conn, user_id) if s["author_id"] == author_id]
    if st.button("← " + t("back", lang)):
        components.goto("home")
    if not stories:
        st.caption(t("expired", lang))
        return
    for s in stories:
        services.mark_story_viewed(conn, s["id"], user_id)
        with st.container(border=True):
            st.markdown(f"**{s['display_name']}** <span class='silver-muted'>@{s['username']}</span>",
                        unsafe_allow_html=True)
            media = services.story_media(conn, s["id"])
            if media:
                try:
                    if media["kind"] == "image":
                        st.image(media["path"], use_container_width=True)
                    else:
                        st.video(media["path"])
                except Exception:
                    st.caption("⚠️ media unavailable")
            if s["body"]:
                st.write(s["body"])
            if s["author_id"] == user_id:
                c1, c2 = st.columns(2)
                c1.caption(f"👁 {services.story_view_count(conn, s['id'])} {t('story_viewers', lang)}")
                if not s["featured"] and c2.button(t("feature_story", lang), key=f"feat_{s['id']}"):
                    services.feature_story(conn, s["id"])
                    st.rerun()
            else:
                with st.form(key=f"sreply_{s['id']}", clear_on_submit=True, border=False):
                    txt = st.text_input(t("reply_story", lang), key=f"sreply_txt_{s['id']}")
                    if st.form_submit_button(t("send", lang)) and txt.strip():
                        if services.can_message(conn, user_id, s["author_id"]):
                            cid = services.get_or_create_direct(conn, user_id, s["author_id"])
                            services.send_message(conn, cid, user_id, txt.strip(), story_id=s["id"])
                            st.success(t("send", lang) + " ✓")
                        else:
                            st.warning(t("cannot_message", lang))


def compose_view(conn, user_id: int, lang: str, tab: str = "post"):
    theme.header()
    st.subheader("➕ " + t("create", lang))
    me = auth.get_user(conn, user_id)
    cats = services.categories(conn)
    kinds = ["post", "story", "live"]
    kind_labels = {"post": t("new_post", lang), "story": t("kind_story", lang), "live": t("kind_live", lang)}
    choice = st.radio("", kinds, format_func=lambda k: kind_labels[k],
                      horizontal=True, index=kinds.index(tab if tab in kinds else "post"),
                      label_visibility="collapsed")

    if choice == "post":
        _compose_post(conn, user_id, me, cats, lang)
    elif choice == "story":
        _compose_story(conn, user_id, lang)
    else:
        _compose_live(conn, user_id, cats, lang)


def _compose_post(conn, user_id, me, cats, lang):
    body = st.text_area(t("post_text", lang), key="compose_body", height=120)

    # Smart assistant: suggestions only, never auto-publish.
    if body.strip():
        sug_section = ai.suggest_section(body, False, me["city"] or "")
        sug_cat = ai.suggest_category(body)
        sug_kw = ai.suggest_keywords(body)
        warnings = ai.sensitive_warnings(body)
        with st.expander("✨ " + t("ai_suggest", lang), expanded=bool(warnings)):
            st.markdown(f"**{t('ai_suggest_section', lang)}:** {t('sec_' + sug_section, lang)}")
            if sug_kw:
                st.markdown(f"**{t('ai_suggest_keywords', lang)}:** " + " ".join(f"`{w}`" for w in sug_kw))
            for w in warnings:
                st.warning("⚠️ " + w)
    else:
        sug_cat = None

    media = st.file_uploader(
        t("upload_media", lang), type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "webm"],
        accept_multiple_files=True, key="compose_media",
    )
    aud_options = ["circle", "front", "interests", "nearby"]
    audiences = st.multiselect(
        t("choose_audiences", lang), aud_options, default=["front"],
        format_func=lambda a: t("sec_" + a, lang),
    )
    cat_ids = [None] + [c["id"] for c in cats]
    default_cat = 0
    if sug_cat:
        for i, c in enumerate(cats):
            if c["slug"] == sug_cat:
                default_cat = i + 1
    category_id = st.selectbox(
        t("choose_category", lang), cat_ids, index=default_cat,
        format_func=lambda cid: "—" if cid is None else services.category_name(
            next(c for c in cats if c["id"] == cid), lang),
    )
    my_comms = services.user_communities(conn, user_id)
    community_id = None
    if my_comms:
        comm_ids = [None] + [c["id"] for c in my_comms]
        community_id = st.selectbox(
            t("choose_community", lang), comm_ids,
            format_func=lambda cid: "—" if cid is None else next(
                c["name"] for c in my_comms if c["id"] == cid),
        )
    is_short = st.toggle(t("kind_short", lang), key="compose_short")
    ai_generated = st.checkbox(t("mark_ai", lang), key="compose_ai")

    if st.button(t("publish", lang), type="primary", disabled=not (body.strip() or media)):
        media_files = [{"path": services.save_upload(user_id, f)} for f in (media or [])]
        has_video = any(m["path"].lower().endswith((".mp4", ".mov", ".webm")) for m in media_files)
        kind = "short_video" if (is_short and has_video) else (
            "video" if has_video else ("image" if media_files else "text"))
        auds = list(audiences)
        if community_id:
            auds.append("communities")
        services.create_post(
            conn, user_id, body.strip(), kind, auds or ["front"],
            category_id=category_id, community_id=community_id,
            city=me["city"] or "", ai_generated=ai_generated, media_files=media_files,
        )
        st.success(t("post_published", lang))
        components.goto("home")


def _compose_story(conn, user_id, lang):
    body = st.text_area(t("post_text", lang), key="story_body", height=80)
    media = st.file_uploader(
        t("upload_media", lang), type=["png", "jpg", "jpeg", "webp", "mp4", "mov", "webm"],
        key="story_media",
    )
    audience = st.radio(
        t("story_audience", lang), ["circle", "followers", "public"],
        format_func=lambda a: {"circle": t("aud_circle_only", lang),
                               "followers": t("aud_followers", lang),
                               "public": t("aud_public", lang)}[a],
        horizontal=True,
    )
    if st.button(t("publish", lang), type="primary", disabled=not (body.strip() or media)):
        path = services.save_upload(user_id, media) if media else ""
        services.create_story(conn, user_id, body.strip(), audience, path)
        st.success(t("story_published", lang))
        components.goto("home")


def _compose_live(conn, user_id, cats, lang):
    st.info("📡 " + t("all_streams_public", lang))
    st.caption(t("live_note", lang))
    with st.form("live_form"):
        title = st.text_input(t("live_title", lang))
        desc = st.text_area(t("live_desc", lang), height=68)
        cat_ids = [None] + [c["id"] for c in cats]
        category_id = st.selectbox(
            t("choose_category", lang), cat_ids,
            format_func=lambda cid: "—" if cid is None else services.category_name(
                next(c for c in cats if c["id"] == cid), lang),
        )
        comments_on = st.toggle(t("live_chat", lang), value=True)
        guests_on = st.toggle(t("join_as_guest", lang), value=True)
        save_rec = st.toggle(t("save_recording", lang), value=True)
        if st.form_submit_button(t("start_live", lang), type="primary") and title.strip():
            sid = services.start_stream(
                conn, user_id, title.strip(), desc.strip(), category_id,
                comments_on, guests_on, save_rec,
            )
            components.goto("live_room", stream_id=sid)
