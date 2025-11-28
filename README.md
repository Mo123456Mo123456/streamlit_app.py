# 🤖 نظام الوكيل الذكي المتكامل
### Complete AI Agent System | نظام ذكاء اصطناعي متعدد الوكلاء

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

نظام ذكاء اصطناعي متكامل مع وكلاء متخصصين، قاعدة معرفة ذكية، وواجهة تفاعلية جميلة

[البدء السريع](#-البدء-السريع) •
[المميزات](#-المميزات) •
[الوثائق](#-الوثائق) •
[الأمثلة](#-الأمثلة)

</div>

---

## 📖 نظرة عامة

نظام الوكيل الذكي هو منصة متكاملة للذكاء الاصطناعي تتضمن:

- 🤝 **نظام متعدد الوكلاء**: 6 وكلاء متخصصين يعملون معاً
- 🧠 **ذاكرة ذكية**: نظام ذاكرة قصيرة وطويلة المدى
- 💬 **محادثة تفاعلية**: واجهة دردشة سلسة وسهلة
- 📊 **تحليل متقدم**: قدرات تحليل بيانات احترافية
- 💻 **توليد أكواد**: كتابة ومراجعة الأكواد البرمجية
- 📋 **تخطيط ذكي**: وضع خطط وإدارة مشاريع

## ✨ المميزات

### 🎯 الوكلاء المتخصصون

| الوكيل | الدور | القدرات |
|--------|------|----------|
| 👑 **Master Agent** | الوكيل الرئيسي | إدارة وتنسيق جميع الوكلاء |
| 🔍 **Research Agent** | الباحث | البحث وجمع المعلومات والتلخيص |
| 📊 **Data Analyst** | محلل البيانات | تحليل البيانات وتوليد الرؤى |
| 💻 **Coder Agent** | المبرمج | كتابة ومراجعة الأكواد |
| 📋 **Planner Agent** | المخطط | وضع الخطط وإدارة المشاريع |
| 🌐 **Language Agent** | معالج اللغات | الترجمة وتحليل المشاعر |

### 🧠 نظام الذاكرة الذكي

- ✅ ذاكرة قصيرة المدى للسياق الحالي
- ✅ ذاكرة طويلة المدى للمعلومات المهمة
- ✅ قاعدة معرفة متكاملة مع SQLite
- ✅ إدارة السياق التلقائية

### 💬 واجهة المستخدم

- ✅ تصميم عصري وجميل
- ✅ واجهة عربية كاملة
- ✅ دردشة في الوقت الفعلي
- ✅ لوحة تحكم شاملة
- ✅ إحصائيات تفاعلية

## 🚀 البدء السريع

### التثبيت والتشغيل (3 خطوات)

#### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```

#### Windows
```batch
start.bat
```

#### يدوياً
```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. تشغيل التطبيق
streamlit run ai_agent_app.py
```

🎉 التطبيق سيفتح تلقائياً على: `http://localhost:8501`

## 🎯 أمثلة الاستخدام

### محادثة بسيطة

```python
from ai_agent import MasterAgent

master = MasterAgent("المساعد")
response = master.chat("مرحبا، كيف حالك؟")
print(response)
```

### تحليل بيانات

```python
from ai_agent import DataAnalystAgent

analyst = DataAnalystAgent()
data = [10, 20, 30, 40, 50]
analysis = analyst.analyze_data(data)
print(analysis)
```

### كتابة كود

```python
from ai_agent import CoderAgent

coder = CoderAgent()
code = coder.generate_code("دالة لحساب الأعداد الأولية")
print(code)
```

### نظام متكامل

```python
from ai_agent import MasterAgent, ResearchAgent, DataAnalystAgent

master = MasterAgent()
master.add_sub_agent(ResearchAgent())
master.add_sub_agent(DataAnalystAgent())

result = master.coordinate("حلل البيانات: [1, 5, 10, 15, 20]")
print(result)
```

## 📁 هيكل المشروع

```
workspace/
├── ai_agent/                  # النظام الأساسي
│   ├── core/                  # المكونات الأساسية
│   │   ├── agent.py          # نظام الوكيل
│   │   └── knowledge_base.py # قاعدة المعرفة
│   ├── agents/                # الوكلاء المتخصصون
│   │   └── specialized_agents.py
│   └── utils/                 # أدوات مساعدة
│       └── helpers.py
├── examples/                  # أمثلة الاستخدام
│   ├── basic_usage.py        # أمثلة أساسية
│   └── advanced_usage.py     # أمثلة متقدمة
├── tests/                     # الاختبارات
│   └── test_agent.py         # اختبارات النظام
├── ai_agent_app.py           # التطبيق الرئيسي
├── config.py                  # الإعدادات
├── requirements.txt           # المتطلبات
├── start.sh                   # نص التشغيل (Linux/Mac)
├── start.bat                  # نص التشغيل (Windows)
├── README.md                  # هذا الملف
├── README_AI_AGENT.md        # وثائق تفصيلية
└── QUICK_START.md            # دليل البدء السريع
```

## 📊 لقطات شاشة

### صفحة المحادثة
واجهة دردشة تفاعلية مع الوكيل الذكي، مع أوامر سريعة وسجل كامل للمحادثات.

### لوحة الوكلاء
عرض شامل لجميع الوكلاء المتاحة، قدراتهم، وإحصائيات أدائهم.

### الإحصائيات
رسوم بيانية تفاعلية لتحليل الأداء واستخدام النظام.

## 🧪 تشغيل الأمثلة

### الأمثلة الأساسية
```bash
python examples/basic_usage.py
```

### الأمثلة المتقدمة
```bash
python examples/advanced_usage.py
```

## 🧪 تشغيل الاختبارات

```bash
# باستخدام unittest
python tests/test_agent.py

# باستخدام pytest (إذا كان مثبتاً)
pytest tests/
```

## 📚 الوثائق

- 📖 [الوثائق الكاملة](README_AI_AGENT.md) - دليل شامل ومفصل
- 🚀 [البدء السريع](QUICK_START.md) - ابدأ في 5 دقائق
- 💡 [الأمثلة](examples/) - أمثلة عملية

## 🛠️ التخصيص

### إضافة وكيل مخصص

```python
from ai_agent.core.agent import AIAgent, AgentRole

class MyCustomAgent(AIAgent):
    def __init__(self):
        super().__init__(
            name="وكيلي المخصص",
            role=AgentRole.ASSISTANT,
            capabilities=["custom_capability"]
        )
    
    def custom_method(self, data):
        # أضف الكود الخاص بك هنا
        return "نتيجة مخصصة"
```

### تعديل الإعدادات

عدّل ملف `config.py`:

```python
# زيادة حجم الذاكرة
MAX_MEMORY_SIZE = 5000

# تفعيل وضع التطوير
DEBUG = True
```

## 🔐 الأمان والخصوصية

- ✅ جميع البيانات تُخزن محلياً
- ✅ لا توجد اتصالات خارجية (إلا إذا أضفتها)
- ✅ قاعدة بيانات SQLite آمنة
- ✅ لا يتم جمع أي بيانات شخصية

## 🤝 المساهمة

نرحب بالمساهمات! خطوات المساهمة:

1. Fork المشروع
2. أنشئ فرع للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

## 📝 المتطلبات

- Python 3.8 أو أحدث
- المكتبات في `requirements.txt`

### المكتبات الأساسية

- `streamlit` - واجهة المستخدم
- `pandas` - معالجة البيانات
- `plotly` - الرسوم البيانية
- `sqlite3` - قاعدة البيانات

## 🎯 خارطة الطريق

- [ ] دعم OpenAI API و GPT
- [ ] إضافة المزيد من الوكلاء المتخصصين
- [ ] دعم متعدد اللغات الكامل
- [ ] واجهة REST API
- [ ] تطبيق موبايل (iOS/Android)
- [ ] تكامل مع أدوات خارجية
- [ ] نماذج NLP محلية

## 🐛 حل المشاكل

### المشكلة: لا يعمل streamlit
```bash
pip install --upgrade streamlit
```

### المشكلة: خطأ في الاستيراد
```bash
pip install -r requirements.txt --force-reinstall
```

### المشكلة: خطأ في قاعدة البيانات
```bash
rm ai_agent_knowledge.db
rm -rf database/
```

## 📞 الدعم

- 📧 Email: support@aiagent.example.com
- 💬 Discord: [انضم للمجتمع](#)
- 📖 Wiki: [الوثائق الكاملة](README_AI_AGENT.md)

## 📜 الترخيص

هذا المشروع مرخص تحت رخصة MIT. انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

شكراً لجميع المساهمين والمستخدمين!

بُني باستخدام:
- [Streamlit](https://streamlit.io/) - واجهة المستخدم
- [Plotly](https://plotly.com/) - الرسوم البيانية
- [Pandas](https://pandas.pydata.org/) - معالجة البيانات
- [SQLite](https://www.sqlite.org/) - قاعدة البيانات

## ⭐ أعطنا نجمة!

إذا أعجبك المشروع، لا تنسَ أن تعطيه نجمة ⭐ على GitHub!

---

<div align="center">

**صُنع بـ ❤️ باستخدام Python و Streamlit**

[الموقع الرسمي](#) • [التوثيق](#) • [المجتمع](#)

© 2025 نظام الوكيل الذكي المتكامل - جميع الحقوق محفوظة

</div>
