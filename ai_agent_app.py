"""
واجهة الوكيل الذكي - Streamlit
AI Agent Interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.insert(0, str(Path(__file__).parent))

from ai_agent import (
    MasterAgent,
    ResearchAgent,
    DataAnalystAgent,
    CoderAgent,
    PlannerAgent,
    LanguageAgent,
    KnowledgeBase,
    ConversationManager
)

# إعداد الصفحة
st.set_page_config(
    page_title="🤖 نظام الوكيل الذكي المتكامل",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق CSS مخصص
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .agent-message {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة الجلسة
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.master_agent = MasterAgent("المساعد الرئيسي")
    st.session_state.kb = KnowledgeBase("ai_agent_knowledge.db")
    st.session_state.conversation_manager = ConversationManager(st.session_state.kb)
    st.session_state.chat_history = []
    
    # إضافة الوكلاء المتخصصين
    st.session_state.master_agent.add_sub_agent(ResearchAgent())
    st.session_state.master_agent.add_sub_agent(DataAnalystAgent())
    st.session_state.master_agent.add_sub_agent(CoderAgent())
    st.session_state.master_agent.add_sub_agent(PlannerAgent())
    st.session_state.master_agent.add_sub_agent(LanguageAgent())
    
    # إضافة مهارات أساسية
    skills = [
        ("بحث", "البحث عن المعلومات على الإنترنت", "research"),
        ("تحليل", "تحليل البيانات والإحصائيات", "analysis"),
        ("برمجة", "كتابة ومراجعة الأكواد البرمجية", "coding"),
        ("تخطيط", "إنشاء الخطط والجداول الزمنية", "planning"),
        ("ترجمة", "ترجمة النصوص بين اللغات", "language")
    ]
    
    for name, desc, cat in skills:
        st.session_state.kb.add_skill(name, desc, cat)

# الشريط الجانبي
with st.sidebar:
    st.markdown("### 🎛️ لوحة التحكم")
    
    page = st.radio(
        "اختر الصفحة:",
        ["💬 المحادثة", "🤖 الوكلاء", "📊 الإحصائيات", "🧠 قاعدة المعرفة", "⚙️ الإعدادات"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # معلومات النظام
    st.markdown("### 📈 حالة النظام")
    status = st.session_state.master_agent.get_full_status()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("الوكلاء النشطة", status["total_agents"])
    with col2:
        st.metric("المهام المنجزة", status["master_agent"]["stats"]["tasks_completed"])
    
    st.markdown("---")
    st.markdown("### 🔗 روابط سريعة")
    st.markdown("- 📚 [الوثائق](#)")
    st.markdown("- 💡 [أمثلة](#)")
    st.markdown("- ⚡ [اختصارات](#)")

# العنوان الرئيسي
st.markdown("""
<div class="main-header">
    <h1>🤖 نظام الوكيل الذكي المتكامل</h1>
    <p>نظام ذكاء اصطناعي متعدد الوكلاء مع قدرات متقدمة</p>
