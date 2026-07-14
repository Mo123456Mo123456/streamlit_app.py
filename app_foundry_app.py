"""
🧪 مصنع التطبيقات الفورية — Instant App Foundry
ورشة تحوّل وصف العميل بالعربي إلى تطبيق ويب كامل في ملف HTML واحد
يعمل على أي جهاز بدون استضافة — تبيعه كبرمجة مخصصة على مستقل/خمسات.

التشغيل:  streamlit run app_foundry_app.py
"""

import os

import streamlit as st
import streamlit.components.v1 as components

from app_foundry import db, engine, templates

# ---------------------------------------------------------------- الإعداد

st.set_page_config(page_title="مصنع التطبيقات الفورية", page_icon="🧪", layout="wide")
db.init_db()

st.markdown(
    """
    <style>
      .stApp, section[data-testid="stSidebar"] { direction: rtl; text-align: right; }
      .stTabs [data-baseweb="tab-list"] { direction: rtl; }
      textarea, input { direction: rtl; }
      .foundry-hero {
        background: linear-gradient(120deg, #1a1033 0%, #2d1b5e 55%, #00c9a7 170%);
        color: #fff; padding: 26px 32px; border-radius: 16px; margin-bottom: 8px;
      }
      .foundry-hero h1 { margin: 0 0 6px 0; font-size: 1.7rem; }
      .foundry-hero p { margin: 0; opacity: .92; }
    </style>
    <div class="foundry-hero">
      <h1>🧪 مصنع التطبيقات الفورية</h1>
      <p>حوّل طلب العميل إلى تطبيق ويب كامل في ملف واحد — عاينه، عدّله، وسلّمه كبرمجة مخصصة بأسعار المبرمجين.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "") or st.session_state.get("api_key_input", "")


with st.sidebar:
    st.header("⚙️ الإعدادات")
    if get_api_key() and "api_key_input" not in st.session_state:
        st.success("✅ مفتاح API مضبوط")
    st.text_input("مفتاح Anthropic API", type="password", key="api_key_input",
                  placeholder="sk-ant-...")
    model = st.selectbox("النموذج", list(engine.MODELS.keys()),
                         format_func=lambda m: engine.MODELS[m], index=0)
    st.caption("💰 تكلفة بناء تطبيق كامل: عادة أقل من دولار واحد — وتبيعه بعشرات الدولارات.")
    st.divider()
    st.metric("💵 أرباح المشاريع المُسلَّمة", f"${db.total_earnings():,.2f}")

API_KEY = get_api_key()


def require_key() -> bool:
    if not API_KEY:
        st.warning("🔑 أدخل مفتاح Anthropic API في الشريط الجانبي أولًا.")
        return False
    return True


tab_build, tab_sales, tab_projects, tab_guide = st.tabs(
    ["🧪 الورشة", "💼 مساعد البيع", "📦 مشاريعي", "🗺️ دليل البيع"]
)

# ================================================================ 1) الورشة

with tab_build:
    st.subheader("ابنِ تطبيق العميل")

    tpl_name = st.selectbox("نوع التطبيق (قوالب الأكثر طلبًا)", list(templates.TEMPLATES.keys()))
    tpl = templates.TEMPLATES[tpl_name]
    if tpl["brief"]:
        st.caption(f"💲 السعر السوقي: **{tpl['price']}** — 🎯 من يشتريه: {tpl['buyers']}")

    c1, c2, c3 = st.columns(3)
    with c1:
        b_title = st.text_input("اسم التطبيق / العميل", placeholder="مثال: حاسبة مكتب النخبة العقاري")
    with c2:
        b_brand = st.text_input("الهوية البصرية (اختياري)",
                                placeholder="مثال: ألوان ذهبي وأسود، طابع فاخر")
    with c3:
        b_language = st.selectbox("لغة الواجهة", ["العربية", "English", "عربي + English"])

    b_brief = st.text_area(
        "وصف الطلب (عدّل القالب أو الصق طلب العميل حرفيًا)",
        value=tpl["brief"], height=200,
    )

    if st.button("🚀 ابنِ التطبيق الآن", type="primary", use_container_width=True):
        if require_key() and b_brief.strip():
            prompt = engine.BUILD_PROMPT.format(
                title=b_title or "تطبيق العميل", kind=tpl_name,
                language=b_language, brand=b_brand or "اختر أنت لوحة ألوان راقية تناسب المجال",
                brief=b_brief,
            )
            with st.expander("👨‍💻 الكود يُكتب الآن مباشرة...", expanded=True):
                raw = st.write_stream(engine.stream_call(API_KEY, model, engine.SYSTEM_BUILDER, prompt))
            code = engine.extract_html(raw)
            if code:
                st.session_state["foundry_code"] = code
                st.session_state["foundry_title"] = b_title or "تطبيق العميل"
                st.session_state["foundry_kind"] = tpl_name
                st.session_state["foundry_pid"] = db.save_project(
                    b_title or "تطبيق العميل", tpl_name, code
                )
                st.rerun()
            else:
                st.error("لم أستطع استخراج كود HTML من الرد — أعد المحاولة أو جرّب نموذجًا أقوى.")
        elif not b_brief.strip():
            st.error("اكتب وصف الطلب أولًا.")

    # -------- المعاينة والتسليم والتعديل (تظهر بعد أول بناء ناجح)
    if st.session_state.get("foundry_code"):
        code = st.session_state["foundry_code"]
        title = st.session_state.get("foundry_title", "app")

        st.markdown(f"### 📱 معاينة حية: {title}")
        warnings = engine.validate_html(code)
        if warnings:
            st.warning("فحص الجودة: " + " • ".join(warnings))
        else:
            st.success("✅ فحص الجودة: ملف واحد مكتفٍ ذاتيًا — يعمل بدون إنترنت.")

        components.html(code, height=640, scrolling=True)

        d1, d2 = st.columns(2)
        d1.download_button(
            "⬇️ تحميل التطبيق (HTML) — جاهز للتسليم", code,
            file_name="app.html", mime="text/html", use_container_width=True,
        )
        with d2:
            with st.popover("📤 كيف أسلّمه للعميل؟", use_container_width=True):
                st.markdown(
                    "- **كملف:** أرسل `app.html` عبر واتساب/تيليجرام — يفتحه بأي متصفح.\n"
                    "- **كرابط دائم:** ارفعه مجانًا على Netlify Drop أو GitHub Pages.\n"
                    "- **كباركود:** حوّل الرابط إلى QR بأي مولد مجاني."
                )

        st.markdown("#### 🔧 طلب تعديل (كرر حتى يرضى العميل)")
        change = st.text_area("ماذا يريد العميل تغييره؟", height=90, key="change_req",
                              placeholder="مثال: غيّر الألوان إلى أزرق داكن، وأضف حقل خصم 10%")
        if st.button("♻️ طبّق التعديل", use_container_width=True):
            if require_key() and change.strip():
                prompt = engine.REFINE_PROMPT.format(code=code, change=change)
                with st.expander("👨‍💻 يُعدَّل الآن...", expanded=True):
                    raw = st.write_stream(
                        engine.stream_call(API_KEY, model, engine.SYSTEM_BUILDER, prompt)
                    )
                new_code = engine.extract_html(raw)
                if new_code:
                    st.session_state["foundry_code"] = new_code
                    if st.session_state.get("foundry_pid"):
                        db.update_code(st.session_state["foundry_pid"], new_code)
                    st.rerun()
                else:
                    st.error("لم أستطع استخراج الكود المعدَّل — أعد المحاولة.")

# ================================================================ 2) مساعد البيع

with tab_sales:
    st.subheader("حوّل مشروعًا منشورًا على مستقل إلى عرض فائز")
    st.caption("افتح mostaql.com أو khamsat.com → انسخ نص أي مشروع برمجة بسيط → الصقه هنا.")
    project_text = st.text_area("نص المشروع كما نشره صاحبه", height=200,
                                placeholder="الصق نص المشروع هنا...")
    if st.button("💼 اكتب لي العرض + السعر", type="primary", use_container_width=True):
        if require_key() and project_text.strip():
            with st.container(border=True):
                result = st.write_stream(engine.stream_call(
                    API_KEY, model, engine.SYSTEM_SALES,
                    engine.PROPOSAL_PROMPT.format(project_text=project_text),
                    max_tokens=8000,
                ))
                st.session_state["proposal_text"] = result
        elif not project_text.strip():
            st.error("الصق نص المشروع أولًا.")
    if st.session_state.get("proposal_text"):
        st.download_button("⬇️ تحميل العرض", st.session_state["proposal_text"],
                           file_name="proposal.md", use_container_width=True)

# ================================================================ 3) مشاريعي

with tab_projects:
    st.subheader("سجل المشاريع والأرباح")
    projects = db.list_projects()
    if not projects:
        st.info("لا مشاريع بعد — ابنِ أول تطبيق من تبويب الورشة 🧪")
    else:
        st.dataframe(
            [{"#": p["id"], "التاريخ": p["created_at"], "التطبيق": p["title"],
              "النوع": p["kind"], "السعر $": p["price_usd"], "الحالة": p["status"]}
             for p in projects],
            use_container_width=True, hide_index=True,
        )
        st.markdown("#### تحديث حالة مشروع")
        u1, u2, u3, u4 = st.columns([1, 1, 1, 1])
        with u1:
            sel_id = st.selectbox("رقم المشروع", [p["id"] for p in projects])
        with u2:
            sel_status = st.selectbox("الحالة", ["قيد العمل", "أُرسل للعميل", "مُسلَّم ومدفوع"])
        with u3:
            sel_price = st.number_input("المبلغ المدفوع $", min_value=0.0, step=5.0)
        with u4:
            st.write("")
            if st.button("💾 تحديث", use_container_width=True):
                db.update_status(sel_id, sel_status, sel_price if sel_price > 0 else None)
                st.rerun()
        code = db.get_code(sel_id)
        if code:
            st.download_button(f"⬇️ إعادة تحميل ملف المشروع #{sel_id}", code,
                               file_name=f"project_{sel_id}.html", mime="text/html")

# ================================================================ 4) دليل البيع

with tab_guide:
    st.subheader("كيف تبيع برمجة وأنت على جوالك — خطة 14 يومًا")
    st.markdown(
        """
> **الفكرة في سطر:** أنت الآن تملك ما يعادل فريق مبرمجين يسلّم خلال ساعة. العملاء موجودون فعلًا
> على مستقل وخمسات ويدفعون أسعار برمجة — أنت فقط توصل بين طلبهم وبين الورشة.

### الأيام 1-2: جهّز عدّتك
1. ابنِ من الورشة **3 تطبيقات نموذجية** (منيو مطعم + حاسبة عقارية + بطاقة أعمال) كنماذج تعرضها.
2. ارفعها على Netlify Drop (سحب وإفلات من الجوال) لتحصل على روابط حية تريها للعملاء.
3. أنشئ حسابك على **مستقل** و**خمسات** بمعرض أعمال من هذه الروابط الثلاثة.

### الأيام 3-14: دورة البيع اليومية (30-60 دقيقة يوميًا)
1. تصفح مشاريع البرمجة الجديدة على مستقل (فلتر: تطوير مواقع، أقل من 500$).
2. أي مشروع يمكن تسليمه كملف واحد → انسخ نصه إلى **مساعد البيع** → قدّم العرض الجاهز.
3. عند القبول: ابنِ التطبيق في الورشة → أرسل **لقطة شاشة + رابط معاينة** → طبّق تعديلاته → سلّم الملف.
4. سجّل الحالة في **مشاريعي** واطلب تقييمًا 5 نجوم.

### قواعد ذهبية
- **سلّم أسرع مما وعدت** — وعدت 48 ساعة؟ سلّم في 12. هذا وحده يبني تقييماتك.
- **راجع التطبيق بنفسك قبل التسليم** — جرّب كل زر. أنت المسؤول أمام العميل، ليس الأداة.
- **لا تنافس على السعر الأرخص** — نافس على «ملف واحد، بدون استضافة شهرية، تسليم فوري، تعديلات مجانية».
- في خمسات: انشر الخدمات كقوالب جاهزة («منيو رقمي لمطعمك بـ 5$ + إضافات») — الإضافات هي الربح الحقيقي.

### التوسع بعد أول 10 مشاريع
- ارفع أسعارك 50% مع كل 5 تقييمات.
- المنتجات الاستهلاكية (دعوات الزفاف): افتح معرضًا على إنستغرام/تيك توك — كل دعوة تُصنع بدقائق وتُباع 20-70$.
- المرحلة التالية: تطبيقات تيليجرام المصغّرة للتجار (اطلبها مني وأضيفها للورشة).
        """
    )
