"""
🧠 نواة وكيل الذكاء الاصطناعي
المحرك الأساسي للوكيل الذكي
"""

import os
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Generator
from .tools import ToolManager

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 وكيل الذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════

class AIAgent:
    """
    وكيل الذكاء الاصطناعي الذكي
    يدمج بين قدرات المحادثة والأدوات المتعددة
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        """
        تهيئة الوكيل
        
        Args:
            api_key: مفتاح API
            provider: مزود الخدمة (openai, anthropic, local)
        """
        self.provider = provider
        self.api_key = api_key
        self.tool_manager = ToolManager()
        self.conversation_history: List[Dict] = []
        self.memory: Dict[str, Any] = {}
        self.created_at = datetime.now()
        
        # إعداد شخصية الوكيل
        self.personality = {
            "name": "وكيل الذكاء الاصطناعي",
            "traits": ["ذكي", "مساعد", "ودود", "دقيق"],
            "language": "ar",
            "emoji_style": True
        }
        
        # قوالب الردود
        self.response_templates = {
            "greeting": [
                "مرحباً! 👋 أنا وكيلك الذكي. كيف يمكنني مساعدتك اليوم؟",
                "أهلاً وسهلاً! 🌟 في خدمتك دائماً. ماذا تحتاج؟",
                "السلام عليكم! 🤖 أنا هنا لمساعدتك. ما الذي تود معرفته؟"
            ],
            "farewell": [
                "وداعاً! 👋 سعدت بمحادثتك. إلى اللقاء!",
                "أتمنى لك يوماً سعيداً! 🌈",
                "شكراً لك! لا تتردد في العودة متى احتجت المساعدة 💫"
            ],
            "thinking": [
                "دعني أفكر... 🤔",
                "جاري البحث والتحليل... ⚡",
                "أعمل على ذلك الآن... 🔄"
            ],
            "error": [
                "عذراً، واجهت مشكلة في معالجة طلبك. 😅",
                "يبدو أن هناك خطأ ما. هل يمكنك إعادة صياغة السؤال؟",
                "لم أتمكن من إكمال المهمة. دعني أحاول بطريقة أخرى."
            ]
        }
    
    def _detect_intent(self, message: str) -> Dict[str, Any]:
        """
        اكتشاف نية المستخدم من الرسالة
        
        Args:
            message: رسالة المستخدم
            
        Returns:
            قاموس يحتوي على النية والمعلومات المستخرجة
        """
        message_lower = message.lower()
        
        # أنماط الأوامر
        patterns = {
            'greeting': r'(مرحبا|أهلا|السلام|هاي|صباح|مساء|hello|hi)',
            'farewell': r'(وداعا|مع السلامة|باي|bye|goodbye)',
            'calculation': r'(احسب|حساب|كم|ناتج|\+|\-|\*|\/|\^|=)',
            'search': r'(ابحث|بحث|search|find|أين|ماذا|من هو|ما هي)',
            'weather': r'(طقس|جو|حرارة|weather|درجة)',
            'time': r'(وقت|ساعة|تاريخ|يوم|time|date)',
            'currency': r'(عملة|تحويل|دولار|ريال|يورو|currency)',
            'translate': r'(ترجم|ترجمة|translate|بالإنجليزية|بالعربية)',
            'wikipedia': r'(ويكيبيديا|wikipedia|معلومات عن|من هو|ما هو)',
            'analyze': r'(حلل|تحليل|analyze|عدد الكلمات|إحصائيات)',
            'help': r'(مساعدة|help|أوامر|قدرات|ماذا تستطيع)'
        }
        
        detected_intents = []
        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                detected_intents.append(intent)
        
        # استخراج المعلومات
        extracted = {}
        
        # استخراج الأرقام
        numbers = re.findall(r'\d+\.?\d*', message)
        if numbers:
            extracted['numbers'] = [float(n) for n in numbers]
        
        # استخراج العملات
        currencies = re.findall(r'(دولار|ريال|يورو|جنيه|USD|EUR|SAR|EGP)', message, re.IGNORECASE)
        if currencies:
            extracted['currencies'] = currencies
        
        return {
            'intents': detected_intents if detected_intents else ['general'],
            'extracted': extracted,
            'original_message': message
        }
    
    def _execute_tool_based_on_intent(self, intent_data: Dict) -> Optional[Dict]:
        """
        تنفيذ الأداة المناسبة بناءً على النية
        """
        intents = intent_data['intents']
        message = intent_data['original_message']
        extracted = intent_data['extracted']
        
        results = []
        
        for intent in intents:
            if intent == 'calculation':
                # استخراج التعبير الرياضي
                expr = re.search(r'[\d\+\-\*\/\^\(\)\s\.]+', message)
                if expr and len(expr.group().strip()) > 0:
                    expr_clean = expr.group().strip()
                    # تجاهل إذا كان التعبير أرقام فقط بدون عمليات
                    if any(op in expr_clean for op in ['+', '-', '*', '/', '^']):
                        result = self.tool_manager.execute_tool('calculator', 'calculate', expression=expr_clean)
                        results.append(result)
            
            elif intent == 'weather':
                # استخراج اسم المدينة
                city_match = re.search(r'(?:طقس|جو|حرارة|weather)\s+(?:في\s+)?(\w+)', message, re.IGNORECASE)
                if city_match:
                    city = city_match.group(1)
                    result = self.tool_manager.execute_tool('weather', 'get_weather', city=city)
                    results.append(result)
            
            elif intent == 'time':
                result = self.tool_manager.execute_tool('datetime', 'get_current_time')
                results.append(result)
            
            elif intent == 'search':
                result = self.tool_manager.execute_tool('web_search', 'search', query=message)
                results.append(result)
            
            elif intent == 'wikipedia':
                # استخراج موضوع البحث
                topic_match = re.search(r'(?:معلومات عن|من هو|ما هو|ما هي)\s+(.+)', message)
                if topic_match:
                    topic = topic_match.group(1)
                    result = self.tool_manager.execute_tool('wikipedia', 'search', query=topic)
                    results.append(result)
        
        return results if results else None
    
    def _format_tool_result(self, result: Dict) -> str:
        """
        تنسيق نتيجة الأداة للعرض
        """
        if not result.get('success', False):
            return f"❌ {result.get('error', 'حدث خطأ غير معروف')}"
        
        result_type = result.get('type', '')
        
        if result_type == 'calculation':
            return f"🧮 **النتيجة**: `{result['expression']}` = **{result['result']}**"
        
        elif result_type == 'weather':
            return f"""🌤️ **طقس {result['city']}**
            