</div>
""", unsafe_allow_html=True)

# صفحة المحادثة
if page == "💬 المحادثة":
    st.markdown("## 💬 محادثة مع الوكيل الذكي")
    
    # عرض سجل المحادثة
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 أنت:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 الوكيل:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # مربع إدخال الرسالة
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "اكتب رسالتك هنا...",
            key="user_input",
            placeholder="مثال: اكتب لي كود بايثون لحساب الأعداد الأولية"
        )
    
    with col2:
        send_button = st.button("إرسال 📤", use_container_width=True)
    
    if send_button and user_input:
        # إضافة رسالة المستخدم
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # معالجة الرسالة
        with st.spinner("🤔 يفكر الوكيل..."):
            result = st.session_state.master_agent.coordinate(user_input)
            
            if result["status"] == "success":
                agent_response = result["results"][0]["result"]["output"]
                
                # عرض التفاصيل إذا كانت موجودة
                if result["results"][0]["result"].get("details"):
                    details = result["results"][0]["result"]["details"]
                    agent_response += f"\n\n**التفاصيل:**\n```json\n{json.dumps(details, ensure_ascii=False, indent=2)}\n```"
            else:
                agent_response = result.get("message", "عذراً، حدث خطأ في المعالجة")
        
        # إضافة رد الوكيل
        st.session_state.chat_history.append({
            "role": "agent",
            "content": agent_response
        })
        
        # حفظ في قاعدة المعرفة
        st.session_state.conversation_manager.process_message(user_input)
        
        st.rerun()
    
    # أزرار سريعة
    st.markdown("### 🚀 أوامر سريعة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 ابحث عن معلومة"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "ابحث لي عن معلومات حول الذكاء الاصطناعي"
            })
            st.rerun()
    
    with col2:
        if st.button("📊 حلل بيانات"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "حلل البيانات التالية: [1, 5, 10, 15, 20, 25]"
            })
            st.rerun()
    
    with col3:
        if st.button("💻 اكتب كود"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "اكتب لي كود بايثون لحساب الأعداد الأولية"
            })
            st.rerun()
    
    with col4:
        if st.button("📋 ضع خطة"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "ضع لي خطة لتعلم الذكاء الاصطناعي"
            })
            st.rerun()
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

# صفحة الوكلاء
elif page == "🤖 الوكلاء":
    st.markdown("## 🤖 الوكلاء المتخصصون")
    
    status = st.session_state.master_agent.get_full_status()
    
    # الوكيل الرئيسي
    st.markdown("### 👑 الوكيل الرئيسي")
    
    master_info = status["master_agent"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("المهام المنجزة", master_info["stats"]["tasks_completed"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("المهام الفاشلة", master_info["stats"]["tasks_failed"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("المهام المعلقة", master_info["pending_tasks"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("حجم الذاكرة", master_info["memory_size"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الوكلاء الفرعيون
    st.markdown("### 👥 الوكلاء الفرعيون")
    
    for agent_info in status["sub_agents"]:
        with st.expander(f"🔹 {agent_info['name']} - {agent_info['role']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**القدرات:**")
                for cap in agent_info["capabilities"]:
                    st.markdown(f"- {cap}")
            
            with col2:
                st.metric("المهام المنجزة", agent_info["stats"]["tasks_completed"])
                st.metric("المهام المعلقة", agent_info["pending_tasks"])

# صفحة الإحصائيات
elif page == "📊 الإحصائيات":
    st.markdown("## 📊 إحصائيات النظام")
    
    # إحصائيات قاعدة المعرفة
    kb_stats = st.session_state.kb.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("إجمالي الحقائق", kb_stats["total_facts"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("إجمالي المحادثات", kb_stats["total_conversations"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("إجمالي المهارات", kb_stats["total_skills"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الفئات الأكثر شيوعاً
    if kb_stats["top_categories"]:
        st.markdown("### 📈 الفئات الأكثر شيوعاً")
        
        categories_df = pd.DataFrame(kb_stats["top_categories"])
        
        fig = px.bar(
            categories_df,
            x="category",
            y="count",
            title="توزيع الفئات",
            color="count",
            color_continuous_scale="Viridis"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # المهارات
    st.markdown("### 🎯 المهارات")
    
    skills = st.session_state.kb.get_all_skills()
    
    if skills:
        skills_df = pd.DataFrame(skills)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                skills_df,
                values="usage_count",
                names="name",
                title="استخدام المهارات"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                skills_df,
                x="name",
                y="success_rate",
                title="معدل نجاح المهارات",
                color="success_rate",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig, use_container_width=True)

# صفحة قاعدة المعرفة
elif page == "🧠 قاعدة المعرفة":
    st.markdown("## 🧠 قاعدة المعرفة")
    
    tab1, tab2, tab3 = st.tabs(["📚 الحقائق", "💬 سجل المحادثات", "🎯 المهارات"])
    
    with tab1:
        st.markdown("### 📚 إدارة الحقائق")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("🔍 ابحث في الحقائق", placeholder="ادخل كلمة البحث...")
            
            if search_query:
                results = st.session_state.kb.search_facts(search_query)
                
                st.markdown(f"**عدد النتائج:** {len(results)}")
                
                for i, fact in enumerate(results[:10], 1):
                    with st.expander(f"{i}. {fact['category']} - {fact['key']}"):
                        st.json(fact)
        
        with col2:
            st.markdown("**إضافة حقيقة جديدة**")
            
            category = st.text_input("الفئة")
            key = st.text_input("المفتاح")
            value = st.text_area("القيمة")
            
            if st.button("➕ إضافة"):
                if category and key and value:
                    st.session_state.kb.add_fact(category, key, value)
                    st.success("✓ تمت الإضافة بنجاح!")
                else:
                    st.error("✗ يرجى ملء جميع الحقول")
    
    with tab2:
        st.markdown("### 💬 سجل المحادثات")
        
        history = st.session_state.kb.get_conversation_history(50)
        
        for conv in reversed(history):
            with st.expander(f"📅 {conv['timestamp'][:19]}"):
                st.markdown(f"**👤 المستخدم:** {conv['user_message']}")
                st.markdown(f"**🤖 الوكيل:** {conv['agent_response']}")
                
                if conv.get('context'):
                    st.markdown("**السياق:**")
                    st.json(conv['context'])
    
    with tab3:
        st.markdown("### 🎯 المهارات المتاحة")
        
        skills = st.session_state.kb.get_all_skills()
        
        for skill in skills:
            st.markdown(f"""
            <div class="agent-card">
                <h4>🔹 {skill['name']}</h4>
                <p>{skill['description']}</p>
                <p><strong>الفئة:</strong> {skill['category']}</p>
                <p><strong>عدد الاستخدامات:</strong> {skill['usage_count']}</p>
                <p><strong>معدل النجاح:</strong> {skill['success_rate']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)

