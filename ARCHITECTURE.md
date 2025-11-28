# 🏗️ معمارية النظام

## نظرة عامة على البنية

```
┌─────────────────────────────────────────────────────────────┐
│                    واجهة المستخدم (Streamlit)                │
│                      ai_agent_app.py                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   الوكيل الرئيسي (Master Agent)              │
│                   إدارة وتنسيق الوكلاء                       │
│  - تحليل المهام                                              │
│  - تفويض المسؤوليات                                          │
│  - تنسيق النتائج                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────┐
        ▼               ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ وكيل البحث   │ │ محلل البيانات│ │   المبرمج    │ │   المخطط     │
│ Research     │ │ Data Analyst │ │   Coder      │ │  Planner     │
│              │ │              │ │              │ │              │
│ - بحث        │ │ - تحليل      │ │ - كتابة كود  │ │ - تخطيط      │
│ - تجميع      │ │ - إحصاء      │ │ - مراجعة     │ │ - جدولة      │
│ - تلخيص      │ │ - رؤى        │ │ - اختبار     │ │ - موارد      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │               │               │              │
        └───────────────┴───────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  نظام الذاكرة والمعرفة                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ذاكرة قصيرة  │  │ ذاكرة طويلة  │  │ قاعدة البيانات│      │
│  │ Short-term   │  │ Long-term    │  │   SQLite     │      │
│  │ Memory       │  │ Memory       │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## التدفق التفصيلي

### 1. دورة معالجة المهمة

```
┌──────────┐
│ المستخدم │
└────┬─────┘
     │ (1) إدخال نص
     ▼
┌─────────────────┐
│ واجهة Streamlit │
└────┬────────────┘
     │ (2) معالجة الإدخال
     ▼
┌──────────────────┐
│  Master Agent    │
│                  │
│ ┌──────────────┐ │
│ │   Perceive   │ │ (3) إدراك
│ └──────┬───────┘ │
│        ▼         │
│ ┌──────────────┐ │
│ │    Think     │ │ (4) تفكير
│ └──────┬───────┘ │
│        ▼         │
│ ┌──────────────┐ │
│ │    Decide    │ │ (5) قرار
│ └──────┬───────┘ │
└────────┼─────────┘
         │ (6) تفويض
         ▼
┌──────────────────┐
│ Specialized Agent│ (7) تنفيذ
└────────┬─────────┘
         │ (8) نتيجة
         ▼
┌──────────────────┐
│ Knowledge Base   │ (9) حفظ
└────────┬─────────┘
         │ (10) استجابة
         ▼
┌──────────────────┐
│      المستخدم     │
└──────────────────┘
```

## المكونات الرئيسية

### 1. طبقة الواجهة (UI Layer)

```
ai_agent_app.py
├── صفحة المحادثة (Chat)
├── صفحة الوكلاء (Agents)
├── صفحة الإحصائيات (Statistics)
├── صفحة قاعدة المعرفة (Knowledge Base)
└── صفحة الإعدادات (Settings)
```

**المسؤوليات:**
- عرض واجهة المستخدم
- استقبال المدخلات
- عرض النتائج
- إدارة الجلسة

### 2. طبقة المنطق (Business Logic Layer)

```
ai_agent/core/
├── agent.py
│   ├── AIAgent (الوكيل الأساسي)
│   │   ├── perceive()    # الإدراك
│   │   ├── think()       # التفكير
│   │   ├── act()         # التنفيذ
│   │   └── process()     # دورة كاملة
│   │
│   └── MasterAgent (الوكيل الرئيسي)
│       ├── delegate_task()   # تفويض
│       ├── coordinate()      # تنسيق
│       └── chat()            # محادثة
│
└── knowledge_base.py
    ├── KnowledgeBase         # قاعدة المعرفة
    │   ├── add_fact()
    │   ├── search_facts()
    │   └── get_statistics()
    │
    └── ConversationManager   # إدارة المحادثات
        ├── process_message()
        └── get_context()
```

### 3. طبقة الوكلاء المتخصصين

```
ai_agent/agents/
└── specialized_agents.py
    ├── ResearchAgent
    │   ├── search_web()
    │   └── summarize()
    │
    ├── DataAnalystAgent
    │   ├── analyze_data()
    │   └── generate_insights()
    │
    ├── CoderAgent
    │   ├── generate_code()
    │   └── review_code()
    │
    ├── PlannerAgent
    │   ├── create_plan()
    │   └── break_down_goal()
    │
    └── LanguageAgent
        ├── translate()
        ├── analyze_sentiment()
        └── extract_keywords()
