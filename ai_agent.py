"""
نظام وكيل الذكاء الاصطناعي المتكامل
AI Agent System - Integrated AI Agent Program
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Message:
    """رسالة في المحادثة"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentMemory:
    """ذاكرة الوكيل"""
    conversation_history: List[Message]
    user_preferences: Dict[str, Any]
    context: Dict[str, Any]
    created_at: str
    last_updated: str


class AIAgent:
    """وكيل الذكاء الاصطناعي الرئيسي"""
    
    def __init__(self, name: str = "AI Agent", memory_file: str = "agent_memory.json"):
        self.name = name
        self.memory_file = memory_file
        self.memory = self._load_memory()
        self.capabilities = {
            "conversation": True,
            "code_assistance": True,
            "data_analysis": True,
            "text_generation": True,
            "translation": True,
            "summarization": True,
            "question_answering": True
        }
    
    def _load_memory(self) -> AgentMemory:
        """تحميل الذاكرة من الملف"""
        memory_path = Path(self.memory_file)
        if memory_path.exists():
            try:
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AgentMemory(
                        conversation_history=[
                            Message(**msg) for msg in data.get('conversation_history', [])
                        ],
                        user_preferences=data.get('user_preferences', {}),
                        context=data.get('context', {}),
                        created_at=data.get('created_at', datetime.now().isoformat()),
                        last_updated=data.get('last_updated', datetime.now().isoformat())
                    )
            except Exception as e:
                print(f"Error loading memory: {e}")
        
        # إنشاء ذاكرة جديدة
        return AgentMemory(
            conversation_history=[],
            user_preferences={},
            context={},
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
    
    def _save_memory(self):
        """حفظ الذاكرة في الملف"""
        self.memory.last_updated = datetime.now().isoformat()
        memory_path = Path(self.memory_file)
        
        data = {
            'conversation_history': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp,
                    'metadata': msg.metadata or {}
                }
                for msg in self.memory.conversation_history[-100:]  # حفظ آخر 100 رسالة فقط
            ],
            'user_preferences': self.memory.user_preferences,
            'context': self.memory.context,
            'created_at': self.memory.created_at,
            'last_updated': self.memory.last_updated
        }
        
        try:
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """إضافة رسالة إلى المحادثة"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )
        self.memory.conversation_history.append(message)
        self._save_memory()
    
    def get_conversation_context(self, last_n: int = 10) -> List[Message]:
        """الحصول على سياق المحادثة"""
        return self.memory.conversation_history[-last_n:]
    
    def process_query(self, user_query: str) -> str:
        """معالجة استعلام المستخدم"""
        # إضافة رسالة المستخدم
        self.add_message('user', user_query)
        
        # تحليل الاستعلام وتحديد نوع المهمة
        task_type = self._analyze_task(user_query)
        
        # معالجة الاستعلام بناءً على نوع المهمة
        response = self._generate_response(user_query, task_type)
        
        # إضافة رد الوكيل
        self.add_message('assistant', response, metadata={'task_type': task_type})
        
        return response
    
    def _analyze_task(self, query: str) -> str:
        """تحليل نوع المهمة من الاستعلام"""
        query_lower = query.lower()
        
        # كلمات مفتاحية للترجمة
        if any(word in query_lower for word in ['ترجم', 'translate', 'translation']):
            return 'translation'
        
        # كلمات مفتاحية للكود
        if any(word in query_lower for word in ['كود', 'code', 'برمجة', 'programming', 'function', 'class']):
            return 'code_assistance'
        
        # كلمات مفتاحية للتحليل
        if any(word in query_lower for word in ['حلل', 'analyze', 'analysis', 'تحليل']):
            return 'data_analysis'
        
        # كلمات مفتاحية للخلاصة
        if any(word in query_lower for word in ['لخص', 'summarize', 'summary', 'خلاصة']):
            return 'summarization'
        
        # كلمات مفتاحية للأسئلة
        if any(word in query_lower for word in ['؟', '?', 'what', 'how', 'why', 'ماذا', 'كيف', 'لماذا']):
            return 'question_answering'
        
        return 'conversation'
    
    def _generate_response(self, query: str, task_type: str) -> str:
        """إنشاء رد بناءً على نوع المهمة"""
        context = self.get_conversation_context(5)
        context_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in context
        ])
        
        if task_type == 'translation':
            return self._handle_translation(query)
        elif task_type == 'code_assistance':
            return self._handle_code_assistance(query)
        elif task_type == 'data_analysis':
            return self._handle_data_analysis(query)
        elif task_type == 'summarization':
            return self._handle_summarization(query)
        elif task_type == 'question_answering':
            return self._handle_question_answering(query)
        else:
            return self._handle_conversation(query, context_text)
    
    def _handle_translation(self, query: str) -> str:
        """معالجة طلبات الترجمة"""
        # هذا مثال بسيط - يمكن تحسينه باستخدام APIs حقيقية
        if 'english' in query.lower() or 'إنجليزي' in query:
            return f"أنا جاهز لترجمة النص إلى الإنجليزية. يرجى إرسال النص الذي تريد ترجمته."
        elif 'arabic' in query.lower() or 'عربي' in query:
            return f"أنا جاهز لترجمة النص إلى العربية. يرجى إرسال النص الذي تريد ترجمته."
        return "أنا جاهز لمساعدتك في الترجمة. ما هي اللغة التي تريد الترجمة منها وإليها؟"
    
    def _handle_code_assistance(self, query: str) -> str:
        """معالجة طلبات المساعدة في البرمجة"""
        return f"أنا هنا لمساعدتك في البرمجة! يمكنني:\n" \
               f"- كتابة الكود\n" \
               f"- شرح الكود\n" \
               f"- إصلاح الأخطاء\n" \
               f"- تحسين الأداء\n\n" \
               f"ما الذي تحتاج مساعدة فيه بالضبط؟"
    
    def _handle_data_analysis(self, query: str) -> str:
        """معالجة طلبات تحليل البيانات"""
        return f"أنا جاهز لتحليل البيانات! يمكنني:\n" \
               f"- تحليل البيانات الإحصائية\n" \
               f"- إنشاء الرسوم البيانية\n" \
               f"- استخراج الأنماط والاتجاهات\n" \
               f"- تقديم التوصيات\n\n" \
               f"ما هي البيانات التي تريد تحليلها؟"
    
    def _handle_summarization(self, query: str) -> str:
        """معالجة طلبات التلخيص"""
        return f"أنا جاهز لإنشاء ملخصات! يرجى إرسال النص أو المحتوى الذي تريد تلخيصه."
    
    def _handle_question_answering(self, query: str) -> str:
        """معالجة الأسئلة"""
        # استخدام سياق المحادثة للإجابة
        return f"بناءً على سؤالك، سأحاول تقديم إجابة شاملة ومفيدة. " \
               f"هل يمكنك توضيح سؤالك أكثر إذا لزم الأمر؟"
    
    def _handle_conversation(self, query: str, context: str) -> str:
        """معالجة المحادثة العامة"""
        greetings = ['مرحبا', 'hello', 'hi', 'أهلا', 'سلام']
        if any(greeting in query.lower() for greeting in greetings):
            return f"مرحباً! أنا {self.name}، وكيل الذكاء الاصطناعي الخاص بك. " \
                   f"كيف يمكنني مساعدتك اليوم؟"
        
        return f"شكراً على رسالتك. أنا هنا لمساعدتك في أي شيء تحتاجه. " \
               f"يمكنني المساعدة في البرمجة، التحليل، الترجمة، وأكثر من ذلك!"
    
    def update_preferences(self, key: str, value: Any):
        """تحديث تفضيلات المستخدم"""
        self.memory.user_preferences[key] = value
        self._save_memory()
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات المحادثة"""
        total_messages = len(self.memory.conversation_history)
        user_messages = sum(1 for msg in self.memory.conversation_history if msg.role == 'user')
        assistant_messages = sum(1 for msg in self.memory.conversation_history if msg.role == 'assistant')
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'conversation_started': self.memory.created_at,
            'last_activity': self.memory.last_updated,
            'capabilities': list(self.capabilities.keys())
        }
    
    def clear_memory(self):
        """مسح الذاكرة"""
        self.memory.conversation_history = []
        self.memory.context = {}
        self._save_memory()
    
    def export_conversation(self, filepath: str):
        """تصدير المحادثة إلى ملف"""
        data = {
            'agent_name': self.name,
            'exported_at': datetime.now().isoformat(),
            'conversation': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in self.memory.conversation_history
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
