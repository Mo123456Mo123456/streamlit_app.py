"""
واجهة وكيل الذكاء الاصطناعي المتكامل
Integrated AI Agent Interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from ai_agent import AIAgent, Message
import json
from pathlib import Path

# إعداد الصفحة
st.set_page_config(
    page_title='AI Agent - وكيل الذكاء الاصطناعي',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS مخصص للتصميم الجميل
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .capability-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background-color: #667eea;
        color: white;
        border-radius: 1.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة الوكيل
@st.cache_resource
def get_agent():
    """الحصول على وكيل AI مع التخزين المؤقت"""
    return AIAgent(name="وكيل الذكاء الاصطناعي الخاص", memory_file="agent_memory.json")

agent = get_agent()

# العنوان الرئيسي
st.markdown('<h1 class="main-header">🤖 وكيل الذكاء الاصطناعي المتكامل</h1>', unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    # إحصائيات
    stats = agent.get_statistics()
    st.subheader("📊 الإحصائيات")
    st.metric("إجمالي الرسائل", stats['total_messages'])
    st.metric("رسائل المستخدم", stats['user_messages'])
    st.metric("ردود الوكيل", stats['assistant_messages'])
    
    st.divider()
    
    # القدرات
    st.subheader("🛠️ القدرات المتاحة")
    for capability in stats['capabilities']:
        st.markdown(f'<span class="capability-badge">✓ {capability}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # إدارة الذاكرة
    st.subheader("💾 إدارة الذاكرة")
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        agent.clear_memory()
        st.success("تم مسح المحادثة بنجاح!")
        st.rerun()
    
    if st.button("📥 تصدير المحادثة", use_container_width=True):
        export_path = f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        agent.export_conversation(export_path)
        st.success(f"تم التصدير إلى: {export_path}")
    
    st.divider()
    
    # معلومات إضافية
    st.subheader("ℹ️ معلومات")
    st.caption(f"تاريخ الإنشاء: {stats['conversation_started'][:10]}")
    st.caption(f"آخر نشاط: {stats['last_activity'][:19]}")

# المحتوى الرئيسي
tab1, tab2, tab3 = st.tabs(["💬 المحادثة", "📈 التحليلات", "🔧 الأدوات"])

with tab1:
    st.header("💬 محادثة مع الوكيل")
    
    # عرض تاريخ المحادثة
    conversation_history = agent.get_conversation_context(50)
    
    # حاوية المحادثة
    chat_container = st.container()
    
    with chat_container:
        if conversation_history:
            for msg in conversation_history:
                if msg.role == 'user':
                    with st.chat_message("user"):
                        st.write(msg.content)
                        st.caption(f"🕐 {msg.timestamp[:19]}")
                else:
                    with st.chat_message("assistant"):
                        st.write(msg.content)
                        if msg.metadata and 'task_type' in msg.metadata:
                            st.caption(f"📌 نوع المهمة: {msg.metadata['task_type']}")
                        st.caption(f"🕐 {msg.timestamp[:19]}")
        else:
            st.info("👋 مرحباً! ابدأ المحادثة بإرسال رسالة أدناه.")
    
    # إدخال الرسالة
    st.divider()
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "اكتب رسالتك هنا...",
            key="user_input",
            placeholder="اسألني أي شيء! يمكنني المساعدة في البرمجة، التحليل، الترجمة، وأكثر..."
        )
    
    with col2:
        send_button = st.button("إرسال 📤", use_container_width=True, type="primary")
    
    # معالجة الإدخال
    if send_button and user_input:
        with st.spinner("🤔 الوكيل يفكر..."):
            response = agent.process_query(user_input)
            st.rerun()
    
    # أمثلة سريعة
    st.subheader("💡 أمثلة سريعة")
    example_cols = st.columns(3)
    
    examples = [
        ("مرحباً! كيف حالك؟", "greeting"),
        ("اكتب لي دالة Python لحساب الأرقام الأولية", "code"),
        ("حلل البيانات التالية...", "analysis")
    ]
    
    for i, (example_text, example_type) in enumerate(examples):
        with example_cols[i]:
            if st.button(f"📝 {example_text[:30]}...", use_container_width=True, key=f"example_{i}"):
                with st.spinner("🤔 الوكيل يفكر..."):
                    agent.process_query(example_text)
                    st.rerun()

with tab2:
    st.header("📈 التحليلات والإحصائيات")
    
    # إحصائيات المحادثة
    stats = agent.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("إجمالي الرسائل", stats['total_messages'], delta=None)
    
    with col2:
        st.metric("رسائل المستخدم", stats['user_messages'], delta=None)
    
    with col3:
        st.metric("ردود الوكيل", stats['assistant_messages'], delta=None)
    
    with col4:
        conversation_count = len(agent.memory.conversation_history)
        st.metric("جلسات المحادثة", conversation_count // 2 if conversation_count > 0 else 0)
    
    st.divider()
    
    # تحليل أنواع المهام
    st.subheader("📊 تحليل أنواع المهام")
    
    task_types = {}
    for msg in agent.memory.conversation_history:
        if msg.role == 'assistant' and msg.metadata and 'task_type' in msg.metadata:
            task_type = msg.metadata['task_type']
            task_types[task_type] = task_types.get(task_type, 0) + 1
    
    if task_types:
        task_df = pd.DataFrame({
            'نوع المهمة': list(task_types.keys()),
            'العدد': list(task_types.values())
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(task_df.set_index('نوع المهمة'))
        
        with col2:
            st.dataframe(task_df, use_container_width=True)
    else:
        st.info("لا توجد بيانات كافية للتحليل بعد. ابدأ المحادثة لرؤية الإحصائيات!")
    
    st.divider()
    
    # جدول المحادثة الكامل
    st.subheader("📋 تاريخ المحادثة الكامل")
    
    if agent.memory.conversation_history:
        conversation_data = []
        for msg in agent.memory.conversation_history:
            conversation_data.append({
                'الوقت': msg.timestamp[:19],
                'النوع': 'مستخدم' if msg.role == 'user' else 'وكيل',
                'المحتوى': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'نوع المهمة': msg.metadata.get('task_type', 'N/A') if msg.metadata else 'N/A'
            })
        
        df = pd.DataFrame(conversation_data)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("لا توجد محادثات سابقة.")

with tab3:
    st.header("🔧 الأدوات والوظائف")
    
    # أداة الترجمة
    st.subheader("🌐 أداة الترجمة")
    translation_text = st.text_area("النص للترجمة", placeholder="أدخل النص الذي تريد ترجمته...")
    if st.button("ترجم", key="translate_btn"):
        if translation_text:
            response = agent.process_query(f"ترجم هذا النص: {translation_text}")
            st.success("تمت المعالجة!")
            st.info(response)
    
    st.divider()
    
    # أداة التلخيص
    st.subheader("📝 أداة التلخيص")
    summary_text = st.text_area("النص للتلخيص", placeholder="أدخل النص الذي تريد تلخيصه...", key="summary_input")
    if st.button("لخص", key="summarize_btn"):
        if summary_text:
            response = agent.process_query(f"لخص هذا النص: {summary_text}")
            st.success("تمت المعالجة!")
            st.info(response)
    
    st.divider()
    
    # أداة تحليل الكود
    st.subheader("💻 أداة تحليل الكود")
    code_input = st.text_area("الكود للتحليل", placeholder="أدخل الكود الذي تريد تحليله...", key="code_input")
    if st.button("حلل الكود", key="analyze_code_btn"):
        if code_input:
            response = agent.process_query(f"حلل هذا الكود: {code_input}")
            st.success("تمت المعالجة!")
            st.code(response)
    
    st.divider()
    
    # إعدادات التفضيلات
    st.subheader("⚙️ التفضيلات")
    
    pref_col1, pref_col2 = st.columns(2)
    
    with pref_col1:
        language_pref = st.selectbox("اللغة المفضلة", ["العربية", "English", "Français"])
        if st.button("حفظ اللغة", key="save_lang"):
            agent.update_preferences('language', language_pref)
            st.success(f"تم حفظ اللغة: {language_pref}")
    
    with pref_col2:
        theme_pref = st.selectbox("المظهر", ["فاتح", "داكن", "تلقائي"])
        if st.button("حفظ المظهر", key="save_theme"):
            agent.update_preferences('theme', theme_pref)
            st.success(f"تم حفظ المظهر: {theme_pref}")

# تذييل الصفحة
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🤖 وكيل الذكاء الاصطناعي المتكامل - تم التطوير خصيصاً لك</p>
    <p>Powered by AI Agent System | Version 1.0</p>
</div>
""", unsafe_allow_html=True)
