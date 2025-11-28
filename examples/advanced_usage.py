"""
أمثلة متقدمة للاستخدام
Advanced Usage Examples
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent import (
    MasterAgent,
    ResearchAgent,
    DataAnalystAgent,
    CoderAgent,
    Task,
    TaskStatus,
    KnowledgeBase,
    ConversationManager
)


def example_custom_workflow():
    """مثال: سير عمل مخصص"""
    print("=" * 60)
    print("مثال: سير عمل مخصص متقدم")
    print("=" * 60)
    
    # إنشاء نظام متكامل
    master = MasterAgent("المدير التنفيذي")
    researcher = ResearchAgent()
    analyst = DataAnalystAgent()
    coder = CoderAgent()
    
    master.add_sub_agent(researcher)
    master.add_sub_agent(analyst)
    master.add_sub_agent(coder)
    
    # تعريف مشروع متكامل
    project_tasks = [
        ("البحث عن أفضل ممارسات تطوير API", "research"),
        ("تحليل متطلبات المشروع", "analysis"),
        ("كتابة كود الخادم الأساسي", "coding"),
        ("مراجعة وتحسين الكود", "coding")
    ]
    
    print("\n🎯 المشروع: تطوير API متكامل")
    print("\n📋 المهام:")
    
    for i, (desc, task_type) in enumerate(project_tasks, 1):
        print(f"  {i}. {desc} ({task_type})")
        
        task = Task(desc, priority=i, task_type=task_type)
        assigned_agent = master.delegate_task(task)
        
        print(f"     ✓ تم التفويض إلى: {assigned_agent.name}")
        
        # محاكاة التنفيذ
        time.sleep(0.5)
        
        result = assigned_agent.execute_tasks()
        if result:
            print(f"     ✓ اكتمل بنجاح")


def example_conversation_context():
    """مثال: السياق في المحادثات"""
    print("\n" + "=" * 60)
    print("مثال: إدارة السياق في المحادثات")
    print("=" * 60)
    
    kb = KnowledgeBase(":memory:")
    conv_manager = ConversationManager(kb)
    
    # محادثة متعددة الرسائل
    messages = [
        "مرحبا، أريد تعلم البرمجة",
        "ما هي أفضل لغة للمبتدئين؟",
        "كم من الوقت أحتاج للتعلم؟",
        "هل يمكنك وضع خطة دراسية؟"
    ]
    
    print("\n💬 محادثة متواصلة:")
    
    for msg in messages:
        print(f"\n👤 المستخدم: {msg}")
        
        result = conv_manager.process_message(msg)
        print(f"🤖 الوكيل: {result['agent_response']}")
        
        # عرض السياق الحالي
        context = conv_manager.get_context()
        print(f"📎 السياق: آخر رسالة في {context.get('timestamp', 'N/A')[:19]}")
    
    kb.close()


def example_collaborative_agents():
    """مثال: تعاون الوكلاء"""
    print("\n" + "=" * 60)
    print("مثال: تعاون الوكلاء لحل مشكلة معقدة")
    print("=" * 60)
    
    master = MasterAgent("المنسق")
    
    # إضافة وكلاء متخصصين
    researcher = ResearchAgent()
    analyst = DataAnalystAgent()
    coder = CoderAgent()
    
    master.add_sub_agent(researcher)
    master.add_sub_agent(analyst)
    master.add_sub_agent(coder)
    
    # مشكلة معقدة تحتاج تعاون
    problem = """
    نحتاج إلى تطوير نظام تحليل بيانات يقوم بـ:
    1. جمع البيانات من مصادر متعددة
    2. تحليل البيانات إحصائياً
    3. إنشاء تقارير تلقائية
    """
    
    print(f"\n🎯 المشكلة:\n{problem}")
    print("\n🔄 مراحل الحل:\n")
    
    # المرحلة 1: البحث
    print("1️⃣ مرحلة البحث:")
    research_task = Task("البحث عن أدوات تحليل البيانات", task_type="research")
    researcher.add_task(research_task)
    research_results = researcher.execute_tasks()
    print(f"   ✓ {research_results[0]['result']['output']}")
    
    # المرحلة 2: التحليل
    print("\n2️⃣ مرحلة التحليل:")
    analysis_task = Task("تحليل متطلبات النظام", task_type="analysis")
    analyst.add_task(analysis_task)
    analysis_results = analyst.execute_tasks()
    print(f"   ✓ {analysis_results[0]['result']['output']}")
    
    # المرحلة 3: البرمجة
    print("\n3️⃣ مرحلة البرمجة:")
    coding_task = Task("كتابة كود جمع وتحليل البيانات", task_type="coding")
    coder.add_task(coding_task)
    coding_results = coder.execute_tasks()
    print(f"   ✓ {coding_results[0]['result']['output']}")
    
    print("\n\n🎉 اكتمل المشروع بنجاح!")


def example_dynamic_learning():
    """مثال: التعلم الديناميكي"""
    print("\n" + "=" * 60)
    print("مثال: التعلم من التجارب السابقة")
    print("=" * 60)
    
    kb = KnowledgeBase(":memory:")
    
    # إضافة خبرات سابقة
    experiences = [
        ("مشروع A", {"نوع": "تطوير ويب", "نجاح": True, "مدة": 30}),
        ("مشروع B", {"نوع": "تطوير ويب", "نجاح": True, "مدة": 45}),
        ("مشروع C", {"نوع": "تحليل بيانات", "نجاح": True, "مدة": 20}),
    ]
    
    print("\n📚 إضافة خبرات سابقة:")
    for project, details in experiences:
        kb.add_fact("مشاريع", project, details, source="experience")
        print(f"  ✓ {project}: {details['نوع']}")
    
    # البحث عن أنماط
    print("\n\n🔍 البحث عن أنماط في المشاريع:")
    web_projects = kb.search_facts("تطوير ويب", category="مشاريع")
    
    if web_projects:
        print(f"  - وجدنا {len(web_projects)} مشاريع تطوير ويب")
        
        total_duration = sum(p['value']['مدة'] for p in web_projects)
        avg_duration = total_duration / len(web_projects)
        
        print(f"  - متوسط المدة: {avg_duration:.1f} يوم")
        print(f"  - معدل النجاح: 100%")
    
    # استخدام المعرفة لتقدير مشروع جديد
    print("\n\n💡 تقدير مشروع جديد:")
    print("  المشروع: تطوير منصة ويب جديدة")
    print(f"  التقدير بناءً على الخبرة: {avg_duration:.0f}-{avg_duration * 1.5:.0f} يوم")
    
    kb.close()


def example_error_handling():
    """مثال: معالجة الأخطاء"""
    print("\n" + "=" * 60)
    print("مثال: معالجة الأخطاء والاستثناءات")
    print("=" * 60)
    
    master = MasterAgent()
    analyst = DataAnalystAgent()
    master.add_sub_agent(analyst)
    
    # حالات مختلفة
    test_cases = [
        ("تحليل بيانات صحيحة: [1, 2, 3, 4, 5]", "success"),
        ("تحليل قائمة فارغة: []", "empty_data"),
        ("طلب غير واضح: asdfjkl", "unclear_request"),
    ]
    
    print("\n🧪 اختبار حالات مختلفة:\n")
    
    for test, expected in test_cases:
        print(f"📝 الحالة: {test}")
        print(f"   المتوقع: {expected}")
        
        try:
            result = master.coordinate(test)
            
            if result["status"] == "success":
                print(f"   ✓ نجح التنفيذ")
            else:
                print(f"   ⚠️ فشل التنفيذ: {result.get('message', 'خطأ غير معروف')}")
        except Exception as e:
            print(f"   ✗ استثناء: {str(e)}")
        
        print()


def example_performance_monitoring():
    """مثال: مراقبة الأداء"""
    print("\n" + "=" * 60)
    print("مثال: مراقبة أداء الوكلاء")
    print("=" * 60)
    
    master = MasterAgent()
    agents = [
        ResearchAgent(),
        DataAnalystAgent(),
        CoderAgent()
    ]
    
    for agent in agents:
        master.add_sub_agent(agent)
    
    # تنفيذ عدة مهام
    print("\n⚡ تنفيذ مهام متعددة:\n")
    
    tasks = [
        "ابحث عن معلومات",
        "حلل البيانات: [1, 2, 3]",
        "اكتب كود بايثون"
    ] * 3  # تكرار 3 مرات
    
    start_time = time.time()
    
    for i, task in enumerate(tasks, 1):
        result = master.coordinate(task)
        print(f"  ✓ مهمة {i}/{len(tasks)} اكتملت")
    
    total_time = time.time() - start_time
    
    # عرض الإحصائيات
    print(f"\n\n📊 إحصائيات الأداء:")
    print(f"  - إجمالي الوقت: {total_time:.2f} ثانية")
    print(f"  - متوسط وقت المهمة: {total_time/len(tasks):.3f} ثانية")
    print(f"  - معدل المعالجة: {len(tasks)/total_time:.2f} مهمة/ثانية")
    
    status = master.get_full_status()
    print(f"\n👥 أداء الوكلاء:")
    
    for agent_info in status['sub_agents']:
        print(f"\n  {agent_info['name']}:")
        print(f"    - المهام المنجزة: {agent_info['stats']['tasks_completed']}")
        print(f"    - وقت التنفيذ: {agent_info['stats']['total_execution_time']:.3f}s")


def main():
    """تشغيل الأمثلة المتقدمة"""
    print("\n")
    print("🚀" * 30)
    print("نظام الوكيل الذكي - أمثلة متقدمة")
    print("🚀" * 30)
    
    examples = [
        example_custom_workflow,
        example_conversation_context,
        example_collaborative_agents,
        example_dynamic_learning,
        example_error_handling,
        example_performance_monitoring
    ]
    
    for example in examples:
        try:
            example()
            print("\n✓ اكتمل المثال بنجاح!")
        except Exception as e:
            print(f"\n✗ خطأ: {e}")
        
        input("\n\nاضغط Enter للمتابعة...")
    
    print("\n\n🎉 اكتملت جميع الأمثلة المتقدمة!")


if __name__ == "__main__":
    main()
