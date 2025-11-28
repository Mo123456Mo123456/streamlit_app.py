"""
إعدادات نظام الوكيل الذكي
AI Agent System Configuration
"""

import os
from pathlib import Path


class Config:
    """إعدادات النظام"""
    
    # المسارات
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    DB_DIR = BASE_DIR / "database"
    
    # قاعدة البيانات
    DB_NAME = "ai_agent_knowledge.db"
    DB_PATH = DB_DIR / DB_NAME
    
    # إعدادات الوكيل
    MAX_MEMORY_SIZE = 1000
    MAX_CONTEXT_SIZE = 100
    DEFAULT_PRIORITY = 1
    
    # إعدادات الأداء
    MAX_CONCURRENT_TASKS = 5
    TASK_TIMEOUT = 300  # 5 دقائق
    AGENT_RESPONSE_TIMEOUT = 30  # 30 ثانية
    
    # إعدادات اللغة
    DEFAULT_LANGUAGE = "ar"
    SUPPORTED_LANGUAGES = ["ar", "en"]
    
    # إعدادات التحليل
    MAX_DATA_POINTS = 10000
    CONFIDENCE_THRESHOLD = 0.7
    
    # إعدادات البحث
    MAX_SEARCH_RESULTS = 10
    SEARCH_TIMEOUT = 10
    
    # إعدادات الكود
    SUPPORTED_PROGRAMMING_LANGUAGES = [
        "python",
        "javascript",
        "java",
        "cpp",
        "go",
        "rust",
        "typescript"
    ]
    MAX_CODE_LENGTH = 10000
    
    # إعدادات التخطيط
    DEFAULT_STEP_DURATION = 30  # دقيقة
    MAX_PLAN_STEPS = 20
    
    # إعدادات السجل
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "ai_agent.log"
    
    # إعدادات الأمان
    ENABLE_AUTHENTICATION = False
    SESSION_TIMEOUT = 3600  # ساعة
    
    # إعدادات واجهة المستخدم
    UI_THEME = "light"
    UI_PRIMARY_COLOR = "#667eea"
    UI_SECONDARY_COLOR = "#764ba2"
    
    @classmethod
    def ensure_directories(cls):
        """التأكد من وجود المجلدات المطلوبة"""
        for dir_path in [cls.DATA_DIR, cls.LOGS_DIR, cls.DB_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_db_path(cls):
        """الحصول على مسار قاعدة البيانات"""
        cls.ensure_directories()
        return str(cls.DB_PATH)
    
    @classmethod
    def to_dict(cls):
        """تحويل الإعدادات إلى قاموس"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }


class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_AUTHENTICATION = True


# تحديد البيئة
ENV = os.getenv("AI_AGENT_ENV", "development")

if ENV == "production":
    config = ProductionConfig
else:
    config = DevelopmentConfig

# تأكد من وجود المجلدات
config.ensure_directories()
