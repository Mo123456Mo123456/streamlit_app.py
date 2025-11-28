"""
نظام وكيل الذكاء الاصطناعي المتكامل
AI Agent System - Comprehensive AI Assistant
"""

import streamlit as st
import pandas as pd
import json
import datetime
from typing import List, Dict, Any
import re
import os
from pathlib import Path

# إعدادات الصفحة
st.set_page_config(
    page_title='وكيل الذكاء الاصطناعي | AI Agent',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS مخصص للواجهة
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# نظام إدارة الذاكرة والمحادثات
# ============================================================================

class ConversationMemory:
    """إدارة ذاكرة المحادثات"""
    
    def __init__(self):
        if 'conversations' not in st.session_state:
            st.session_state.conversations = []
        if 'current_conversation' not in st.session_state:
            st.session_state.current_conversation = []
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = 0
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """إضافة رسالة جديدة للمحادثة"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        st.session_state.current_conversation.append(message)
    
    def get_conversation_history(self) -> List[Dict]:
        """الحصول على تاريخ المحادثة"""
        return st.session_state.current_conversation
    
    def clear_conversation(self):
        """مسح المحادثة الحالية"""
        if st.session_state.current_conversation:
            st.session_state.conversations.append({
                'id': st.session_state.conversation_id,
                'messages': st.session_state.current_conversation.copy(),
                'created_at': datetime.datetime.now().isoformat()
            })
            st.session_state.conversation_id += 1
        st.session_state.current_conversation = []
    
    def save_conversation(self, filename: str = None):
        """حفظ المحادثة في ملف"""
        if filename is None:
            filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'conversation_id': st.session_state.conversation_id,
            'messages': st.session_state.current_conversation,
            'saved_at': datetime.datetime.now().isoformat()
        }
        
        os.makedirs('saved_conversations', exist_ok=True)
        filepath = Path('saved_conversations') / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath

# ============================================================================
# أدوات الوكيل
# ============================================================================

class AgentTools:
    """مجموعة أدوات الوكيل"""
    
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """تحليل النص"""
        analysis = {
            'length': len(text),
            'word_count': len(text.split()),
            'character_count': len(text),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'language': 'Arabic' if any('\u0600' <= char <= '\u06FF' for char in text) else 'English',
            'has_numbers': bool(re.search(r'\d', text)),
            'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
            'has_urls': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
        }
        return analysis
    
    @staticmethod
    def process_data(data: pd.DataFrame, operation: str) -> Dict[str, Any]:
        """معالجة البيانات"""
        results = {
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'null_counts': data.isnull().sum().to_dict(),
            'summary_stats': {}
        }
        
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            results['summary_stats'] = data[numeric_cols].describe().to_dict()
        
        return results
    
    @staticmethod
    def generate_code(task: str, language: str = 'python') -> str:
        """إنشاء كود بناءً على المهمة"""
        code_templates = {
            'python': {
                'data_analysis': f"""
# تحليل البيانات
import pandas as pd
import numpy as np

# {task}
def analyze_data(data):
    # كود التحليل هنا
    return results
""",
                'web_scraping': f"""
# استخراج البيانات من الويب
import requests
from bs4 import BeautifulSoup

# {task}
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # كود الاستخراج هنا
    return data
""",
                'api': f"""
# إنشاء API
from flask import Flask, jsonify

app = Flask(__name__)

# {task}
@app.route('/api/endpoint')
def endpoint():
    return jsonify({{'message': 'Success'}})

if __name__ == '__main__':
    app.run(debug=True)
"""
            }
        }
        
        # تحديد نوع المهمة
        task_type = 'data_analysis'
        if 'scrap' in task.lower() or 'web' in task.lower():
            task_type = 'web_scraping'
        elif 'api' in task.lower() or 'endpoint' in task.lower():
            task_type = 'api'
        
        return code_templates.get(language, {}).get(task_type, f"# {task}\n# كود مخصص هنا")
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """حساب تعبير رياضي"""
        try:
            # تنظيف التعبير
            expression = expression.replace(' ', '')
            # تقييم آمن
            result = eval(expression, {"__builtins__": {}}, {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': __import__('math').sqrt
            })
            return {'expression': expression, 'result': result, 'success': True}
        except Exception as e:
            return {'expression': expression, 'error': str(e), 'success': False}

# ============================================================================
# محرك الوكيل الرئيسي
# ============================================================================

class AIAgent:
    """الوكيل الرئيسي للذكاء الاصطناعي"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.tools = AgentTools()
    
    def process_query(self, user_input: str) -> str:
        """معالجة استعلام المستخدم"""
        user_input_lower = user_input.lower()
        
        # تحليل النص
        if any(keyword in user_input_lower for keyword in ['حلل', 'analyze', 'تحليل']):
            if 'نص' in user_input_lower or 'text' in user_input_lower:
                analysis = self.tools.analyze_text(user_input)
                response = f"""
**نتائج تحليل النص:**
- الطول: {analysis['length']} حرف
- عدد الكلمات: {analysis['word_count']}
- عدد الجمل: {analysis['sentence_count']}
- اللغة: {analysis['language']}
- يحتوي على أرقام: {'نعم' if analysis['has_numbers'] else 'لا'}
- يحتوي على بريد إلكتروني: {'نعم' if analysis['has_emails'] else 'لا'}
- يحتوي على روابط: {'نعم' if analysis['has_urls'] else 'لا'}
"""
                return response
        
        # معالجة البيانات
        if any(keyword in user_input_lower for keyword in ['بيانات', 'data', 'جدول']):
            if 'gdp_data' in st.session_state or 'uploaded_data' in st.session_state:
                data = st.session_state.get('uploaded_data') or st.session_state.get('gdp_data')
                if isinstance(data, pd.DataFrame):
                    analysis = self.tools.process_data(data, 'analyze')
                    response = f"""
**تحليل البيانات:**
- الأبعاد: {analysis['shape'][0]} صف × {analysis['shape'][1]} عمود
- الأعمدة: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}
- القيم المفقودة: {sum(analysis['null_counts'].values())} قيمة
"""
                    return response
        
        # إنشاء كود
        if any(keyword in user_input_lower for keyword in ['كود', 'code', 'برنامج', 'program']):
            language = 'python'
            if 'javascript' in user_input_lower or 'js' in user_input_lower:
                language = 'javascript'
            code = self.tools.generate_code(user_input, language)
            response = f"""
**الكود المقترح:**

```{language}
{code}
```
"""
            return response
        
        # حسابات رياضية
        if any(keyword in user_input_lower for keyword in ['احسب', 'calculate', 'حساب']):
            # استخراج التعبير الرياضي
            numbers = re.findall(r'[\d+\-*/().\s]+', user_input)
            if numbers:
                expression = ''.join(numbers).strip()
                result = self.tools.calculate(expression)
                if result['success']:
                    response = f"**النتيجة:** {result['expression']} = {result['result']}"
                else:
                    response = f"**خطأ في الحساب:** {result.get('error', 'تعبير غير صحيح')}"
                return response
        
        # رد عام ذكي
        return self._generate_intelligent_response(user_input)
    
    def _generate_intelligent_response(self, user_input: str) -> str:
        """إنشاء رد ذكي بناءً على المدخل"""
        greetings_ar = ['مرحبا', 'السلام', 'أهلا', 'صباح', 'مساء']
        greetings_en = ['hello', 'hi', 'hey', 'good morning', 'good evening']
        
        user_lower = user_input.lower()
        
        if any(greeting in user_lower for greeting in greetings_ar + greetings_en):
            return """
مرحباً! أنا وكيل الذكاء الاصطناعي الخاص بك. يمكنني مساعدتك في:

🤖 **التحليل والمعالجة:**
- تحليل النصوص والبيانات
- معالجة الملفات والجداول
- إجراء الحسابات الرياضية

💻 **البرمجة:**
- إنشاء الكود
- شرح المفاهيم البرمجية
- حل المشاكل التقنية

📊 **البيانات:**
- تحليل البيانات
- إنشاء الرسوم البيانية
- معالجة CSV و Excel

💬 **المحادثة:**
- الإجابة على الأسئلة
- تقديم النصائح
- المساعدة في المهام

كيف يمكنني مساعدتك اليوم؟
"""
        
        if 'مساعدة' in user_lower or 'help' in user_lower:
            return """
**دليل الاستخدام:**

1. **تحليل النص:** اكتب "حلل هذا النص: [النص]"
2. **تحليل البيانات:** اكتب "حلل البيانات" أو "analyze data"
3. **إنشاء كود:** اكتب "أنشئ كود لـ [المهمة]"
4. **حساب:** اكتب "احسب [التعبير الرياضي]"
5. **محادثة:** اسأل أي سؤال وسأجيب عليه

**أمثلة:**
- "حلل هذا النص: مرحبا بك في نظام الذكاء الاصطناعي"
- "أنشئ كود لتحليل البيانات"
- "احسب 25 * 4 + 10"
"""
        
        # رد عام
        return f"""
شكراً لسؤالك! لقد استلمت رسالتك: "{user_input}"

يمكنني مساعدتك في:
- تحليل النصوص والبيانات
- إنشاء الكود البرمجي
- إجراء الحسابات
- الإجابة على الأسئلة

يرجى توضيح ما تحتاجه بالضبط وسأكون سعيداً لمساعدتك!
"""

# ============================================================================
# واجهة المستخدم
# ============================================================================

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # العنوان الرئيسي
    st.markdown('<h1 class="main-header">🤖 وكيل الذكاء الاصطناعي المتكامل</h1>', unsafe_allow_html=True)
    
    # إنشاء الوكيل
    agent = AIAgent()
    
    # الشريط الجانبي
    with st.sidebar:
        st.header('⚙️ الإعدادات')
        
        # إحصائيات
        st.subheader('📊 الإحصائيات')
        st.metric('عدد الرسائل', len(agent.memory.get_conversation_history()))
        st.metric('المحادثات المحفوظة', len(st.session_state.conversations))
        
        st.divider()
        
        # إدارة المحادثات
        st.subheader('💾 إدارة المحادثات')
        if st.button('🗑️ مسح المحادثة', use_container_width=True):
            agent.memory.clear_conversation()
            st.rerun()
        
        if st.button('💾 حفظ المحادثة', use_container_width=True):
            filepath = agent.memory.save_conversation()
            st.success(f'تم الحفظ في: {filepath}')
        
        st.divider()
        
        # رفع ملفات
        st.subheader('📁 رفع الملفات')
        uploaded_file = st.file_uploader(
            'رفع ملف CSV أو Excel',
            type=['csv', 'xlsx', 'xls'],
            help='يمكنك رفع ملف بيانات لتحليله'
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                st.session_state.uploaded_data = data
                st.success(f'تم رفع الملف بنجاح! ({data.shape[0]} صف × {data.shape[1]} عمود)')
                st.dataframe(data.head(), use_container_width=True)
            except Exception as e:
                st.error(f'خطأ في قراءة الملف: {str(e)}')
        
        st.divider()
        
        # معلومات
        st.subheader('ℹ️ معلومات')
        st.info("""
        **الإصدار:** 1.0.0
        
        **القدرات:**
        - تحليل النصوص
        - معالجة البيانات
        - إنشاء الكود
        - الحسابات الرياضية
        """)
    
    # المنطقة الرئيسية
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header('💬 المحادثة')
        
        # عرض تاريخ المحادثة
        conversation_history = agent.memory.get_conversation_history()
        
        for message in conversation_history:
            role = message['role']
            content = message['content']
            timestamp = message.get('timestamp', '')
            
            if role == 'user':
                with st.chat_message("user"):
                    st.write(content)
                    if timestamp:
                        st.caption(f"🕐 {timestamp[:19]}")
            else:
                with st.chat_message("assistant"):
                    st.markdown(content)
                    if timestamp:
                        st.caption(f"🕐 {timestamp[:19]}")
        
        # حقل الإدخال
        user_input = st.chat_input("اكتب رسالتك هنا...")
        
        if user_input:
            # إضافة رسالة المستخدم
            agent.memory.add_message('user', user_input)
            
            # معالجة الاستعلام
            with st.spinner('🤔 جاري المعالجة...'):
                response = agent.process_query(user_input)
            
            # إضافة رد الوكيل
            agent.memory.add_message('assistant', response)
            
            # إعادة تحميل الصفحة لعرض الرسائل الجديدة
            st.rerun()
    
    with col2:
        st.header('🛠️ الأدوات السريعة')
        
        # أزرار سريعة
        if st.button('📊 تحليل البيانات المرفوعة', use_container_width=True):
            if 'uploaded_data' in st.session_state:
                data = st.session_state.uploaded_data
                analysis = agent.tools.process_data(data, 'analyze')
                st.json(analysis)
            else:
                st.warning('لم يتم رفع أي ملف بيانات')
        
        if st.button('📝 مثال على تحليل النص', use_container_width=True):
            sample_text = "مرحباً بك في نظام الذكاء الاصطناعي المتكامل. هذا نظام متقدم يمكنه مساعدتك في العديد من المهام."
            analysis = agent.tools.analyze_text(sample_text)
            st.json(analysis)
        
        if st.button('🧮 مثال على الحساب', use_container_width=True):
            result = agent.tools.calculate("25 * 4 + 10")
            st.json(result)
        
        st.divider()
        
        st.subheader('📈 البيانات المتاحة')
        if 'uploaded_data' in st.session_state:
            data = st.session_state.uploaded_data
            st.metric('الصفوف', data.shape[0])
            st.metric('الأعمدة', data.shape[1])
            st.dataframe(data.head(5), use_container_width=True)
        else:
            st.info('لم يتم رفع أي بيانات بعد')

if __name__ == '__main__':
    main()
