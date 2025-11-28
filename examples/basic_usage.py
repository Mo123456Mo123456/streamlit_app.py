"""
أمثلة على الاستخدام الأساسي
Basic Usage Examples
"""

import sys
from pathlib import Path

# إضافة المسار الرئيسي
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent import (
    MasterAgent,
    ResearchAgent,
    DataAnalystAgent,
    CoderAgent,
    PlannerAgent,
    LanguageAgent,
    KnowledgeBase
)


def example_1_basic_chat():
    """مثال 1: محادثة بسيطة"""
    print("=" * 60)
    print("مثال 1: محادثة بسيطة مع الوكيل")
    print("=" * 60)
    
    master = MasterAgent("المساعد")
    
    messages = [
        "مرحبا",
        "كيف حالك؟",
        "ماذا يمكنك أن تفعل؟"
    ]
    
    for msg in messages:
        print(f"\n👤 المستخدم: {msg}")
        response = master.chat(msg)
        print(f"🤖 الوكيل: {response}")


def example_2_data_analysis():
    """مثال 2: تحليل بيانات"""
    print("\n" + "=" * 60)
    print("مثال 2: تحليل البيانات")
    print("=" * 60)
    
    analyst = DataAnalystAgent()
    
    data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    print(f"\n📊 البيانات: {data}")
    
    analysis = analyst.analyze_data(data)
    print(f"\n📈 التحليل:")
    for key, value in analysis.items():
        print(f"  - {key}: {value}")
    
    insights = analyst.generate_insights(analysis)
    print(f"\n💡 الرؤى:")
    for insight in insights:
        print(f"  - {insight}")


def example_3_code_generation():
    """مثال 3: توليد الأكواد"""
    print("\n" + "=" * 60)
    print("مثال 3: توليد الأكواد البرمجية")
    print("=" * 60)
    
    coder = CoderAgent()
    
    descriptions = [
        "دالة حساب الأعداد الأولية",
        "إنشاء قائمة بالأرقام الزوجية"
    ]
    
    for desc in descriptions:
        print(f"\n💻 المطلوب: {desc}")
        code = coder.generate_code(desc)
        print("\n📝 الكود المولد:")
        print(code)


def example_4_planning():
    """مثال 4: التخطيط"""
    print("\n" + "=" * 60)
    print("مثال 4: التخطيط ووضع الخطط")
    print("=" * 60)
    
    planner = PlannerAgent()
    
    goal = "تطوير تطبيق ويب"
    
    print(f"\n🎯 الهدف: {goal}")
    
    plan = planner.create_plan(goal)
    
    print(f"\n📋 الخطة:")
    print(f"  الوقت المقدر: {plan['estimated_time']} دقيقة")
    print(f"  الأولوية: {plan['priority']}")
    
    print(f"\n📝 الخطوات:")
    for step in plan['steps']:
        print(f"  {step['step']}. {step['action']} - {step['status']}")
    
    print(f"\n🎯 المعالم الرئيسية:")
    for milestone in plan['milestones']:
        print(f"  ✓ {milestone}")


def example_5_language_processing():
    """مثال 5: معالجة اللغات"""
    print("\n" + "=" * 60)
    print("مثال 5: معالجة اللغات الطبيعية")
    print("=" * 60)
    
    lang_agent = LanguageAgent()
    
    # تحليل المشاعر
    texts = [
        "هذا يوم رائع وجميل!",
        "أشعر بالحزن اليوم",
        "الجو عادي"
    ]
    
    print("\n😊 تحليل المشاعر:")
    for text in texts:
        sentiment = lang_agent.analyze_sentiment(text)
        print(f"\n  النص: {text}")
        print(f"  المشاعر: {sentiment['sentiment']}")
        print(f"  الدرجة: {sentiment['score']:.2f}")
    
    # استخراج الكلمات المفتاحية
    long_text = """
    الذكاء الاصطناعي هو مجال واسع يشمل التعلم الآلي والشبكات العصبية
    ومعالجة اللغات الطبيعية وتعلم الآلة العميق
    """
    
    print("\n\n🔑 استخراج الكلمات المفتاحية:")
    print(f"  النص: {long_text.strip()}")
    
    keywords = lang_agent.extract_keywords(long_text)
    print(f"\n  الكلمات المفتاحية: {', '.join(keywords)}")


