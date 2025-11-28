"""
نظام الوكيل الذكي المتكامل
Complete AI Agent System

نظام ذكاء اصطناعي متعدد الوكلاء مع قدرات متقدمة
"""

__version__ = "1.0.0"
__author__ = "AI Agent System"

from .core.agent import MasterAgent, AIAgent, Task, TaskStatus, AgentRole
from .agents.specialized_agents import (
    ResearchAgent,
    DataAnalystAgent,
    CoderAgent,
    PlannerAgent,
    LanguageAgent
)
from .core.knowledge_base import KnowledgeBase, ConversationManager

__all__ = [
    "MasterAgent",
    "AIAgent",
    "Task",
    "TaskStatus",
    "AgentRole",
    "ResearchAgent",
    "DataAnalystAgent",
    "CoderAgent",
    "PlannerAgent",
    "LanguageAgent",
    "KnowledgeBase",
    "ConversationManager"
]
