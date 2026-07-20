"""Silver — visual identity (Tiffany #0ABAB5, white cards, RTL/LTR)."""
import streamlit as st

PRIMARY = "#0ABAB5"
LIGHT_BG = "#EAF9F8"
GRAY_BG = "#F5F7F8"
TEXT = "#14232B"
TEXT_2 = "#6B767C"

LOGO_SVG = (
    '<svg width="42" height="42" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M40 20c0-8.8-7.2-14-16-14S8 11.2 8 18c0 5.5 4 8.6 10.5 10l7 1.5c3.3.7 4.5 1.8 4.5 3.7 '
    '0 2.6-2.9 4.3-6.9 4.3-4.4 0-7.5-1.9-8.1-5.1H7c.5 6.5 5.6 10.8 13.2 11.5L18 49l8.5-5.1C34.9 43.3 '
    '41 38.6 41 32.4c0-5.6-3.8-8.7-10.4-10.1l-7.2-1.6c-3.2-.7-4.6-1.8-4.6-3.8 0-2.5 2.7-4.1 6.4-4.1 '
    '4 0 6.6 1.8 7.2 4.6H40z" fill="#0ABAB5"/>'
    '<circle cx="35" cy="12" r="2.4" fill="#0ABAB5"/>'
    '<circle cx="41" cy="16" r="1.6" fill="#7fd9d6"/></svg>'
)

CSS = f"""
<style>
:root {{
  --silver-primary: {PRIMARY};
  --silver-light: {LIGHT_BG};
  --silver-gray: {GRAY_BG};
  --silver-text: {TEXT};
  --silver-text2: {TEXT_2};
}}
.stApp {{ background: var(--silver-gray); }}
h1, h2, h3, h4 {{ color: var(--silver-text); }}
[data-testid="stSidebar"] {{ background: #ffffff; }}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{ border-radius: 16px; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: #ffffff; border-radius: 16px;
  box-shadow: 0 1px 4px rgba(20,35,43,0.06);
}}
.stButton > button[kind="primary"] {{
  background: var(--silver-primary); border: none; border-radius: 12px; color: #fff;
}}
.stButton > button[kind="primary"]:hover {{ background: #089a96; color: #fff; }}
.stButton > button {{ border-radius: 12px; }}
.silver-header {{
  display: flex; align-items: center; gap: 10px; padding: 4px 0 0 0;
}}
.silver-header .name {{ font-size: 1.5rem; font-weight: 800; color: var(--silver-text); }}
.silver-header .name .ar {{ color: var(--silver-primary); }}
.silver-tag {{
  display: inline-block; background: var(--silver-light); color: {PRIMARY};
  border-radius: 999px; padding: 1px 10px; font-size: 0.75rem; font-weight: 600;
}}
.silver-muted {{ color: var(--silver-text2); font-size: 0.8rem; }}
.story-ring-new {{
  width: 62px; height: 62px; border-radius: 50%;
  border: 3px solid var(--silver-primary);
  display:flex; align-items:center; justify-content:center;
  background: var(--silver-light); font-weight:700; color:{PRIMARY};
  margin: 0 auto;
}}
.story-ring-seen {{
  width: 62px; height: 62px; border-radius: 50%;
  border: 3px solid #c9d2d4;
  display:flex; align-items:center; justify-content:center;
  background: #f0f3f4; font-weight:700; color:#6B767C;
  margin: 0 auto;
}}
.live-badge {{
  background:#e5484d; color:#fff; border-radius:6px; padding:1px 8px;
  font-size:0.72rem; font-weight:700;
}}
.avatar-circle {{
  width: 44px; height: 44px; border-radius: 50%;
  background: var(--silver-light); color: {PRIMARY};
  display:flex; align-items:center; justify-content:center; font-weight:800;
}}
</style>
"""

RTL_CSS = """
<style>
.stApp, [data-testid="stSidebar"] { direction: rtl; }
.stMarkdown, p, h1, h2, h3, h4, label, .stCaption { text-align: right; }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { direction: rtl; }
</style>
"""


def apply(lang: str) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    if lang == "ar":
        st.markdown(RTL_CSS, unsafe_allow_html=True)


def header() -> None:
    st.markdown(
        f'<div class="silver-header">{LOGO_SVG}'
        f'<span class="name">Silver <span class="ar">سيلفر</span></span></div>',
        unsafe_allow_html=True,
    )


def avatar_html(name: str) -> str:
    initial = (name or "?").strip()[:1].upper()
    return f'<div class="avatar-circle">{initial}</div>'
