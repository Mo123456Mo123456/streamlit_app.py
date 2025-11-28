"""
⚙️ ملف الإعدادات
إعدادات وكيل الذكاء الاصطناعي
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """إعدادات الوكيل"""
    
    # مزود خدمة AI
    provider: str = "local"  # local, openai, anthropic
    
    # مفاتيح API
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # إعدادات النموذج
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # إعدادات المحادثة
    max_history: int = 50
    save_conversations: bool = True
    
    # إعدادات اللغة
    default_language: str = "ar"
    enable_rtl: bool = True
    
    # إعدادات الواجهة
    theme: str = "dark"
    show_stats: bool = True
    enable_animations: bool = True
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """تحميل الإعدادات من متغيرات البيئة"""
        return cls(
            provider=os.getenv("AI_PROVIDER", "local"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            model_name=os.getenv("AI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "2000")),
        )

# الإعدادات الافتراضية
DEFAULT_CONFIG = AgentConfig()

# ثوابت التطبيق
APP_NAME = "وكيل الذكاء الاصطناعي المتكامل"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your AI Agent"

# الألوان
COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "accent": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
}

# رسائل النظام
SYSTEM_MESSAGES = {
    "ar": {
        "welcome": "مرحباً! أنا وكيلك الذكي. كيف يمكنني مساعدتك اليوم؟",
        "thinking": "جاري التفكير...",
        "error": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
        "no_results": "لم يتم العثور على نتائج.",
    },
    "en": {
        "welcome": "Hello! I'm your AI agent. How can I help you today?",
        "thinking": "Thinking...",
        "error": "Sorry, an error occurred. Please try again.",
        "no_results": "No results found.",
    }
}
