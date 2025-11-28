"""
🤖 وكيل الذكاء الاصطناعي المتكامل
واجهة Streamlit احترافية وعصرية
"""

import streamlit as st
import time
import json
from datetime import datetime
import sys
import os

# إضافة المسار للوصول إلى الوحدات
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_agent.agent_core import AIAgent
from ai_agent.tools import ToolManager

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ إعدادات الصفحة
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="وكيل الذكاء الاصطناعي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 التنسيقات المخصصة
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* المتغيرات */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-input: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-color: #475569;
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    /* الجسم الرئيسي */
    .stApp {
        background: var(--bg-dark);
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    
    /* إخفاء الهيدر والفوتر */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* الشريط الجانبي */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
        border-left: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* العنوان الرئيسي */
    .main-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, #a78bfa 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.2rem;
    }
    
    /* بطاقة الأدوات */
    .tool-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .tool-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .tool-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tool-name {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    
    .tool-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* رسائل المحادثة */
    .chat-container {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .agent-message {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        max-width: 85%;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .agent-message code {
        background: var(--bg-input);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
    
    /* حقل الإدخال */
    .stTextInput > div > div > input {
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 15px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1.1rem !important;
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* الأزرار */
    .stButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Tajawal', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* الإحصائيات */
    .stat-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* الأقسام */
    .section-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-color);
        display: inline-block;
    }
    
    /* تأثير التحميل */
    .typing-indicator {
        display: flex;
        gap: 0.3rem;
        padding: 1rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--primary-color);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* تأثيرات الخلفية */
    .glow-effect {
        position: fixed;
        width: 500px;
        height: 500px;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.15;
        pointer-events: none;
        z-index: -1;
    }
    
    .glow-1 {
        background: #6366f1;
        top: -100px;
        right: -100px;
    }
    
    .glow-2 {
        background: #8b5cf6;
        bottom: -100px;
        left: -100px;
    }
    
    /* الميتريكس */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    [data-testid="stMetricValue"] {
        color: var(--accent-color) !important;
    }
    
    /* التنبيهات */
    .stAlert {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* الكود */
    code {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border-color: var(--border-color) !important;
        border-radius: 10px !important;
    }
    
    /* المساحة */
    .spacer {
        height: 2rem;
    }
    
    /* أنيميشن الظهور */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
</style>

<!-- تأثيرات الخلفية -->
<div class="glow-effect glow-1"></div>
<div class="glow-effect glow-2"></div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 تهيئة الحالة
# ═══════════════════════════════════════════════════════════════════════════════

if 'agent' not in st.session_state:
    st.session_state.agent = AIAgent()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'tool_manager' not in st.session_state:
    st.session_state.tool_manager = ToolManager()

# ═══════════════════════════════════════════════════════════════════════════════
# 📱 الشريط الجانبي
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0;">🤖</h1>
        <h2 style="color: #a78bfa; font-size: 1.5rem; margin: 0;">وكيلك الذكي</h2>
        <p style="color: #94a3b8; font-size: 0.9rem;">مساعدك الشخصي بالذكاء الاصطناعي</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # إعدادات API
    st.markdown("### ⚙️ الإعدادات")
    
    provider = st.selectbox(
        "مزود الخدمة",
        ["local", "openai", "anthropic"],
        index=0,
        help="اختر مزود خدمة الذكاء الاصطناعي"
    )
    
    api_key = ""
    if provider != "local":
        api_key = st.text_input(
            f"🔑 مفتاح API لـ {provider}",
            type="password",
            help="أدخل مفتاح API الخاص بك"
        )
        
        if api_key:
            st.session_state.agent = AIAgent(api_key=api_key, provider=provider)
            st.success("✅ تم الاتصال!")
    
    st.markdown("---")
    
    # الأدوات المتاحة
    st.markdown("### 🛠️ الأدوات المتاحة")
    
    tools_info = [
        ("🧮", "الآلة الحاسبة", "حسابات متقدمة"),
        ("🌐", "البحث", "بحث على الإنترنت"),
        ("📚", "ويكيبيديا", "معلومات موثوقة"),
        ("🌤️", "الطقس", "أحوال الجو"),
        ("🕐", "الوقت", "التاريخ والساعة"),
        ("💱", "العملات", "تحويل العملات"),
        ("🌍", "الترجمة", "ترجمة النصوص"),
        ("📝", "التحليل", "تحليل النصوص"),
        ("🔐", "التشفير", "تشفير وفك تشفير"),
        ("📊", "الرسوم", "رسوم بيانية"),
    ]
    
    for emoji, name, desc in tools_info:
        st.markdown(f"""
        <div style="
            background: rgba(99, 102, 241, 0.1);
            padding: 0.5rem 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
        ">
            <span style="font-size: 1.2rem;">{emoji}</span>
            <span style="color: #f1f5f9; font-weight: 600; margin: 0 0.5rem;">{name}</span>
            <span style="color: #94a3b8; font-size: 0.8rem;">- {desc}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # إحصائيات
    st.markdown("### 📊 إحصائيات الجلسة")
    
    stats = st.session_state.agent.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 الرسائل", stats['total_messages'])
    with col2:
        st.metric("🤖 الردود", stats['agent_messages'])
    
    st.markdown("---")
    
    # أزرار التحكم
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent.clear_history()
        st.rerun()
    
    if st.button("💾 حفظ المحادثة", use_container_width=True):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            st.session_state.agent.save_conversation(filename)
            st.success(f"✅ تم الحفظ: {filename}")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem;">
        <p>صُنع بـ ❤️ باستخدام</p>
        <p>Streamlit + Python</p>
        <p style="margin-top: 1rem;">الإصدار 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 🏠 المحتوى الرئيسي
# ═══════════════════════════════════════════════════════════════════════════════

# العنوان الرئيسي
st.markdown("""
<div class="main-header">
    <h1>🤖 وكيل الذكاء الاصطناعي المتكامل</h1>
    <p>مساعدك الشخصي الذكي - جاهز لمساعدتك في أي وقت</p>
</div>
""", unsafe_allow_html=True)

# البطاقات السريعة
st.markdown("### ⚡ ابدأ بسرعة")

quick_actions = st.columns(5)

quick_prompts = [
    ("🧮", "حساب", "احسب 25 × 4 + 100"),
    ("🌤️", "طقس", "ما طقس الرياض؟"),
    ("🕐", "الوقت", "كم الساعة الآن؟"),
    ("🔍", "بحث", "ابحث عن الذكاء الاصطناعي"),
    ("❓", "مساعدة", "مساعدة"),
]

for i, (emoji, label, prompt) in enumerate(quick_prompts):
    with quick_actions[i]:
        if st.button(f"{emoji} {label}", key=f"quick_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = st.session_state.agent.chat(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

st.markdown("---")

# منطقة المحادثة
st.markdown("### 💬 المحادثة")

# عرض الرسائل
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 3rem;
            color: #64748b;
        ">
            <p style="font-size: 4rem; margin-bottom: 1rem;">💬</p>
            <h3 style="color: #94a3b8;">ابدأ محادثتك الآن!</h3>
            <p>اكتب رسالتك أو استخدم الأزرار السريعة أعلاه</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 أنت:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="agent-message">
                    <strong>🤖 الوكيل:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)

# حقل الإدخال
st.markdown("---")

col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "رسالتك",
        placeholder="✍️ اكتب رسالتك هنا... (مثال: احسب 100 + 50)",
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 إرسال", use_container_width=True)

# معالجة الإرسال
if send_button and user_input:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # الحصول على الرد
    with st.spinner("🤔 جاري التفكير..."):
        response = st.session_state.agent.chat(user_input)
    
    # إضافة رد الوكيل
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # تحديث الصفحة
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 🛠️ قسم الأدوات المباشرة
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### 🛠️ الأدوات المباشرة")

tool_tabs = st.tabs(["🧮 الحاسبة", "🌤️ الطقس", "🌍 الترجمة", "💱 العملات", "📝 تحليل النص"])

# تبويب الحاسبة
with tool_tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        calc_input = st.text_input(
            "أدخل العملية الحسابية",
            placeholder="مثال: 25 * 4 + 100",
            key="calc_input"
        )
    with col2:
        if st.button("🧮 احسب", key="calc_btn"):
            if calc_input:
                result = st.session_state.tool_manager.execute_tool('calculator', 'calculate', expression=calc_input)
                if result['success']:
                    st.success(f"✅ النتيجة: **{result['result']}**")
                else:
                    st.error(f"❌ خطأ: {result['error']}")

# تبويب الطقس
with tool_tabs[1]:
    col1, col2 = st.columns([2, 1])
    with col1:
        city_input = st.text_input(
            "أدخل اسم المدينة",
            placeholder="مثال: Riyadh, Dubai, Cairo",
            key="weather_input"
        )
    with col2:
        if st.button("🌤️ اعرض الطقس", key="weather_btn"):
            if city_input:
                result = st.session_state.tool_manager.execute_tool('weather', 'get_weather', city=city_input)
                if result['success']:
                    wcol1, wcol2, wcol3 = st.columns(3)
                    with wcol1:
                        st.metric("🌡️ الحرارة", f"{result['temperature']}°C")
                    with wcol2:
                        st.metric("💧 الرطوبة", f"{result['humidity']}%")
                    with wcol3:
                        st.metric("🌬️ الرياح", f"{result['wind_speed']} km/h")
                    st.info(f"☁️ {result['description']}")
                else:
                    st.error(f"❌ خطأ: {result['error']}")

# تبويب الترجمة
with tool_tabs[2]:
    col1, col2 = st.columns(2)
    with col1:
        source_text = st.text_area(
            "النص المراد ترجمته",
            placeholder="اكتب النص هنا...",
            key="translate_input",
            height=100
        )
    with col2:
        target_lang = st.selectbox(
            "اللغة الهدف",
            ["en", "ar", "fr", "de", "es", "tr", "zh-cn", "ja"],
            format_func=lambda x: {
                "en": "🇬🇧 الإنجليزية",
                "ar": "🇸🇦 العربية",
                "fr": "🇫🇷 الفرنسية",
                "de": "🇩🇪 الألمانية",
                "es": "🇪🇸 الإسبانية",
                "tr": "🇹🇷 التركية",
                "zh-cn": "🇨🇳 الصينية",
                "ja": "🇯🇵 اليابانية"
            }.get(x, x)
        )
    
    if st.button("🌍 ترجم", key="translate_btn"):
        if source_text:
            result = st.session_state.tool_manager.execute_tool('translator', 'translate', text=source_text, to_lang=target_lang)
            if result['success']:
                st.success(f"✨ **الترجمة:**\n\n{result['translated']}")
            else:
                st.error(f"❌ خطأ: {result['error']}")

# تبويب العملات
with tool_tabs[3]:
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        amount = st.number_input("المبلغ", min_value=0.0, value=100.0, key="currency_amount")
    with col2:
        from_curr = st.selectbox("من", ["USD", "EUR", "SAR", "AED", "EGP", "GBP"], key="from_curr")
    with col3:
        to_curr = st.selectbox("إلى", ["SAR", "USD", "EUR", "AED", "EGP", "GBP"], key="to_curr")
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💱 حوّل", key="currency_btn"):
            result = st.session_state.tool_manager.execute_tool('currency', 'convert', amount=amount, from_currency=from_curr, to_currency=to_curr)
            if result['success']:
                st.success(f"💰 {amount} {from_curr} = **{result['result']} {to_curr}**")
            else:
                st.error(f"❌ {result['error']}")

# تبويب تحليل النص
with tool_tabs[4]:
    analyze_text = st.text_area(
        "النص للتحليل",
        placeholder="الصق النص هنا للتحليل...",
        key="analyze_input",
        height=150
    )
    
    if st.button("📝 حلل النص", key="analyze_btn"):
        if analyze_text:
            result = st.session_state.tool_manager.execute_tool('text_analysis', 'analyze', text=analyze_text)
            if result['success']:
                acol1, acol2, acol3 = st.columns(3)
                with acol1:
                    st.metric("📊 الحروف", result['character_count'])
                    st.metric("🔤 حروف عربية", result['arabic_characters'])
                with acol2:
                    st.metric("📖 الكلمات", result['word_count'])
                    st.metric("🔡 حروف إنجليزية", result['english_characters'])
                with acol3:
                    st.metric("📜 الجمل", result['sentence_count'])
                    st.metric("📏 متوسط الكلمة", result['average_word_length'])

# ═══════════════════════════════════════════════════════════════════════════════
# 📄 التذييل
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #64748b;">
    <p>🤖 <strong>وكيل الذكاء الاصطناعي المتكامل</strong></p>
    <p style="font-size: 0.9rem;">مبني بـ ❤️ باستخدام Python و Streamlit</p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">© 2024 - جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
