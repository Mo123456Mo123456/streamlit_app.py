"""
إعدادات التطبيق
Application Configuration
"""

# إعدادات الوكيل
AGENT_CONFIG = {
    'name': 'وكيل الذكاء الاصطناعي الخاص',
    'memory_file': 'agent_memory.json',
    'max_history': 100,  # الحد الأقصى لعدد الرسائل المحفوظة
    'context_window': 10,  # عدد الرسائل المستخدمة في السياق
}

# إعدادات الواجهة
UI_CONFIG = {
    'page_title': 'AI Agent - وكيل الذكاء الاصطناعي',
    'page_icon': '🤖',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# القدرات المتاحة
CAPABILITIES = {
    'conversation': True,
    'code_assistance': True,
    'data_analysis': True,
    'text_generation': True,
    'translation': True,
    'summarization': True,
    'question_answering': True,
}

# إعدادات اللغة
LANGUAGE_CONFIG = {
    'default_language': 'arabic',
    'supported_languages': ['arabic', 'english', 'french'],
}

# إعدادات الأدوات
TOOLS_CONFIG = {
    'enable_code_extraction': True,
    'enable_language_detection': True,
    'enable_text_analysis': True,
    'enable_email_extraction': True,
    'enable_url_extraction': True,
}
