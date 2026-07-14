"""
🏭 مصنع الدخل الرقمي — Digital Income Factory
تطبيق يحوّل الذكاء الاصطناعي إلى خط إنتاج لأشياء تُباع فعليًا:
منتجات رقمية جاهزة للرفع على Gumroad/Payhip، وخدمات جاهزة للتقديم
على خمسات/مستقل/Fiverr، مع حزم تسويق ولوحة أرباح.

التشغيل:  streamlit run income_factory_app.py
"""

import os

import streamlit as st

from income_factory import db, export, llm, prompts

# ---------------------------------------------------------------- الإعداد العام

st.set_page_config(page_title="مصنع الدخل الرقمي", page_icon="🏭", layout="wide")
db.init_db()

st.markdown(
    """
    <style>
      .stApp, section[data-testid="stSidebar"] { direction: rtl; text-align: right; }
      .stTabs [data-baseweb="tab-list"] { direction: rtl; }
      div[data-testid="stMetric"] { direction: rtl; text-align: right; }
      textarea, input { direction: rtl; }
      .factory-hero {
        background: linear-gradient(120deg, #0f3d5c 0%, #14507a 60%, #d9a441 160%);
        color: #fff; padding: 26px 32px; border-radius: 16px; margin-bottom: 8px;
      }
      .factory-hero h1 { margin: 0 0 6px 0; font-size: 1.7rem; }
      .factory-hero p { margin: 0; opacity: .92; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="factory-hero">
      <h1>🏭 مصنع الدخل الرقمي</h1>
      <p>ولّد منتجات رقمية وخدمات جاهزة للبيع خلال دقائق — ثم ارفعها على Gumroad / Payhip / خمسات / Fiverr وابدأ البيع.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    """يبحث عن مفتاح API بالترتيب: أسرار Streamlit ← متغير البيئة ← إدخال المستخدم."""
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "") or st.session_state.get("api_key_input", "")


# ---------------------------------------------------------------- الشريط الجانبي

with st.sidebar:
    st.header("⚙️ الإعدادات")
    stored_key = get_api_key()
    if stored_key and "api_key_input" not in st.session_state:
        st.success("✅ مفتاح API مضبوط (من الأسرار أو البيئة)")
    st.text_input(
        "مفتاح Anthropic API",
        type="password",
        key="api_key_input",
        placeholder="sk-ant-...",
        help="احصل على مفتاح من console.anthropic.com — ميزانية 20$ تكفي لمئات المنتجات.",
    )
    model = st.selectbox(
        "النموذج",
        options=list(llm.MODELS.keys()),
        format_func=lambda m: llm.MODELS[m],
        index=0,
    )
    st.caption(
        "💡 نصيحة: استخدم **Haiku** للتجارب الرخيصة، و**Opus 4.8** أو **Fable 5** "
        "للمنتج النهائي الذي ستبيعه."
    )
    st.divider()
    st.markdown(
        "**أين تبيع؟**\n"
        "- 🛒 [Gumroad](https://gumroad.com) — منتجات رقمية (مجاني)\n"
        "- 🛒 [Payhip](https://payhip.com) — منتجات رقمية (مجاني)\n"
        "- 💼 [خمسات](https://khamsat.com) — خدمات مصغرة بالعربية\n"
        "- 💼 [مستقل](https://mostaql.com) — مشاريع عربية\n"
        "- 💼 [Fiverr](https://fiverr.com) — خدمات عالمية"
    )

API_KEY = get_api_key()


def require_key() -> bool:
    if not API_KEY:
        st.warning("🔑 أدخل مفتاح Anthropic API في الشريط الجانبي أولًا حتى يعمل التوليد.")
        return False
    return True


def stream_to_state(state_key: str, system: str, prompt: str, max_tokens: int = 32000):
    """يولّد المحتوى متدفقًا على الشاشة ويحفظه في الجلسة حتى لا يضيع عند إعادة التحميل."""
    text = st.write_stream(llm.stream_generate(API_KEY, model, system, prompt, max_tokens))
    st.session_state[state_key] = text
    return text


# ---------------------------------------------------------------- التبويبات

tab_product, tab_cv, tab_marketing, tab_dashboard, tab_guide = st.tabs(
    ["🏭 منتج رقمي للبيع", "💼 خدمات السيرة الذاتية", "📣 مصنع التسويق", "📊 لوحة الأرباح", "🗺️ خطة الربح"]
)

# ================================================================ 1) منتج رقمي

with tab_product:
    st.subheader("ولّد منتجًا رقميًا كاملًا + حزمة إطلاقه التسويقية")
    c1, c2 = st.columns(2)
    with c1:
        p_kind = st.selectbox("نوع المنتج", list(prompts.PRODUCT_TYPES.keys()))
        p_niche = st.text_input("المجال / التخصص", placeholder="مثال: التجارة الإلكترونية للمبتدئين في الخليج")
    with c2:
        p_audience = st.text_input("الجمهور المستهدف", placeholder="مثال: أصحاب المشاريع الصغيرة")
        p_language = st.selectbox("لغة المنتج", ["العربية", "English", "العربية + English"])

    if st.button("🚀 توليد المنتج + حزمة التسويق", type="primary", use_container_width=True):
        if require_key() and p_niche.strip():
            st.markdown("### 📄 المنتج")
            with st.container(border=True):
                product_prompt = prompts.PRODUCT_TYPES[p_kind].format(
                    niche=p_niche, audience=p_audience or "الجمهور العام", language=p_language
                )
                product_text = stream_to_state("product_text", prompts.SYSTEM_PRODUCT, product_prompt)

            st.markdown("### 📣 حزمة الإطلاق التسويقية")
            with st.container(border=True):
                kit_prompt = prompts.MARKETING_KIT.format(
                    summary=product_text[:3000], language=p_language
                )
                stream_to_state("kit_text", prompts.SYSTEM_MARKETING, kit_prompt, max_tokens=16000)

            db.add_product(p_kind, p_niche, p_language)
            st.session_state["product_meta"] = {"kind": p_kind, "niche": p_niche, "language": p_language}
            st.success("✅ تم التوليد وحُفظ سجل المنتج في لوحة الأرباح. حمّل الحزمة بالأسفل.")
        elif not p_niche.strip():
            st.error("اكتب المجال / التخصص أولًا.")

    if st.session_state.get("product_text"):
        meta = st.session_state.get("product_meta", {})
        title = f"{meta.get('kind', 'منتج رقمي')} — {meta.get('niche', '')}"
        arabic = meta.get("language", "العربية") != "English"
        files = {
            "المنتج/product.md": st.session_state["product_text"],
            "المنتج/product.html": export.markdown_to_html(title, st.session_state["product_text"], arabic),
            "التسويق/marketing_kit.md": st.session_state.get("kit_text", ""),
            "اقرأني.txt": (
                "حزمة منتج رقمي جاهزة للبيع 🏭\n"
                "1) افتح product.html في المتصفح واطبعه كـ PDF (Ctrl+P → Save as PDF).\n"
                "2) ارفع ملف PDF على Gumroad أو Payhip كمنتج رقمي.\n"
                "3) انسخ صفحة البيع من marketing_kit.md إلى صفحة المنتج.\n"
                "4) انشر منشورات الإطلاق الجاهزة من نفس الملف.\n"
            ),
        }
        st.download_button(
            "⬇️ تحميل حزمة المنتج كاملة (ZIP)",
            data=export.build_zip(files),
            file_name="digital_product_package.zip",
            mime="application/zip",
            use_container_width=True,
        )

# ================================================================ 2) خدمات CV

with tab_cv:
    st.subheader("خدمة جاهزة تبيعها: تحسين السير الذاتية بالذكاء الاصطناعي")
    st.caption(
        "هذه خدمة مطلوبة جدًا على خمسات وFiverr (5$–30$ للطلب الواحد). "
        "الصق سيرة العميل هنا وسلّمه النتيجة خلال دقائق."
    )
    cv_text = st.text_area("نص السيرة الذاتية", height=220, placeholder="الصق نص السيرة الذاتية هنا...")
    job_desc = st.text_area("الوصف الوظيفي المستهدف (اختياري)", height=120,
                            placeholder="الصق إعلان الوظيفة لتخصيص السيرة (اختياري)")
    cv_lang = st.selectbox("لغة السيرة النهائية", ["العربية", "English"], key="cv_lang")

    if st.button("✨ تحسين السيرة + خطاب تقديم", type="primary", use_container_width=True):
        if require_key() and cv_text.strip():
            with st.container(border=True):
                job_block = (
                    f"وهذا الوصف الوظيفي المستهدف:\n\n---\n{job_desc}\n---\n\n" if job_desc.strip() else ""
                )
                stream_to_state(
                    "cv_result",
                    prompts.SYSTEM_CV,
                    prompts.CV_OPTIMIZE.format(cv=cv_text, job_block=job_block, language=cv_lang),
                    max_tokens=16000,
                )
            st.success("✅ جاهزة للتسليم — حمّلها بالأسفل.")
        elif not cv_text.strip():
            st.error("الصق نص السيرة الذاتية أولًا.")

    if st.session_state.get("cv_result"):
        cc1, cc2 = st.columns(2)
        cc1.download_button(
            "⬇️ تحميل (Markdown)", st.session_state["cv_result"],
            file_name="optimized_cv.md", use_container_width=True,
        )
        cc2.download_button(
            "⬇️ تحميل (HTML للطباعة PDF)",
            export.markdown_to_html("السيرة الذاتية المحسّنة", st.session_state["cv_result"],
                                    arabic=st.session_state.get("cv_lang", "العربية") == "العربية"),
            file_name="optimized_cv.html", use_container_width=True,
        )

    st.divider()
    st.markdown("#### 🏪 أنشئ عرض خدمتك على المنصات (مرة واحدة)")
    g1, g2 = st.columns(2)
    with g1:
        gig_service = st.text_input("الخدمة التي ستبيعها",
                                    value="تحسين السيرة الذاتية واجتياز أنظمة ATS خلال 24 ساعة")
    with g2:
        gig_tools = st.text_input("خبرتك / أدواتك", value="أدوات ذكاء اصطناعي احترافية + مراجعة يدوية")
    if st.button("🏪 توليد عرض الخدمة (خمسات + Fiverr)", use_container_width=True):
        if require_key():
            with st.container(border=True):
                stream_to_state(
                    "gig_result", prompts.SYSTEM_GIG,
                    prompts.GIG_LISTING.format(service=gig_service, tools=gig_tools),
                    max_tokens=8000,
                )
    if st.session_state.get("gig_result"):
        st.download_button("⬇️ تحميل عرض الخدمة", st.session_state["gig_result"],
                           file_name="gig_listing.md", use_container_width=True)

# ================================================================ 3) التسويق

with tab_marketing:
    st.subheader("حزمة تسويق كاملة لأي منتج أو خدمة")
    m_product = st.text_area("صف منتجك أو خدمتك", height=120,
                             placeholder="مثال: حزمة 50 برومبت للتجارة الإلكترونية أبيعها على Gumroad بـ 9$")
    m1, m2, m3 = st.columns(3)
    with m1:
        m_audience = st.text_input("الجمهور", placeholder="أصحاب المتاجر الإلكترونية", key="mk_aud")
    with m2:
        m_platform = st.selectbox("المنصة", ["X (تويتر)", "Instagram", "TikTok", "LinkedIn", "Snapchat"])
    with m3:
        m_language = st.selectbox("اللغة", ["العربية", "English"], key="mk_lang")

    if st.button("📣 توليد حزمة التسويق", type="primary", use_container_width=True):
        if require_key() and m_product.strip():
            with st.container(border=True):
                stream_to_state(
                    "mk_result", prompts.SYSTEM_MARKETING,
                    prompts.MARKETING_STANDALONE.format(
                        product=m_product, audience=m_audience or "الجمهور العام",
                        platform=m_platform, language=m_language,
                    ),
                    max_tokens=16000,
                )
        elif not m_product.strip():
            st.error("صف المنتج أو الخدمة أولًا.")
    if st.session_state.get("mk_result"):
        st.download_button("⬇️ تحميل حزمة التسويق", st.session_state["mk_result"],
                           file_name="marketing_pack.md", use_container_width=True)

# ================================================================ 4) لوحة الأرباح

with tab_dashboard:
    st.subheader("تتبّع منتجاتك وطلباتك وأرباحك")
    orders = db.list_orders()
    products = db.list_products()

    k1, k2, k3 = st.columns(3)
    k1.metric("💰 إجمالي الأرباح", f"${db.total_revenue():,.2f}")
    k2.metric("📦 الطلبات المسجلة", len(orders))
    k3.metric("🏭 المنتجات المولّدة", len(products))

    st.markdown("#### ➕ سجّل عملية بيع جديدة")
    with st.form("order_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            o_platform = st.selectbox("المنصة", ["Gumroad", "Payhip", "خمسات", "مستقل", "Fiverr", "مباشر", "أخرى"])
        with f2:
            o_item = st.text_input("ماذا بعت؟", placeholder="حزمة برومبتات / تحسين سيرة ذاتية ...")
        with f3:
            o_amount = st.number_input("المبلغ (دولار)", min_value=0.0, step=1.0)
        o_notes = st.text_input("ملاحظات (اختياري)")
        if st.form_submit_button("💾 حفظ العملية", use_container_width=True):
            if o_item.strip() and o_amount > 0:
                db.add_order(o_platform, o_item, o_amount, o_notes)
                st.success("تم تسجيل البيع! 🎉")
                st.rerun()
            else:
                st.error("أدخل اسم ما بعته ومبلغًا أكبر من صفر.")

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 🧾 سجل المبيعات")
        if orders:
            st.dataframe(
                [{"التاريخ": o["created_at"], "المنصة": o["platform"], "الخدمة/المنتج": o["item"],
                  "المبلغ $": o["amount_usd"], "ملاحظات": o["notes"]} for o in orders],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("لا مبيعات مسجلة بعد — أول عملية بيع تبدأ من تبويب «خطة الربح» 🗺️")
    with d2:
        st.markdown("#### 🏭 المنتجات المولّدة")
        if products:
            st.dataframe(
                [{"التاريخ": p["created_at"], "النوع": p["kind"], "المجال": p["niche"],
                  "اللغة": p["language"]} for p in products],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("لم تولّد منتجات بعد — ابدأ من تبويب «منتج رقمي للبيع» 🏭")

# ================================================================ 5) خطة الربح

with tab_guide:
    st.subheader("خطة واقعية لتحويل 20$ إلى دخل متكرر")
    st.markdown(
        """
> ⚠️ **بصراحة تامة:** لا توجد أداة تطبع المال تلقائيًا. هذا التطبيق يصنع لك **المنتج والخدمة والتسويق**
> خلال دقائق بدل أيام — لكن البيع الأول يحتاج منك نشرًا ومتابعة. الميزانية الوحيدة المطلوبة هي
> رصيد API (والـ 20$ تكفي لمئات عمليات التوليد). كل المنصات المقترحة مجانية.

### 🥇 المسار الأسرع للدولار الأول: الخدمات (أسبوعك الأول)
1. من تبويب **خدمات السيرة الذاتية** ولّد عرض خدمتك، وانشره على **خمسات** و**Fiverr** (مجانًا).
2. سعّر أول 5 طلبات بسعر منخفض (5$) لجمع التقييمات بسرعة.
3. عند وصول طلب: الصق سيرة العميل في التطبيق → سلّم النتيجة خلال ساعة → اطلب تقييمًا.
4. بعد 5 تقييمات ارفع السعر تدريجيًا (10$ ثم 20$).
   - **الحسبة:** 10 طلبات شهريًا × 10$ = 100$ شهريًا من خدمة واحدة، وتكلفة كل طلب من رصيد API سنتات معدودة.

### 🥈 الدخل شبه التلقائي: المنتجات الرقمية (من الأسبوع الثاني)
1. من تبويب **منتج رقمي للبيع** ولّد منتجًا في مجال تعرفه (حزمة برومبتات أو دليل عملي).
2. راجعه وحسّنه بلمستك (15 دقيقة) — هذا ما يميزك عن المنافسين.
3. افتح `product.html` → اطبعه PDF → ارفعه على **Gumroad/Payhip** بسعر 7$–15$.
4. انشر منشورات الإطلاق الجاهزة من حزمة التسويق، وكرر منتجًا جديدًا كل أسبوع.
   - المنتج الرقمي **يُباع وأنت نائم** — هذا هو الجزء "شبه التلقائي" الحقيقي.

### 🥉 التوسع (الشهر الثاني+)
- كل منتج ناجح: أنشئ نسخة إنجليزية منه (نفس التطبيق، غيّر اللغة) لتضاعف السوق.
- استخدم تبويب **مصنع التسويق** لعمل محتوى يومي يجذب الزوار لصفحاتك.
- سجّل كل عملية بيع في **لوحة الأرباح** لتعرف أي المنتجات تستحق التكرار.

### 💡 لماذا هذا المسار أفضل من "تطبيق ويب بالاشتراكات"؟
بناء SaaS يحتاج بوابة دفع وشركة مسجلة وتسويقًا طويلًا قبل أول دولار.
هذا المسار يستخدم منصات **جاهزة الدفع والجمهور** (خمسات/Gumroad) — فتصل للدولار الأول في أيام، لا شهور.
        """
    )
