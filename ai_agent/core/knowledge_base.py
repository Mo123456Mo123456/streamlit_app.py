"""
قاعدة المعرفة للوكيل الذكي
Knowledge Base System
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path


class KnowledgeBase:
    """قاعدة معرفة للوكيل الذكي"""
    
    def __init__(self, db_path: str = "ai_agent_knowledge.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
        
    def _initialize_database(self):
        """تهيئة قاعدة البيانات"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.connection.cursor()
        
        # جدول الحقائق
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # جدول المحادثات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # جدول المهارات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        """)
        
        self.connection.commit()
        
    def add_fact(self, category: str, key: str, value: Any, confidence: float = 1.0, source: str = "system"):
        """إضافة حقيقة إلى قاعدة المعرفة"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO facts (category, key, value, confidence, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, key, json.dumps(value), confidence, source, now, now))
        
        self.connection.commit()
        
    def get_fact(self, category: str, key: str) -> Optional[Any]:
        """الحصول على حقيقة من قاعدة المعرفة"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT value FROM facts
            WHERE category = ? AND key = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (category, key))
        
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None
        
    def search_facts(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """البحث في الحقائق"""
        cursor = self.connection.cursor()
        
        if category:
            cursor.execute("""
                SELECT category, key, value, confidence, source, created_at
                FROM facts
                WHERE category = ? AND (key LIKE ? OR value LIKE ?)
                ORDER BY confidence DESC
            """, (category, f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("""
                SELECT category, key, value, confidence, source, created_at
                FROM facts
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY confidence DESC
            """, (f"%{query}%", f"%{query}%"))
            
        results = []
        for row in cursor.fetchall():
            results.append({
                "category": row[0],
                "key": row[1],
                "value": json.loads(row[2]),
                "confidence": row[3],
                "source": row[4],
                "created_at": row[5]
            })
            
        return results
        
    def add_conversation(self, user_message: str, agent_response: str, context: Dict[str, Any] = None):
        """إضافة محادثة إلى السجل"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (user_message, agent_response, context, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_message, agent_response, json.dumps(context) if context else None, datetime.now().isoformat()))
        
        self.connection.commit()
        
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """الحصول على سجل المحادثات"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT user_message, agent_response, context, timestamp
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "user_message": row[0],
                "agent_response": row[1],
                "context": json.loads(row[2]) if row[2] else None,
                "timestamp": row[3]
            })
            
        return list(reversed(history))
        
    def add_skill(self, name: str, description: str, category: str):
        """إضافة مهارة جديدة"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO skills (name, description, category)
                VALUES (?, ?, ?)
            """, (name, description, category))
            self.connection.commit()
        except sqlite3.IntegrityError:
            # المهارة موجودة بالفعل
            pass
            
    def update_skill_stats(self, name: str, success: bool = True):
        """تحديث إحصائيات المهارة"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            UPDATE skills
            SET usage_count = usage_count + 1,
                success_rate = (success_rate * usage_count + ?) / (usage_count + 1)
            WHERE name = ?
        """, (1.0 if success else 0.0, name))
        
        self.connection.commit()
        
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """الحصول على جميع المهارات"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT name, description, category, usage_count, success_rate
            FROM skills
            ORDER BY usage_count DESC
        """)
        
        skills = []
        for row in cursor.fetchall():
            skills.append({
                "name": row[0],
                "description": row[1],
                "category": row[2],
                "usage_count": row[3],
                "success_rate": row[4]
            })
            
        return skills
        
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات قاعدة المعرفة"""
        cursor = self.connection.cursor()
        
        stats = {}
        
        # عدد الحقائق
        cursor.execute("SELECT COUNT(*) FROM facts")
        stats["total_facts"] = cursor.fetchone()[0]
        
        # عدد المحادثات
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats["total_conversations"] = cursor.fetchone()[0]
        
        # عدد المهارات
        cursor.execute("SELECT COUNT(*) FROM skills")
        stats["total_skills"] = cursor.fetchone()[0]
        
        # الفئات الأكثر شيوعاً
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM facts
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """)
        stats["top_categories"] = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return stats
        
    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        if self.connection:
            self.connection.close()


class ConversationManager:
    """مدير المحادثات"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.current_context = {}
        
    def process_message(self, user_message: str, agent_name: str = "AI Agent") -> Dict[str, Any]:
        """معالجة رسالة المستخدم"""
        # تحديث السياق
        self.current_context["last_message"] = user_message
        self.current_context["timestamp"] = datetime.now().isoformat()
        
        # توليد استجابة (في التطبيق الحقيقي، استخدم نموذج لغوي)
        response = self._generate_response(user_message)
        
        # حفظ المحادثة
        self.kb.add_conversation(user_message, response, self.current_context.copy())
        
        return {
            "user_message": user_message,
            "agent_response": response,
            "context": self.current_context.copy()
        }
        
    def _generate_response(self, message: str) -> str:
        """توليد استجابة للرسالة"""
        message_lower = message.lower()
        
        # استجابات بسيطة
        if any(word in message_lower for word in ["مرحبا", "السلام", "hello", "hi"]):
            return "مرحباً! كيف يمكنني مساعدتك اليوم؟"
        elif any(word in message_lower for word in ["كيف حالك", "how are you"]):
            return "أنا بخير، شكراً لسؤالك! كيف يمكنني خدمتك؟"
        elif any(word in message_lower for word in ["ساعدني", "help", "مساعدة"]):
            return "بالتأكيد! أنا هنا للمساعدة. يمكنني القيام بالعديد من المهام مثل البحث، التحليل، البرمجة، والتخطيط. ماذا تحتاج؟"
        elif any(word in message_lower for word in ["شكرا", "thank"]):
            return "العفو! سعيد بخدمتك. هل تحتاج أي شيء آخر؟"
        else:
            return f"فهمت طلبك: '{message}'. سأقوم بمعالجته الآن..."
            
    def get_context(self) -> Dict[str, Any]:
        """الحصول على السياق الحالي"""
        return self.current_context.copy()
        
    def clear_context(self):
        """مسح السياق"""
        self.current_context = {}