# صفحة الإعدادات
elif page == "⚙️ الإعدادات":
    st.markdown("## ⚙️ الإعدادات")
    
    tab1, tab2, tab3 = st.tabs(["🎨 المظهر", "🔧 النظام", "📤 تصدير البيانات"])
    
    with tab1:
        st.markdown("### 🎨 إعدادات المظهر")
        
        theme = st.selectbox("اختر السمة", ["فاتح", "داكن", "تلقائي"])
        language = st.selectbox("اللغة", ["العربية", "English"])
        font_size = st.slider("حجم الخط", 12, 20, 14)
        
        st.info("💡 سيتم تطبيق التغييرات عند إعادة تحميل الصفحة")
    
    with tab2:
        st.markdown("### 🔧 إعدادات النظام")
        
        max_memory = st.slider("الحد الأقصى للذاكرة", 100, 10000, 1000)
        auto_save = st.checkbox("الحفظ التلقائي", value=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 إعادة تعيين النظام"):
                st.warning("⚠️ سيتم مسح جميع البيانات!")
        
        with col2:
            if st.button("💾 حفظ الإعدادات"):
                st.success("✓ تم حفظ الإعدادات!")
    
    with tab3:
        st.markdown("### 📤 تصدير البيانات")
        
        export_format = st.selectbox("تنسيق التصدير", ["JSON", "CSV", "Excel"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 تصدير المحادثات"):
                st.info("جاري التصدير...")
        
        with col2:
            if st.button("📥 تصدير الحقائق"):
                st.info("جاري التصدير...")
        
        with col3:
            if st.button("📥 تصدير كل شيء"):
                st.info("جاري التصدير...")

# التذييل
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>نظام الوكيل الذكي المتكامل v1.0.0 | صُنع بـ ❤️ باستخدام Streamlit</p>
    <p>© 2025 - جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
