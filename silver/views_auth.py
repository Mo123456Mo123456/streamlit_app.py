"""Silver — login / registration / onboarding views."""
import streamlit as st

from . import auth, services, theme
from .i18n import t


def auth_view(conn, lang: str):
    theme.header()
    st.caption(t("tagline", lang))
    tab_login, tab_register = st.tabs([t("login", lang), t("register", lang)])

    with tab_login:
        with st.form("login_form"):
            ident = st.text_input(t("identifier", lang))
            pwd = st.text_input(t("password", lang), type="password")
            if st.form_submit_button(t("login", lang), type="primary"):
                user, err = auth.login(conn, ident, pwd)
                if user is None:
                    st.error(t(err, lang))
                else:
                    st.session_state["user_id"] = user["id"]
                    settings = conn.execute(
                        "SELECT language FROM user_settings WHERE user_id=?", (user["id"],)
                    ).fetchone()
                    if settings:
                        st.session_state["lang"] = settings["language"]
                    st.session_state["view"] = "home"
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            name = st.text_input(t("display_name", lang))
            username = st.text_input(t("username", lang))
            email = st.text_input(t("email", lang))
            pwd = st.text_input(t("password", lang), type="password")
            if st.form_submit_button(t("register", lang), type="primary"):
                uid, err = auth.register(conn, username, email, pwd, name)
                if uid is None:
                    st.error(t(err, lang))
                else:
                    st.session_state["user_id"] = uid
                    st.session_state["view"] = "onboarding"
                    st.success(t("account_created", lang))
                    st.rerun()


def onboarding_view(conn, user_id: int, lang: str):
    theme.header()
    st.subheader(t("pick_interests", lang))
    cats = services.categories(conn)
    chosen = st.multiselect(
        t("pick_interests", lang), [c["id"] for c in cats],
        format_func=lambda cid: services.category_name(
            next(c for c in cats if c["id"] == cid), lang),
        label_visibility="collapsed",
    )
    city = st.text_input(t("your_city", lang))
    bio = st.text_area(t("bio", lang), max_chars=200)
    avatar = st.file_uploader(t("upload_media", lang), type=["png", "jpg", "jpeg", "webp"])
    if st.button(t("continue", lang), type="primary"):
        for cid in chosen:
            conn.execute("INSERT OR IGNORE INTO user_interests (user_id, category_id) VALUES (?,?)",
                         (user_id, cid))
        avatar_path = services.save_upload(user_id, avatar) if avatar else ""
        conn.execute(
            "UPDATE profiles SET city=?, bio=?, avatar_path=COALESCE(NULLIF(?,'') , avatar_path) WHERE user_id=?",
            (city.strip(), bio.strip(), avatar_path, user_id),
        )
        conn.commit()
        st.session_state["view"] = "home"
        st.rerun()
