"""
اختبارات نظام الوكيل
Agent System Tests
"""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent import (
    MasterAgent,
    AIAgent,
    Task,
    TaskStatus,
    AgentRole,
    ResearchAgent,
    DataAnalystAgent,
    CoderAgent,
    PlannerAgent,
    LanguageAgent
)


class TestAIAgent(unittest.TestCase):
    """اختبارات الوكيل الأساسي"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.agent = AIAgent(
            name="Test Agent",
            role=AgentRole.ASSISTANT,
            capabilities=["test"]
        )
    
    def test_agent_creation(self):
        """اختبار إنشاء الوكيل"""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.role, AgentRole.ASSISTANT)
        self.assertTrue(self.agent.active)
    
    def test_perceive(self):
        """اختبار الإدراك"""
        input_data = {"type": "message", "content": "test"}
        perception = self.agent.perceive(input_data)
        
        self.assertEqual(perception["type"], "message")
        self.assertEqual(perception["content"], "test")
    
    def test_process(self):
        """اختبار المعالجة"""
        input_data = {"type": "task", "content": "test task"}
        result = self.agent.process(input_data)
        
        self.assertIn("agent", result)
        self.assertIn("perception", result)
        self.assertIn("decision", result)
        self.assertIn("result", result)
    
    def test_add_task(self):
        """اختبار إضافة مهمة"""
        task = Task("test task")
        self.agent.add_task(task)
        
        self.assertEqual(len(self.agent.tasks), 1)
        self.assertEqual(task.assigned_agent, self.agent.name)
    
    def test_get_status(self):
        """اختبار الحصول على الحالة"""
        status = self.agent.get_status()
        
        self.assertIn("name", status)
        self.assertIn("role", status)
        self.assertIn("stats", status)


class TestMasterAgent(unittest.TestCase):
    """اختبارات الوكيل الرئيسي"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.master = MasterAgent("Test Master")
    
    def test_master_creation(self):
        """اختبار إنشاء الوكيل الرئيسي"""
        self.assertEqual(self.master.role, AgentRole.MASTER)
        self.assertEqual(len(self.master.sub_agents), 0)
    
    def test_add_sub_agent(self):
        """اختبار إضافة وكيل فرعي"""
        sub_agent = ResearchAgent()
        self.master.add_sub_agent(sub_agent)
        
        self.assertEqual(len(self.master.sub_agents), 1)
    
    def test_delegate_task(self):
        """اختبار تفويض المهمة"""
        analyst = DataAnalystAgent()
        self.master.add_sub_agent(analyst)
        
        task = Task("analyze data", task_type="analysis")
        assigned = self.master.delegate_task(task)
        
        self.assertIsNotNone(assigned)
    
    def test_coordinate(self):
        """اختبار التنسيق"""
        self.master.add_sub_agent(CoderAgent())
        
        result = self.master.coordinate("write code")
        
        self.assertIn("status", result)
        self.assertIn("task", result)
    
    def test_chat(self):
        """اختبار المحادثة"""
        response = self.master.chat("hello")
        
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)


class TestSpecializedAgents(unittest.TestCase):
    """اختبارات الوكلاء المتخصصين"""
    
    def test_research_agent(self):
        """اختبار وكيل البحث"""
        agent = ResearchAgent()
        
        self.assertEqual(agent.role, AgentRole.RESEARCHER)
        self.assertIn("research", agent.capabilities)
        
        # اختبار البحث
        results = agent.search_web("test query")
        self.assertIn("results", results)
    
    def test_data_analyst_agent(self):
        """اختبار وكيل تحليل البيانات"""
        agent = DataAnalystAgent()
        
        self.assertEqual(agent.role, AgentRole.ANALYST)
        
        # اختبار التحليل
        data = [1, 2, 3, 4, 5]
        analysis = agent.analyze_data(data)
        
        self.assertIn("count", analysis)
        self.assertIn("mean", analysis)
        self.assertEqual(analysis["mean"], 3.0)
    
    def test_coder_agent(self):
        """اختبار وكيل البرمجة"""
        agent = CoderAgent()
        
        self.assertEqual(agent.role, AgentRole.CODER)
        
        # اختبار توليد الكود
        code = agent.generate_code("calculate function")
        
        self.assertIsInstance(code, str)
        self.assertTrue(len(code) > 0)
    
    def test_planner_agent(self):
        """اختبار وكيل التخطيط"""
        agent = PlannerAgent()
        
        self.assertEqual(agent.role, AgentRole.PLANNER)
        
        # اختبار إنشاء الخطة
        plan = agent.create_plan("test goal")
        
        self.assertIn("goal", plan)
        self.assertIn("steps", plan)
        self.assertIn("milestones", plan)
    
    def test_language_agent(self):
        """اختبار وكيل معالجة اللغات"""
        agent = LanguageAgent()
        
        # اختبار تحليل المشاعر
        sentiment = agent.analyze_sentiment("This is great!")
        
        self.assertIn("sentiment", sentiment)
        self.assertIn("score", sentiment)


class TestTask(unittest.TestCase):
    """اختبارات المهام"""
    
    def test_task_creation(self):
        """اختبار إنشاء مهمة"""
        task = Task("test task", priority=2, task_type="test")
        
        self.assertEqual(task.description, "test task")
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.task_type, "test")
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_task_to_dict(self):
        """اختبار تحويل المهمة إلى قاموس"""
        task = Task("test")
        task_dict = task.to_dict()
        
        self.assertIn("id", task_dict)
        self.assertIn("description", task_dict)
        self.assertIn("status", task_dict)


def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 تشغيل الاختبارات...\n")
    
    # إنشاء مجموعة الاختبارات
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAIAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestMasterAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestSpecializedAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestTask))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # عرض النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print("=" * 60)
    print(f"✓ اختبارات نجحت: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ اختبارات فشلت: {len(result.failures)}")
    print(f"⚠ أخطاء: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