def example_6_multi_agent_system():
    """مثال 6: نظام متعدد الوكلاء"""
    print("\n" + "=" * 60)
    print("مثال 6: نظام متعدد الوكلاء")
    print("=" * 60)
    
    # إنشاء الوكيل الرئيسي
    master = MasterAgent("المدير الرئيسي")
    
    # إضافة الوكلاء المتخصصين
    master.add_sub_agent(ResearchAgent())
    master.add_sub_agent(DataAnalystAgent())
    master.add_sub_agent(CoderAgent())
    master.add_sub_agent(PlannerAgent())
    master.add_sub_agent(LanguageAgent())
    
    # عرض حالة النظام
    status = master.get_full_status()
    
    print(f"\n🤖 عدد الوكلاء: {status['total_agents']}")
    print(f"⚡ حالة النظام: {status['system_health']}")
    
    print(f"\n👥 الوكلاء المتاحون:")
    for agent in status['sub_agents']:
        print(f"\n  - {agent['name']} ({agent['role']})")
        print(f"    القدرات: {', '.join(agent['capabilities'])}")
        print(f"    المهام المنجزة: {agent['stats']['tasks_completed']}")
    
    # تنفيذ مهام متعددة
    tasks = [
        "حلل البيانات: [1, 5, 10, 15, 20]",
        "اكتب كود لحساب المتوسط",
        "ضع خطة لمشروع جديد"
    ]
    
    print(f"\n\n📋 تنفيذ المهام:")
    for task in tasks:
        print(f"\n  المهمة: {task}")
        result = master.coordinate(task)
        print(f"  الحالة: {result['status']}")
        print(f"  المسؤول: {result['assigned_to']}")


def example_7_knowledge_base():
    """مثال 7: استخدام قاعدة المعرفة"""
    print("\n" + "=" * 60)
    print("مثال 7: قاعدة المعرفة")
    print("=" * 60)
    
    kb = KnowledgeBase(":memory:")  # استخدام قاعدة بيانات في الذاكرة
    
    # إضافة حقائق
    print("\n➕ إضافة حقائق...")
    kb.add_fact("علوم", "الجاذبية", "قوة تجذب الأجسام نحو بعضها", confidence=1.0)
    kb.add_fact("علوم", "الضوء", "موجة كهرومغناطيسية", confidence=0.95)
    kb.add_fact("تقنية", "AI", "الذكاء الاصطناعي", confidence=1.0)
    
    # البحث في الحقائق
    print("\n🔍 البحث عن 'الجاذبية':")
    results = kb.search_facts("الجاذبية")
    for fact in results:
        print(f"  - الفئة: {fact['category']}")
        print(f"    المفتاح: {fact['key']}")
        print(f"    القيمة: {fact['value']}")
        print(f"    الثقة: {fact['confidence']}")
    
    # إضافة مهارات
    print("\n\n🎯 إضافة مهارات...")
    kb.add_skill("تحليل البيانات", "تحليل وتفسير البيانات", "analysis")
    kb.add_skill("البرمجة", "كتابة الأكواد البرمجية", "coding")
    
    # عرض الإحصائيات
    print("\n📊 إحصائيات قاعدة المعرفة:")
    stats = kb.get_statistics()
    print(f"  - إجمالي الحقائق: {stats['total_facts']}")
    print(f"  - إجمالي المحادثات: {stats['total_conversations']}")
    print(f"  - إجمالي المهارات: {stats['total_skills']}")
    
    kb.close()


def main():
    """تشغيل جميع الأمثلة"""
    print("\n")
    print("🤖" * 30)
    print("نظام الوكيل الذكي المتكامل - أمثلة الاستخدام")
    print("🤖" * 30)
    
    examples = [
        example_1_basic_chat,
        example_2_data_analysis,
        example_3_code_generation,
        example_4_planning,
        example_5_language_processing,
        example_6_multi_agent_system,
        example_7_knowledge_base
    ]
    
    for example in examples:
        try:
            example()
            print("\n✓ اكتمل المثال بنجاح!")
        except Exception as e:
            print(f"\n✗ خطأ في المثال: {e}")
        
        input("\n\nاضغط Enter للمتابعة إلى المثال التالي...")
    
    print("\n\n🎉 اكتملت جميع الأمثلة!")
    print("=" * 60)


if __name__ == "__main__":
    main()
