"""
الوكلاء المتخصصون
Specialized AI Agents
"""

import json
from typing import List, Dict, Any
from ..core.agent import AIAgent, AgentRole


class ResearchAgent(AIAgent):
    """وكيل البحث - متخصص في البحث وجمع المعلومات"""
    
    def __init__(self):
        super().__init__(
            name="الباحث",
            role=AgentRole.RESEARCHER,
            capabilities=["research", "web_search", "information_gathering", "summarization"]
        )
        
    def search_web(self, query: str) -> Dict[str, Any]:
        """البحث في الويب"""
        # محاكاة البحث (في التطبيق الحقيقي، استخدم API للبحث)
        return {
            "query": query,
            "results": [
                {
                    "title": f"نتيجة بحث 1 عن {query}",
                    "url": "https://example.com/1",
                    "snippet": "معلومات مهمة حول الموضوع..."
                },
                {
                    "title": f"نتيجة بحث 2 عن {query}",
                    "url": "https://example.com/2",
                    "snippet": "مزيد من التفاصيل والمعلومات..."
                }
            ],
            "search_time": 0.5
        }
        
    def summarize(self, text: str) -> str:
        """تلخيص النص"""
        # تلخيص بسيط (في التطبيق الحقيقي، استخدم نموذج NLP)
        words = text.split()
        if len(words) > 50:
            return " ".join(words[:50]) + "..."
        return text