🌡️ درجة الحرارة: **{result['temperature']}°C**
🤔 الإحساس: {result['feels_like']}°C
💧 الرطوبة: {result['humidity']}%
🌬️ الرياح: {result['wind_speed']} كم/س
📝 الحالة: {result['description']}"""
        
        elif result_type == 'datetime':
            return f"""🕐 **الوقت والتاريخ**
            
📅 التاريخ: **{result['date']}**
⏰ الوقت: **{result['time']}**
📆 اليوم: {result['day']}
🗓️ الشهر: {result['month']} {result['year']}"""
        
        elif result_type == 'currency':
            return f"""💱 **تحويل العملات**
            
💰 {result['amount']} {result['from_currency']} = **{result['result']} {result['to_currency']}**
📊 سعر الصرف: {result['rate']}"""
        
        elif result_type == 'wikipedia':
            return f"""📚 **{result['title']}**
            
{result['summary']}

🔗 [اقرأ المزيد]({result['url']})"""
        
        elif result_type == 'web_search':
            results_text = "\n\n".join([
                f"**{i+1}. {r['title']}**\n{r['body'][:200]}..."
                for i, r in enumerate(result['results'][:3])
            ])
            return f"🔍 **نتائج البحث:**\n\n{results_text}"
        
        elif result_type == 'translation':
            return f"""🌍 **الترجمة**
            
📝 الأصلي: {result['original']}
✨ الترجمة: **{result['translated']}**"""
        
        elif result_type == 'text_analysis':
            return f"""📝 **تحليل النص**
            