```

### 4. طبقة البيانات (Data Layer)

```
Database (SQLite)
├── facts               # جدول الحقائق
│   ├── id
│   ├── category
│   ├── key
│   ├── value
│   └── confidence
│
├── conversations       # جدول المحادثات
│   ├── id
│   ├── user_message
│   ├── agent_response
│   └── timestamp
│
└── skills             # جدول المهارات
    ├── id
    ├── name
    ├── description
    └── usage_count
```

## أنماط التصميم المستخدمة

### 1. Agent Pattern (نمط الوكيل)

```python
class AIAgent:
    def perceive(self, input_data):
        """إدراك البيئة"""
        
    def think(self, perception):
        """معالجة المعلومات"""
        
    def act(self, decision):
        """تنفيذ القرار"""
        
    def process(self, input_data):
        """دورة كاملة"""
        perception = self.perceive(input_data)
        decision = self.think(perception)
        result = self.act(decision)
        return result
```

### 2. Strategy Pattern (نمط الاستراتيجية)

```python
# كل وكيل له استراتيجية خاصة
researcher = ResearchAgent()  # استراتيجية البحث
analyst = DataAnalystAgent()  # استراتيجية التحليل
coder = CoderAgent()          # استراتيجية البرمجة
```

### 3. Observer Pattern (نمط المراقب)

```python
# قاعدة المعرفة تراقب التغييرات
kb.add_fact(...)              # حدث
conversation_manager.observe() # مراقبة
```

### 4. Singleton Pattern (نمط الوحيد)

```python
# قاعدة البيانات تستخدم اتصال واحد
class KnowledgeBase:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## تدفق البيانات

### مثال: طلب تحليل بيانات

```
1. المستخدم → "حلل البيانات [1,2,3,4,5]"
                ↓
2. Streamlit → معالجة الإدخال
                ↓
3. MasterAgent → تصنيف المهمة (analysis)
                ↓
4. MasterAgent → اختيار DataAnalystAgent
                ↓
5. DataAnalystAgent → analyze_data([1,2,3,4,5])
                ↓
6. DataAnalystAgent → {mean: 3, min: 1, max: 5}
                ↓
7. KnowledgeBase → حفظ النتيجة
                ↓
8. Streamlit → عرض النتيجة
                ↓
9. المستخدم ← "المتوسط: 3، النطاق: 1-5"
```

## التوسعة والإضافات

### إضافة وكيل جديد

```python
# 1. إنشاء فئة الوكيل
class NewAgent(AIAgent):
    def __init__(self):
        super().__init__(
            name="وكيل جديد",
            role=AgentRole.ASSISTANT,
            capabilities=["new_capability"]
        )
    
    def special_action(self, data):
        # الكود الخاص
        pass

# 2. إضافته للنظام
master = MasterAgent()
master.add_sub_agent(NewAgent())
```

### إضافة قدرة جديدة

```python
# في أي وكيل
def new_capability(self, data):
    """قدرة جديدة"""
    # معالجة
    result = process(data)
    
    # حفظ في الذاكرة
    self.memory.add_to_short_term(result)
    
    return result
```

## الأمان والأداء

### مستويات الأمان

```
Layer 1: Input Validation
         ↓
Layer 2: Agent Authorization
         ↓
Layer 3: Data Sanitization
         ↓
Layer 4: Database Security
         ↓
Layer 5: Output Filtering
```

### تحسين الأداء

1. **Caching**: تخزين النتائج المتكررة
2. **Lazy Loading**: تحميل البيانات عند الحاجة
3. **Connection Pooling**: إعادة استخدام الاتصالات
4. **Async Processing**: معالجة غير متزامنة

## التبعيات

```
┌──────────────────┐
│   Streamlit      │ ← واجهة المستخدم
└────────┬─────────┘
         │
┌────────▼─────────┐
│   AI Agent Core  │ ← المنطق الأساسي
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Pandas │ │ SQLite │ ← البيانات
└────────┘ └────────┘
```

## الخلاصة

النظام مبني بشكل:
- ✅ **Modular**: كل مكون مستقل
- ✅ **Extensible**: سهل الإضافة والتوسع
- ✅ **Maintainable**: سهل الصيانة والتحديث
- ✅ **Scalable**: قابل للتوسع
- ✅ **Testable**: سهل الاختبار

---

**آخر تحديث:** Nov 28, 2025  
**الإصدار:** 1.0.0
