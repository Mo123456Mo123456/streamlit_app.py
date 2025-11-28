"""
أدوات إضافية للوكيل
Additional Agent Tools
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class AgentTools:
    """مجموعة من الأدوات المساعدة للوكيل"""
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """استخراج كتل الكود من النص"""
        code_pattern = r'```(?:python|javascript|java|cpp|c|html|css|sql|bash|sh)?\n(.*?)```'
        matches = re.findall(code_pattern, text, re.DOTALL)
        return matches
    
    @staticmethod
    def detect_language(text: str) -> str:
        """اكتشاف لغة النص"""
        # كلمات عربية
        arabic_pattern = r'[\u0600-\u06FF]'
        if re.search(arabic_pattern, text):
            return 'arabic'
        
        # كلمات إنجليزية
        english_words = ['the', 'and', 'is', 'are', 'was', 'were', 'this', 'that']
        if any(word in text.lower() for word in english_words):
            return 'english'
        
        return 'unknown'
    
    @staticmethod
    def count_words(text: str) -> Dict[str, int]:
        """عد الكلمات والحروف"""
        words = text.split()
        chars = len(text)
        chars_no_spaces = len(text.replace(' ', ''))
        
        return {
            'words': len(words),
            'characters': chars,
            'characters_no_spaces': chars_no_spaces,
            'sentences': text.count('.') + text.count('!') + text.count('?')
        }
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """استخراج عناوين البريد الإلكتروني"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """استخراج الروابط"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """استخراج الهاشتاجات"""
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """استخراج الإشارات"""
        mention_pattern = r'@\w+'
        return re.findall(mention_pattern, text)
    
    @staticmethod
    def format_text(text: str, format_type: str = 'title') -> str:
        """تنسيق النص"""
        if format_type == 'title':
            return text.title()
        elif format_type == 'upper':
            return text.upper()
        elif format_type == 'lower':
            return text.lower()
        elif format_type == 'sentence':
            return text.capitalize()
        return text
    
    @staticmethod
    def remove_duplicates(text: str, separator: str = '\n') -> str:
        """إزالة الأسطر المكررة"""
        lines = text.split(separator)
        unique_lines = []
        seen = set()
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen:
                seen.add(line_stripped)
                unique_lines.append(line)
        
        return separator.join(unique_lines)
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        # إزالة علامات الترقيم
        text_clean = re.sub(r'[^\w\s]', '', text)
        words = text_clean.split()
        
        # فلترة الكلمات حسب الطول
        keywords = [word.lower() for word in words if len(word) >= min_length]
        
        # إزالة التكرار
        return list(set(keywords))
    
    @staticmethod
    def validate_json(json_string: str) -> tuple[bool, Optional[str]]:
        """التحقق من صحة JSON"""
        try:
            json.loads(json_string)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)
    
    @staticmethod
    def format_json(json_string: str, indent: int = 2) -> str:
        """تنسيق JSON"""
        try:
            data = json.loads(json_string)
            return json.dumps(data, ensure_ascii=False, indent=indent)
        except json.JSONDecodeError:
            return json_string
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, float]:
        """حساب قابلية القراءة (مقياس بسيط)"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not sentences or not words:
            return {'score': 0, 'avg_words_per_sentence': 0}
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # مقياس بسيط (كلما قل عدد الكلمات في الجملة، زادت القابلية للقراءة)
        readability_score = 100 - min(avg_words_per_sentence * 2, 100)
        
        return {
            'score': round(readability_score, 2),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'total_words': len(words),
            'total_sentences': len(sentences)
        }
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """استخراج التواريخ من النص"""
        # نمط بسيط للتواريخ
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        
        return dates
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """استخراج الأرقام من النص"""
        number_pattern = r'-?\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        numbers = []
        
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    
    @staticmethod
    def summarize_statistics(text: str) -> Dict[str, Any]:
        """ملخص إحصائي للنص"""
        stats = {
            'word_count': AgentTools.count_words(text)['words'],
            'character_count': AgentTools.count_words(text)['characters'],
            'language': AgentTools.detect_language(text),
            'readability': AgentTools.calculate_readability(text),
            'emails': AgentTools.extract_emails(text),
            'urls': AgentTools.extract_urls(text),
            'hashtags': AgentTools.extract_hashtags(text),
            'mentions': AgentTools.extract_mentions(text),
            'keywords': AgentTools.extract_keywords(text)[:10],  # أول 10 كلمات مفتاحية
            'numbers': AgentTools.extract_numbers(text),
            'dates': AgentTools.extract_dates(text)
        }
        
        return stats
