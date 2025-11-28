"""
دوال مساعدة
Helper Functions
"""

import re
import hashlib
from typing import List, Dict, Any
from datetime import datetime, timedelta


def sanitize_text(text: str) -> str:
    """تنظيف النص من الأحرف الخاصة"""
    # إزالة الأحرف الخاصة والاحتفاظ بالأحرف العربية والإنجليزية والأرقام
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    return text.strip()


def generate_id(text: str) -> str:
    """توليد معرف فريد من النص"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def format_timestamp(dt: datetime = None) -> str:
    """تنسيق الطابع الزمني"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_duration(duration_str: str) -> timedelta:
    """تحليل مدة زمنية من نص"""
    # مثال: "2h 30m" -> timedelta
    hours = 0
    minutes = 0
    
    hour_match = re.search(r'(\d+)h', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
    
    minute_match = re.search(r'(\d+)m', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))
    
    return timedelta(hours=hours, minutes=minutes)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """تقسيم قائمة إلى أجزاء"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """دمج قاموسين"""
    result = dict1.copy()
    result.update(dict2)
    return result


def calculate_similarity(text1: str, text2: str) -> float:
    """حساب التشابه بين نصين (بسيط)"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def extract_numbers(text: str) -> List[float]:
    """استخراج الأرقام من النص"""
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(n) for n in numbers]


def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """التحقق من صحة الرابط"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def truncate_text(text: str, max_length: int = 100) -> str:
    """اختصار النص"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def count_words(text: str) -> int:
    """عد الكلمات في النص"""
    return len(text.split())


def detect_language(text: str) -> str:
    """اكتشاف لغة النص (بسيط)"""
    # التحقق من وجود أحرف عربية
    if re.search(r'[\u0600-\u06FF]', text):
        return "ar"
    # التحقق من وجود أحرف صينية أو يابانية
    elif re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text):
        return "zh/ja"
    # افتراض اللغة الإنجليزية
    else:
        return "en"


def format_file_size(size_bytes: int) -> str:
    """تنسيق حجم الملف"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_percentage(part: float, total: float) -> float:
    """حساب النسبة المئوية"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def is_arabic_text(text: str) -> bool:
    """التحقق من وجود نص عربي"""
    return bool(re.search(r'[\u0600-\u06FF]', text))


def clean_html(html: str) -> str:
    """إزالة وسوم HTML من النص"""
    clean = re.sub(r'<[^>]+>', '', html)
    return clean.strip()


def generate_slug(text: str) -> str:
    """توليد slug من النص"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')
