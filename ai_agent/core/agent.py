"""
نظام الوكيل الذكي الرئيسي
Main AI Agent System
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentRole(Enum):
    """أدوار الوكلاء المختلفة"""
    MASTER = "master"  # الوكيل الرئيسي
    ASSISTANT = "assistant"  # مساعد عام
    RESEARCHER = "researcher"  # باحث
    ANALYST = "analyst"  # محلل بيانات
    CODER = "coder"  # مبرمج
    PLANNER = "planner"  # مخطط
    EXECUTOR = "executor"  # منفذ


class TaskStatus(Enum):
    """حالات المهام"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """فئة المهمة"""
    def __init__(self, description: str, priority: int = 1, task_type: str = "general"):
        self.id = f"task_{int(time.time() * 1000)}"
        self.description = description
        self.priority = priority
        self.task_type = task_type
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at = None
        self.result = None
        self.subtasks = []
        self.assigned_agent = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "task_type": self.task_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "assigned_agent": self.assigned_agent
        }


class Memory:
    """نظام الذاكرة للوكيل"""
    def __init__(self, max_size: int = 1000):
        self.short_term = []  # ذاكرة قصيرة المدى
        self.long_term = []  # ذاكرة طويلة المدى
        self.max_size = max_size
        self.facts = {}  # حقائق مهمة
        
    def add_to_short_term(self, item: Dict[str, Any]):
        """إضافة إلى الذاكرة قصيرة المدى"""
        self.short_term.append({
            "timestamp": datetime.now().isoformat(),
            "data": item
        })
        if len(self.short_term) > 50:
            # نقل إلى الذاكرة طويلة المدى
            self.long_term.append(self.short_term.pop(0))
            
    def add_fact(self, key: str, value: Any):
        """إضافة حقيقة مهمة"""
        self.facts[key] = value
        
    def get_context(self, n: int = 10) -> List[Dict[str, Any]]:
        """الحصول على السياق الأخير"""
        return self.short_term[-n:]
        
    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """البحث في الذاكرة"""
        results = []
        for item in self.short_term + self.long_term:
            if query.lower() in str(item).lower():
                results.append(item)
        return results


class AIAgent:
    """الوكيل الذكي الأساسي"""
    
    def __init__(self, name: str, role: AgentRole, capabilities: List[str]):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.memory = Memory()
        self.tasks = []
        self.active = True
        self.created_at = datetime.now()
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0
        }
        
    def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """إدراك وتحليل المدخلات"""
        perception = {
            "timestamp": datetime.now().isoformat(),
            "type": input_data.get("type", "unknown"),
            "content": input_data.get("content", ""),
            "priority": input_data.get("priority", 1)
        }
        self.memory.add_to_short_term(perception)
        return perception
        
    def think(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """التفكير واتخاذ القرار"""
        context = self.memory.get_context()
        
        decision = {
            "action": "process",
            "reasoning": f"معالجة المدخلات بناءً على دور {self.role.value}",
            "confidence": 0.8,
            "next_steps": []
        }
        
        # تحليل نوع المهمة
        content = perception.get("content", "").lower()
        
        if "تحليل" in content or "analyze" in content:
            decision["action"] = "analyze"
            decision["next_steps"] = ["جمع البيانات", "تحليل", "تقرير"]
        elif "بحث" in content or "search" in content:
            decision["action"] = "research"
            decision["next_steps"] = ["بحث", "تجميع النتائج", "تلخيص"]
        elif "كود" in content or "code" in content or "برمجة" in content:
            decision["action"] = "code"
            decision["next_steps"] = ["فهم المتطلبات", "تصميم", "برمجة", "اختبار"]
        elif "خطة" in content or "plan" in content:
            decision["action"] = "plan"
            decision["next_steps"] = ["تحديد الأهداف", "وضع الخطة", "تحديد الموارد"]
            
        return decision
        
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ القرار"""
        start_time = time.time()
        
        result = {
            "action_taken": decision["action"],
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": f"تم تنفيذ {decision['action']} بنجاح",
            "details": {}
        }
        
        # محاكاة التنفيذ
        action = decision["action"]
        
        if action == "analyze":
            result["output"] = "تم إجراء التحليل بنجاح"
            result["details"] = {
                "analysis_type": "comprehensive",
                "findings": ["نتيجة 1", "نتيجة 2", "نتيجة 3"]
            }
        elif action == "research":
            result["output"] = "تم البحث وجمع المعلومات"
            result["details"] = {
                "sources_found": 5,
                "summary": "ملخص نتائج البحث"
            }
        elif action == "code":
            result["output"] = "تم كتابة الكود المطلوب"
            result["details"] = {
                "language": "python",
                "lines_of_code": 150
            }
        elif action == "plan":
            result["output"] = "تم وضع خطة تفصيلية"
            result["details"] = {
                "steps": decision.get("next_steps", []),
                "estimated_time": "2 hours"
            }
            
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        self.stats["total_execution_time"] += execution_time
        
        self.memory.add_to_short_term(result)
        return result
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """دورة المعالجة الكاملة: إدراك -> تفكير -> تنفيذ"""
        perception = self.perceive(input_data)
        decision = self.think(perception)
        result = self.act(decision)
        
        return {
            "agent": self.name,
            "role": self.role.value,
            "perception": perception,
            "decision": decision,
            "result": result
        }
        
    def add_task(self, task: Task):
        """إضافة مهمة للوكيل"""
        task.assigned_agent = self.name
        self.tasks.append(task)
        
    def execute_tasks(self) -> List[Dict[str, Any]]:
        """تنفيذ المهام المعلقة"""
        results = []
        
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS
                
                result = self.process({
                    "type": "task",
                    "content": task.description,
                    "priority": task.priority
                })
                
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                
                self.stats["tasks_completed"] += 1
                results.append(result)
                
        return results
        
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الوكيل"""
        return {
            "name": self.name,
            "role": self.role.value,
            "active": self.active,
            "capabilities": self.capabilities,
            "stats": self.stats,
            "pending_tasks": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            "completed_tasks": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
            "memory_size": len(self.memory.short_term) + len(self.memory.long_term)
        }


class MasterAgent(AIAgent):
    """الوكيل الرئيسي الذي يدير الوكلاء الآخرين"""
    
    def __init__(self, name: str = "المساعد الرئيسي"):
        super().__init__(
            name=name,
            role=AgentRole.MASTER,
            capabilities=[
                "task_management",
                "agent_coordination",
                "decision_making",
                "resource_allocation",
                "conversation",
                "planning"
            ]
        )
        self.sub_agents = []
        
    def add_sub_agent(self, agent: AIAgent):
        """إضافة وكيل فرعي"""
        self.sub_agents.append(agent)
        self.memory.add_fact(f"agent_{agent.name}", agent.get_status())
        
    def delegate_task(self, task: Task) -> Optional[AIAgent]:
        """تفويض المهمة للوكيل المناسب"""
        # اختيار الوكيل الأنسب بناءً على نوع المهمة
        task_type = task.task_type.lower()
        
        for agent in self.sub_agents:
            if task_type in [cap.lower() for cap in agent.capabilities]:
                agent.add_task(task)
                return agent
                
        # إذا لم يتم العثور على وكيل مناسب، المعالجة ذاتياً
        self.add_task(task)
        return self
        
    def coordinate(self, user_input: str) -> Dict[str, Any]:
        """تنسيق المهام بين الوكلاء"""
        # إنشاء مهمة من المدخلات
        task = Task(
            description=user_input,
            priority=1,
            task_type=self._classify_task(user_input)
        )
        
        # تفويض المهمة
        assigned_agent = self.delegate_task(task)
        
        # تنفيذ المهمة
        if assigned_agent:
            results = assigned_agent.execute_tasks()
            
            return {
                "status": "success",
                "task": task.to_dict(),
                "assigned_to": assigned_agent.name,
                "results": results
            }
        else:
            return {
                "status": "failed",
                "message": "لم يتم العثور على وكيل مناسب",
                "task": task.to_dict()
            }
            
    def _classify_task(self, text: str) -> str:
        """تصنيف نوع المهمة"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["تحليل", "analyze", "بيانات", "data"]):
            return "analysis"
        elif any(word in text_lower for word in ["بحث", "search", "ابحث", "find"]):
            return "research"
        elif any(word in text_lower for word in ["كود", "code", "برمجة", "program"]):
            return "coding"
        elif any(word in text_lower for word in ["خطة", "plan", "جدول", "schedule"]):
            return "planning"
        else:
            return "general"
            
    def chat(self, message: str) -> str:
        """محادثة مع الوكيل"""
        result = self.coordinate(message)
        
        if result["status"] == "success":
            output = result["results"][0]["result"]["output"]
            return f"✓ {output}"
        else:
            return f"✗ {result['message']}"
            
    def get_full_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام الكامل"""
        return {
            "master_agent": self.get_status(),
            "sub_agents": [agent.get_status() for agent in self.sub_agents],
            "total_agents": len(self.sub_agents) + 1,
            "system_health": "healthy" if self.active else "inactive"
        }