class DataAnalystAgent(AIAgent):
    """وكيل تحليل البيانات"""
    
    def __init__(self):
        super().__init__(
            name="محلل البيانات",
            role=AgentRole.ANALYST,
            capabilities=["data_analysis", "statistics", "visualization", "reporting"]
        )
        
    def analyze_data(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل البيانات"""
        if not data:
            return {"error": "لا توجد بيانات للتحليل"}
            
        analysis = {
            "count": len(data),
            "type": type(data[0]).__name__ if data else "unknown"
        }
        
        # تحليل إحصائي بسيط للأرقام
        if all(isinstance(x, (int, float)) for x in data):
            analysis.update({
                "min": min(data),
                "max": max(data),
                "mean": sum(data) / len(data),
                "sum": sum(data)
            })
            
        return analysis
        
    def generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """توليد رؤى من التحليل"""
        insights = []
        
        if "mean" in analysis:
            insights.append(f"المتوسط الحسابي: {analysis['mean']:.2f}")
        if "max" in analysis and "min" in analysis:
            insights.append(f"النطاق: {analysis['min']} إلى {analysis['max']}")
        insights.append(f"عدد العناصر: {analysis['count']}")
        
        return insights


class CoderAgent(AIAgent):
    """وكيل البرمجة"""
    
    def __init__(self):
        super().__init__(
            name="المبرمج",
            role=AgentRole.CODER,
            capabilities=["coding", "debugging", "code_review", "testing"]
        )
        self.supported_languages = ["python", "javascript", "java", "cpp", "go"]
        
    def generate_code(self, description: str, language: str = "python") -> str:
        """توليد كود برمجي"""
        if language not in self.supported_languages:
            return f"# اللغة {language} غير مدعومة حالياً"
            
        # قوالب كود بسيطة
        if "حساب" in description or "calculate" in description.lower():
            return """def calculate(a, b, operation='+'):
    \"\"\"دالة حسابية عامة\"\"\"
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        return a / b if b != 0 else None
    return None

# مثال على الاستخدام
result = calculate(10, 5, '+')
print(f"النتيجة: {result}")
"""
        elif "قائمة" in description or "list" in description.lower():
            return """def manage_list(items=None):
    \"\"\"إدارة قائمة عناصر\"\"\"
    if items is None:
        items = []
    
    def add_item(item):
        items.append(item)
        return items
    
    def remove_item(item):
        if item in items:
            items.remove(item)
        return items
    
    def get_items():
        return items.copy()
    
    return {
        'add': add_item,
        'remove': remove_item,
        'get': get_items
    }

# مثال على الاستخدام
manager = manage_list()
manager['add']('عنصر 1')
manager['add']('عنصر 2')
print(manager['get']())
"""
        else:
            return f"""# كود مولد بناءً على: {description}

def main():
    \"\"\"الدالة الرئيسية\"\"\"
    print("تم تنفيذ الكود بنجاح!")
    # أضف الكود الخاص بك هنا
    pass

if __name__ == "__main__":
    main()
"""
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """مراجعة الكود"""
        issues = []
        suggestions = []
        
        # فحوصات بسيطة
        if "except:" in code:
            issues.append("استخدام except عام بدون تحديد نوع الخطأ")
        if "TODO" in code or "FIXME" in code:
            issues.append("يوجد تعليقات TODO أو FIXME تحتاج معالجة")
            
        if len(code.split('\n')) > 100:
            suggestions.append("الكود طويل، فكر في تقسيمه إلى وحدات أصغر")
        if '"""' in code or "'''" in code:
            suggestions.append("جيد: يحتوي على توثيق")
            
        return {
            "issues": issues,
            "suggestions": suggestions,
            "score": max(0, 100 - len(issues) * 10)
        }


class PlannerAgent(AIAgent):
    """وكيل التخطيط"""
    
    def __init__(self):
        super().__init__(
            name="المخطط",
            role=AgentRole.PLANNER,
            capabilities=["planning", "scheduling", "optimization", "strategy"]
        )
        
    def create_plan(self, goal: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """إنشاء خطة"""
        if constraints is None:
            constraints = {}
            
        # تحليل الهدف وتقسيمه
        steps = self._break_down_goal(goal)
        
        plan = {
            "goal": goal,
            "steps": steps,
            "estimated_time": len(steps) * 30,  # 30 دقيقة لكل خطوة
            "priority": "high",
            "constraints": constraints,
            "milestones": self._define_milestones(steps)
        }
        
        return plan
        
    def _break_down_goal(self, goal: str) -> List[Dict[str, Any]]:
        """تقسيم الهدف إلى خطوات"""
        # تقسيم بسيط (في التطبيق الحقيقي، استخدم NLP متقدم)
        base_steps = [
            {"step": 1, "action": "تحليل المتطلبات", "status": "pending"},
            {"step": 2, "action": "تصميم الحل", "status": "pending"},
            {"step": 3, "action": "التنفيذ", "status": "pending"},
            {"step": 4, "action": "الاختبار", "status": "pending"},
            {"step": 5, "action": "التسليم", "status": "pending"}
        ]
        
        return base_steps
        
    def _define_milestones(self, steps: List[Dict[str, Any]]) -> List[str]:
        """تحديد المعالم الرئيسية"""
        milestones = []
        
        # معالم كل 2-3 خطوات
        for i in range(0, len(steps), 2):
            if i < len(steps):
                milestones.append(f"إنجاز حتى الخطوة {i+1}")
                
        milestones.append("إكمال المشروع")
        return milestones


class LanguageAgent(AIAgent):
    """وكيل معالجة اللغات"""
    
    def __init__(self):
        super().__init__(
            name="معالج اللغات",
            role=AgentRole.ASSISTANT,
            capabilities=["translation", "text_analysis", "sentiment_analysis", "nlp"]
        )
        
    def translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """ترجمة النص"""
        # ترجمة محاكاة (في التطبيق الحقيقي، استخدم Google Translate API)
        translations = {
            ("en", "ar"): {
                "hello": "مرحبا",
                "world": "عالم",
                "thank you": "شكراً لك"
            },
            ("ar", "en"): {
                "مرحبا": "hello",
                "عالم": "world",
                "شكرا": "thank you"
            }
        }
        
        key = (from_lang, to_lang)
        if key in translations:
            for word, translation in translations[key].items():
                text = text.replace(word, translation)
                
        return text
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """تحليل المشاعر"""
        # تحليل بسيط
        positive_words = ["جيد", "رائع", "ممتاز", "good", "great", "excellent", "amazing"]
        negative_words = ["سيء", "مزعج", "bad", "terrible", "awful", "horrible"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.7
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -0.7
        else:
            sentiment = "neutral"
            score = 0.0
            
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words_found": positive_count,
            "negative_words_found": negative_count
        }
        
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        # استخراج بسيط (في التطبيق الحقيقي، استخدم TF-IDF أو BERT)
        stop_words = {"في", "من", "إلى", "على", "the", "a", "an", "is", "are", "and", "or"}
        
        words = text.split()
        word_freq = {}
        
        for word in words:
            word_clean = word.strip(".,!?").lower()
            if word_clean not in stop_words and len(word_clean) > 2:
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
                
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