📊 عدد الحروف: {result['character_count']}
📖 عدد الكلمات: {result['word_count']}
📜 عدد الجمل: {result['sentence_count']}
🔤 حروف عربية: {result['arabic_characters']}
🔡 حروف إنجليزية: {result['english_characters']}
📏 متوسط طول الكلمة: {result['average_word_length']}"""
        
        return f"✅ تم بنجاح: {json.dumps(result, ensure_ascii=False, indent=2)}"
    
    def _generate_local_response(self, message: str, intent_data: Dict) -> str:
        """
        توليد رد محلي بدون API خارجي
        """
        intents = intent_data['intents']
        
        # التحيات
        if 'greeting' in intents:
            import random
            return random.choice(self.response_templates['greeting'])
        
        # الوداع
        if 'farewell' in intents:
            import random
            return random.choice(self.response_templates['farewell'])
        
        # طلب المساعدة
        if 'help' in intents:
            tools_desc = self.tool_manager.get_tool_descriptions()
            return f"""🤖 **أهلاً! أنا وكيلك الذكي**

يمكنني مساعدتك في العديد من المهام:

{tools_desc}

**أمثلة على الأوامر:**
• "احسب 25 * 4 + 10"
• "ما هو طقس الرياض؟"
• "كم الساعة الآن؟"
• "ابحث عن الذكاء الاصطناعي"
• "معلومات عن ألبرت أينشتاين"
• "حوّل 100 دولار إلى ريال"

💡 جرب أي من هذه الأوامر أو اسألني عن أي شيء!"""
        
        # تنفيذ الأدوات
        tool_results = self._execute_tool_based_on_intent(intent_data)
        if tool_results:
            responses = []
            for result in tool_results:
                responses.append(self._format_tool_result(result))
            return "\n\n---\n\n".join(responses)
        
        # رد عام
        return f"""🤔 فهمت سؤالك: "{message}"

للأسف، لم أتمكن من تحديد نوع المساعدة المطلوبة بدقة.

💡 **جرب:**
• أن تكون أكثر تحديداً في طلبك
• استخدام كلمات مفتاحية مثل: "احسب"، "ابحث"، "طقس"، "ترجم"
• كتابة "مساعدة" لرؤية قائمة بقدراتي

أنا هنا لمساعدتك! 🌟"""
    
    async def _generate_ai_response(self, message: str, context: str = "") -> str:
        """
        توليد رد باستخدام API الذكاء الاصطناعي
        """
        if self.provider == "openai" and self.api_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.api_key)
                
                system_prompt = f"""أنت وكيل ذكاء اصطناعي ذكي ومساعد.
تتحدث بالعربية بشكل أساسي وتستخدم الإيموجي لجعل الردود أكثر حيوية.
كن ودوداً ومفيداً ودقيقاً في إجاباتك.
{context}"""
                
                messages = [{"role": "system", "content": system_prompt}]
                
                # إضافة تاريخ المحادثة
                for msg in self.conversation_history[-10:]:
                    messages.append(msg)
                
                messages.append({"role": "user", "content": message})
                
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                return self._generate_local_response(message, self._detect_intent(message))
        
        elif self.provider == "anthropic" and self.api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": message}]
                )
                
                return response.content[0].text
                
            except Exception as e:
                return self._generate_local_response(message, self._detect_intent(message))
        
        # الوضع المحلي
        return self._generate_local_response(message, self._detect_intent(message))
    
    def chat(self, message: str) -> str:
        """
        محادثة متزامنة مع الوكيل
        
        Args:
            message: رسالة المستخدم
            
        Returns:
            رد الوكيل
        """
        # اكتشاف النية
        intent_data = self._detect_intent(message)
        
        # توليد الرد
        response = self._generate_local_response(message, intent_data)
        
        # حفظ في التاريخ
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    async def chat_async(self, message: str) -> str:
        """
        محادثة غير متزامنة مع الوكيل
        """
        intent_data = self._detect_intent(message)
        
        # محاولة استخدام AI API أولاً
        if self.api_key:
            response = await self._generate_ai_response(message)
        else:
            response = self._generate_local_response(message, intent_data)
        
        # حفظ في التاريخ
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def clear_history(self):
        """مسح تاريخ المحادثة"""
        self.conversation_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الوكيل"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m['role'] == 'user']),
            "agent_messages": len([m for m in self.conversation_history if m['role'] == 'assistant']),
            "created_at": self.created_at.isoformat(),
            "provider": self.provider,
            "has_api_key": bool(self.api_key)
        }
    
    def save_conversation(self, filepath: str):
        """حفظ المحادثة في ملف"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.conversation_history,
                'stats': self.get_stats()
            }, f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, filepath: str):
        """تحميل محادثة من ملف"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.conversation_history = data.get('history', [])
