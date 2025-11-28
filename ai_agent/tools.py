"""
🛠️ أدوات وكيل الذكاء الاصطناعي
مجموعة شاملة من الأدوات الذكية للوكيل
"""

import re
import json
import math
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

# ═══════════════════════════════════════════════════════════════════════════════
# 🧮 أداة الحسابات الرياضية
# ═══════════════════════════════════════════════════════════════════════════════

class MathTool:
    """أداة للحسابات الرياضية المتقدمة"""
    
    name = "calculator"
    description = "حساب العمليات الرياضية والمعادلات"
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """تنفيذ عملية حسابية"""
        try:
            # تنظيف التعبير
            expression = expression.replace('^', '**')
            expression = expression.replace('×', '*')
            expression = expression.replace('÷', '/')
            
            # محاولة الحل باستخدام sympy
            try:
                result = sp.sympify(expression)
                if result.is_number:
                    result = float(result)
            except:
                # استخدام eval آمن
                allowed = {
                    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                    'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
                    'exp': math.exp, 'pi': math.pi, 'e': math.e,
                    'abs': abs, 'pow': pow, 'round': round
                }
                result = eval(expression, {"__builtins__": {}}, allowed)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": "calculation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "calculation"
            }
    
    @staticmethod
    def solve_equation(equation: str, variable: str = 'x') -> Dict[str, Any]:
        """حل معادلة رياضية"""
        try:
            x = sp.Symbol(variable)
            
            # تحويل المعادلة
            if '=' in equation:
                left, right = equation.split('=')
                eq = sp.Eq(parse_expr(left), parse_expr(right))
            else:
                eq = parse_expr(equation)
            
            solutions = sp.solve(eq, x)
            
            return {
                "success": True,
                "equation": equation,
                "solutions": [str(s) for s in solutions],
                "type": "equation_solving"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "equation_solving"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 أداة البحث على الإنترنت
# ═══════════════════════════════════════════════════════════════════════════════

class WebSearchTool:
    """أداة للبحث على الإنترنت"""
    
    name = "web_search"
    description = "البحث على الإنترنت للحصول على معلومات حديثة"
    
    @staticmethod
    def search(query: str, num_results: int = 5) -> Dict[str, Any]:
        """البحث باستخدام DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get('title', ''),
                    "body": r.get('body', ''),
                    "url": r.get('href', '')
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "type": "web_search"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "web_search"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 📚 أداة ويكيبيديا
# ═══════════════════════════════════════════════════════════════════════════════

class WikipediaTool:
    """أداة للبحث في ويكيبيديا"""
    
    name = "wikipedia"
    description = "البحث في ويكيبيديا للحصول على معلومات موثوقة"
    
    @staticmethod
    def search(query: str, lang: str = 'ar') -> Dict[str, Any]:
        """البحث في ويكيبيديا"""
        try:
            import wikipedia
            wikipedia.set_lang(lang)
            
            # البحث عن صفحات
            search_results = wikipedia.search(query, results=3)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "لم يتم العثور على نتائج",
                    "type": "wikipedia"
                }
            
            # الحصول على ملخص أول نتيجة
            try:
                summary = wikipedia.summary(search_results[0], sentences=5)
                page = wikipedia.page(search_results[0])
                url = page.url
            except wikipedia.DisambiguationError as e:
                # في حالة وجود عدة خيارات
                summary = wikipedia.summary(e.options[0], sentences=5)
                page = wikipedia.page(e.options[0])
                url = page.url
            
            return {
                "success": True,
                "title": search_results[0],
                "summary": summary,
                "url": url,
                "related": search_results[1:],
                "type": "wikipedia"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "wikipedia"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🌤️ أداة الطقس
# ═══════════════════════════════════════════════════════════════════════════════

class WeatherTool:
    """أداة للحصول على معلومات الطقس"""
    
    name = "weather"
    description = "الحصول على معلومات الطقس لأي مدينة"
    
    @staticmethod
    def get_weather(city: str) -> Dict[str, Any]:
        """الحصول على طقس مدينة معينة"""
        try:
            # استخدام wttr.in API المجاني
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            current = data.get('current_condition', [{}])[0]
            location = data.get('nearest_area', [{}])[0]
            
            return {
                "success": True,
                "city": city,
                "temperature": current.get('temp_C', 'N/A'),
                "feels_like": current.get('FeelsLikeC', 'N/A'),
                "humidity": current.get('humidity', 'N/A'),
                "description": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                "wind_speed": current.get('windspeedKmph', 'N/A'),
                "visibility": current.get('visibility', 'N/A'),
                "type": "weather"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "weather"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🕐 أداة الوقت والتاريخ
# ═══════════════════════════════════════════════════════════════════════════════

class DateTimeTool:
    """أداة للتعامل مع الوقت والتاريخ"""
    
    name = "datetime"
    description = "الحصول على معلومات الوقت والتاريخ"
    
    @staticmethod
    def get_current_time(timezone: str = 'UTC') -> Dict[str, Any]:
        """الحصول على الوقت الحالي"""
        try:
            from datetime import datetime
            import pytz
            
            try:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
            except:
                now = datetime.now()
            
            # أسماء الأيام بالعربية
            arabic_days = {
                'Monday': 'الإثنين',
                'Tuesday': 'الثلاثاء',
                'Wednesday': 'الأربعاء',
                'Thursday': 'الخميس',
                'Friday': 'الجمعة',
                'Saturday': 'السبت',
                'Sunday': 'الأحد'
            }
            
            # أسماء الأشهر بالعربية
            arabic_months = {
                1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
                5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
                9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
            }
            
            return {
                "success": True,
                "date": now.strftime('%Y-%m-%d'),
                "time": now.strftime('%H:%M:%S'),
                "day": arabic_days.get(now.strftime('%A'), now.strftime('%A')),
                "month": arabic_months.get(now.month, now.strftime('%B')),
                "year": now.year,
                "timezone": timezone,
                "type": "datetime"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "datetime"
            }
    
    @staticmethod
    def calculate_date_difference(date1: str, date2: str) -> Dict[str, Any]:
        """حساب الفرق بين تاريخين"""
        try:
            d1 = datetime.strptime(date1, '%Y-%m-%d')
            d2 = datetime.strptime(date2, '%Y-%m-%d')
            diff = abs(d2 - d1)
            
            return {
                "success": True,
                "date1": date1,
                "date2": date2,
                "days": diff.days,
                "weeks": diff.days // 7,
                "months": diff.days // 30,
                "years": diff.days // 365,
                "type": "date_calculation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "date_calculation"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 أداة تحويل العملات
# ═══════════════════════════════════════════════════════════════════════════════

class CurrencyTool:
    """أداة لتحويل العملات"""
    
    name = "currency"
    description = "تحويل بين العملات المختلفة"
    
    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """تحويل عملة إلى أخرى"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            rate = data['rates'].get(to_currency.upper())
            if rate is None:
                return {
                    "success": False,
                    "error": f"العملة {to_currency} غير مدعومة",
                    "type": "currency"
                }
            
            result = amount * rate
            
            return {
                "success": True,
                "amount": amount,
                "from_currency": from_currency.upper(),
                "to_currency": to_currency.upper(),
                "rate": rate,
                "result": round(result, 2),
                "type": "currency"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "currency"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🌍 أداة الترجمة
# ═══════════════════════════════════════════════════════════════════════════════

class TranslationTool:
    """أداة للترجمة بين اللغات"""
    
    name = "translator"
    description = "ترجمة النصوص بين اللغات المختلفة"
    
    LANGUAGE_CODES = {
        'العربية': 'ar', 'الإنجليزية': 'en', 'الفرنسية': 'fr',
        'الألمانية': 'de', 'الإسبانية': 'es', 'الإيطالية': 'it',
        'الصينية': 'zh-cn', 'اليابانية': 'ja', 'الكورية': 'ko',
        'الروسية': 'ru', 'التركية': 'tr', 'الهندية': 'hi'
    }
    
    @staticmethod
    def translate(text: str, to_lang: str, from_lang: str = 'auto') -> Dict[str, Any]:
        """ترجمة نص"""
        try:
            from googletrans import Translator
            translator = Translator()
            
            result = translator.translate(text, dest=to_lang, src=from_lang)
            
            return {
                "success": True,
                "original": text,
                "translated": result.text,
                "from_language": result.src,
                "to_language": to_lang,
                "type": "translation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "translation"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 أداة تحليل النصوص
# ═══════════════════════════════════════════════════════════════════════════════

class TextAnalysisTool:
    """أداة لتحليل النصوص"""
    
    name = "text_analysis"
    description = "تحليل النصوص وإحصائياتها"
    
    @staticmethod
    def analyze(text: str) -> Dict[str, Any]:
        """تحليل نص"""
        try:
            # إحصائيات أساسية
            words = text.split()
            sentences = re.split(r'[.!?؟]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # عد الحروف العربية والإنجليزية
            arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            return {
                "success": True,
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len(sentences),
                "arabic_characters": arabic_chars,
                "english_characters": english_chars,
                "average_word_length": round(sum(len(w) for w in words) / len(words), 2) if words else 0,
                "type": "text_analysis"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "text_analysis"
            }

# ═══════════════════════════════════════════════════════════════════════════════
# 🔐 أداة التشفير
# ═══════════════════════════════════════════════════════════════════════════════

class CryptoTool:
    """أداة للتشفير وفك التشفير"""
    
    name = "crypto"
    description = "تشفير وفك تشفير النصوص"
    
    @staticmethod
    def encode_base64(text: str) -> Dict[str, Any]:
        """ترميز Base64"""
        try:
            import base64
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return {
                "success": True,
                "original": text,
                "encoded": encoded,
                "type": "base64_encode"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "type": "base64_encode"}
    
    @staticmethod
    def decode_base64(encoded: str) -> Dict[str, Any]:
        """فك ترميز Base64"""
        try:
            import base64
            decoded = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            return {
                "success": True,
                "encoded": encoded,
                "decoded": decoded,
                "type": "base64_decode"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "type": "base64_decode"}
    
    @staticmethod
    def hash_text(text: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """تشفير النص باستخدام hash"""
        try:
            import hashlib
            
            if algorithm == 'md5':
                hashed = hashlib.md5(text.encode()).hexdigest()
            elif algorithm == 'sha1':
                hashed = hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == 'sha256':
                hashed = hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == 'sha512':
                hashed = hashlib.sha512(text.encode()).hexdigest()
            else:
                return {"success": False, "error": "خوارزمية غير مدعومة", "type": "hash"}
            
            return {
                "success": True,
                "original": text,
                "algorithm": algorithm,
                "hash": hashed,
                "type": "hash"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "type": "hash"}

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 أداة إنشاء الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════════════

class ChartTool:
    """أداة لإنشاء الرسوم البيانية"""
    
    name = "chart"
    description = "إنشاء رسوم بيانية من البيانات"
    
    @staticmethod
    def create_chart_data(data: Dict[str, List], chart_type: str = 'bar') -> Dict[str, Any]:
        """إعداد بيانات الرسم البياني"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            return {
                "success": True,
                "data": df.to_dict('records'),
                "columns": list(df.columns),
                "chart_type": chart_type,
                "type": "chart_data"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "type": "chart_data"}

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 مدير الأدوات
# ═══════════════════════════════════════════════════════════════════════════════

class ToolManager:
    """مدير الأدوات - يدير جميع الأدوات المتاحة"""
    
    def __init__(self):
        self.tools = {
            'calculator': MathTool(),
            'web_search': WebSearchTool(),
            'wikipedia': WikipediaTool(),
            'weather': WeatherTool(),
            'datetime': DateTimeTool(),
            'currency': CurrencyTool(),
            'translator': TranslationTool(),
            'text_analysis': TextAnalysisTool(),
            'crypto': CryptoTool(),
            'chart': ChartTool()
        }
    
    def get_tool_descriptions(self) -> str:
        """الحصول على وصف جميع الأدوات"""
        descriptions = []
        tool_info = {
            'calculator': ('🧮', 'الآلة الحاسبة', 'حسابات رياضية متقدمة وحل المعادلات'),
            'web_search': ('🌐', 'البحث', 'البحث على الإنترنت'),
            'wikipedia': ('📚', 'ويكيبيديا', 'معلومات موثوقة من ويكيبيديا'),
            'weather': ('🌤️', 'الطقس', 'معلومات الطقس لأي مدينة'),
            'datetime': ('🕐', 'الوقت', 'الوقت والتاريخ'),
            'currency': ('💱', 'العملات', 'تحويل العملات'),
            'translator': ('🌍', 'الترجمة', 'ترجمة النصوص'),
            'text_analysis': ('📝', 'تحليل النص', 'تحليل وإحصائيات النصوص'),
            'crypto': ('🔐', 'التشفير', 'تشفير وفك تشفير'),
            'chart': ('📊', 'الرسوم', 'إنشاء رسوم بيانية')
        }
        
        for name, (emoji, title, desc) in tool_info.items():
            descriptions.append(f"{emoji} **{title}**: {desc}")
        
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """تنفيذ أداة معينة"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"الأداة '{tool_name}' غير موجودة"}
        
        tool = self.tools[tool_name]
        
        if hasattr(tool, action):
            method = getattr(tool, action)
            return method(**kwargs)
        
        return {"success": False, "error": f"الإجراء '{action}' غير موجود في الأداة"}
