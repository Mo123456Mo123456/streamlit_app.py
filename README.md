# 🤖 وكيل الذكاء الاصطناعي المتكامل | AI Agent System

نظام وكيل ذكاء اصطناعي متكامل ومتقدم يوفر واجهة محادثة ذكية مع قدرات متعددة لتحليل البيانات، معالجة النصوص، إنشاء الكود، والحسابات الرياضية.

A comprehensive and advanced AI agent system that provides an intelligent conversational interface with multiple capabilities for data analysis, text processing, code generation, and mathematical calculations.

## ✨ المميزات | Features

### 🧠 القدرات الرئيسية | Core Capabilities

- **💬 محادثة ذكية** | **Intelligent Conversation**
  - واجهة محادثة تفاعلية بالعربية والإنجليزية
  - ذاكرة محادثات متقدمة
  - حفظ واسترجاع المحادثات

- **📊 تحليل البيانات** | **Data Analysis**
  - رفع ومعالجة ملفات CSV و Excel
  - تحليل إحصائي شامل
  - عرض البيانات والرسوم البيانية

- **📝 معالجة النصوص** | **Text Processing**
  - تحليل النصوص (الطول، عدد الكلمات، اللغة)
  - اكتشاف البريد الإلكتروني والروابط
  - دعم العربية والإنجليزية

- **💻 إنشاء الكود** | **Code Generation**
  - إنشاء كود برمجي بناءً على المهام
  - دعم Python و JavaScript
  - قوالب جاهزة للاستخدام

- **🧮 الحسابات الرياضية** | **Mathematical Calculations**
  - تقييم التعبيرات الرياضية
  - دعم العمليات الحسابية المعقدة

## 🚀 التثبيت والتشغيل | Installation & Running

### المتطلبات | Requirements

```bash
pip install -r requirements.txt
```

### تشغيل التطبيق | Run the Application

```bash
streamlit run ai_agent.py
```

أو | Or:

```bash
streamlit run streamlit_app.py
```

## 📖 دليل الاستخدام | User Guide

### 1. تحليل النص | Text Analysis

اكتب في المحادثة:
```
حلل هذا النص: [النص الذي تريد تحليله]
```

أو | Or:
```
analyze this text: [text to analyze]
```

### 2. تحليل البيانات | Data Analysis

1. ارفع ملف CSV أو Excel من الشريط الجانبي
2. اكتب في المحادثة: "حلل البيانات" أو "analyze data"

### 3. إنشاء الكود | Code Generation

اكتب في المحادثة:
```
أنشئ كود لتحليل البيانات
```

أو | Or:
```
generate code for data analysis
```

### 4. الحسابات الرياضية | Mathematical Calculations

اكتب في المحادثة:
```
احسب 25 * 4 + 10
```

أو | Or:
```
calculate 25 * 4 + 10
```

## 🛠️ البنية التقنية | Technical Architecture

### المكونات الرئيسية | Main Components

1. **ConversationMemory**: إدارة ذاكرة المحادثات
2. **AgentTools**: مجموعة أدوات الوكيل
3. **AIAgent**: المحرك الرئيسي للوكيل
4. **UI Components**: واجهة المستخدم التفاعلية

### الملفات | Files

- `ai_agent.py`: الملف الرئيسي للتطبيق
- `streamlit_app.py`: تطبيق Streamlit الأصلي (GDP Dashboard)
- `requirements.txt`: المكتبات المطلوبة
- `saved_conversations/`: مجلد المحادثات المحفوظة

## 📁 هيكل المشروع | Project Structure

```
/workspace/
├── ai_agent.py              # التطبيق الرئيسي للوكيل
├── streamlit_app.py         # تطبيق GDP Dashboard الأصلي
├── requirements.txt         # المكتبات المطلوبة
├── README.md               # هذا الملف
├── data/                   # بيانات GDP
│   └── gdp_data.csv
└── saved_conversations/     # المحادثات المحفوظة (يتم إنشاؤها تلقائياً)
```

## 🎯 أمثلة الاستخدام | Usage Examples

### مثال 1: تحليل نص | Example 1: Text Analysis

**المدخل | Input:**
```
حلل هذا النص: مرحبا بك في نظام الذكاء الاصطناعي المتكامل
```

**المخرجات | Output:**
- الطول: عدد الأحرف
- عدد الكلمات
- اللغة المكتشفة
- معلومات إضافية

### مثال 2: تحليل بيانات | Example 2: Data Analysis

**الخطوات | Steps:**
1. ارفع ملف CSV من الشريط الجانبي
2. اكتب: "حلل البيانات"
3. احصل على تحليل شامل للبيانات

### مثال 3: إنشاء كود | Example 3: Code Generation

**المدخل | Input:**
```
أنشئ كود لتحليل البيانات باستخدام pandas
```

**المخرجات | Output:**
كود Python جاهز للاستخدام

## 🔧 التخصيص | Customization

يمكنك تخصيص الوكيل من خلال:

1. **إضافة أدوات جديدة** في فئة `AgentTools`
2. **تحسين منطق الردود** في دالة `process_query`
3. **تخصيص الواجهة** من خلال CSS في `main()`

## 📝 الملاحظات | Notes

- المحادثات يتم حفظها تلقائياً في مجلد `saved_conversations/`
- يمكنك مسح المحادثة الحالية من الشريط الجانبي
- النظام يدعم العربية والإنجليزية بشكل كامل

## 🤝 المساهمة | Contributing

نرحب بمساهماتك! يمكنك:
- إضافة ميزات جديدة
- تحسين الواجهة
- إصلاح الأخطاء
- تحسين الأداء

## 📄 الترخيص | License

انظر ملف `LICENSE` للتفاصيل.

## 📧 الدعم | Support

للمساعدة أو الاستفسارات، يرجى فتح issue في المستودع.

---

**تم التطوير بـ ❤️ | Developed with ❤️**
