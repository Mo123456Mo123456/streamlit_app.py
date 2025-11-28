# 🤖 وكيل الذكاء الاصطناعي المتكامل

<div align="center">

![AI Agent](https://img.shields.io/badge/AI-Agent-6366f1?style=for-the-badge&logo=robot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

**مساعدك الشخصي الذكي - متعدد القدرات والأدوات**

[🚀 تشغيل التطبيق](#-تشغيل-التطبيق) • [✨ المميزات](#-المميزات) • [🛠️ الأدوات](#️-الأدوات-المتاحة) • [📖 التوثيق](#-التوثيق)

</div>

---

## 📋 نظرة عامة

وكيل الذكاء الاصطناعي المتكامل هو مساعد شخصي ذكي يجمع بين قوة الذكاء الاصطناعي ومجموعة واسعة من الأدوات العملية. يتميز بواجهة مستخدم عربية أنيقة وعصرية، مع دعم كامل للغة العربية.

## ✨ المميزات

### 🎯 المميزات الرئيسية

- 💬 **محادثة ذكية** - تفاعل طبيعي باللغة العربية والإنجليزية
- 🛠️ **10+ أدوات متكاملة** - من الحسابات إلى البحث والترجمة
- 🎨 **واجهة عصرية** - تصميم أنيق وسهل الاستخدام
- 🔌 **دعم متعدد لمزودي AI** - OpenAI، Anthropic، أو الوضع المحلي
- 💾 **حفظ المحادثات** - احفظ واسترجع محادثاتك
- 📊 **إحصائيات مباشرة** - تتبع استخدامك للوكيل

### 🎨 التصميم

- 🌙 وضع داكن أنيق
- ✨ تأثيرات بصرية جذابة
- 📱 تصميم متجاوب
- 🎭 رسوم متحركة سلسة

## 🛠️ الأدوات المتاحة

| الأداة | الوصف | مثال |
|--------|--------|-------|
| 🧮 **الآلة الحاسبة** | حسابات رياضية متقدمة وحل المعادلات | `احسب 25 × 4 + 100` |
| 🌐 **البحث** | البحث على الإنترنت للحصول على معلومات حديثة | `ابحث عن الذكاء الاصطناعي` |
| 📚 **ويكيبيديا** | معلومات موثوقة من الموسوعة الحرة | `معلومات عن ألبرت أينشتاين` |
| 🌤️ **الطقس** | أحوال الجو لأي مدينة في العالم | `ما طقس الرياض؟` |
| 🕐 **الوقت والتاريخ** | الوقت الحالي وحسابات التاريخ | `كم الساعة الآن؟` |
| 💱 **العملات** | تحويل بين العملات المختلفة | `حوّل 100 دولار إلى ريال` |
| 🌍 **الترجمة** | ترجمة النصوص بين اللغات | `ترجم مرحبا إلى الإنجليزية` |
| 📝 **تحليل النص** | إحصائيات وتحليل النصوص | `حلل هذا النص` |
| 🔐 **التشفير** | تشفير وفك تشفير Base64 و Hash | `شفّر كلمة سر` |
| 📊 **الرسوم البيانية** | إنشاء رسوم بيانية من البيانات | `ارسم بيانات المبيعات` |

## 🚀 تشغيل التطبيق

### المتطلبات

- Python 3.8 أو أحدث
- pip (مدير حزم Python)

### التثبيت

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd workspace
```

2. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

3. **تشغيل التطبيق**
```bash
streamlit run streamlit_app.py
```

4. **افتح المتصفح** على العنوان:
```
http://localhost:8501
```

### إعداد مفاتيح API (اختياري)

للحصول على قدرات AI متقدمة، يمكنك إضافة مفتاح API:

#### OpenAI
1. احصل على مفتاح من [OpenAI](https://platform.openai.com/api-keys)
2. أدخله في الشريط الجانبي للتطبيق

#### Anthropic (Claude)
1. احصل على مفتاح من [Anthropic](https://console.anthropic.com/)
2. اختر "anthropic" كمزود واكتب المفتاح

## 📁 هيكل المشروع

```
workspace/
├── 📄 streamlit_app.py      # الواجهة الرئيسية
├── 📁 ai_agent/
│   ├── 🔧 __init__.py       # تهيئة الوحدة
│   ├── 🧠 agent_core.py     # نواة الوكيل
│   └── 🛠️ tools.py          # الأدوات المتاحة
├── 📋 requirements.txt       # المتطلبات
└── 📖 README.md             # هذا الملف
```

## 📖 التوثيق

### استخدام الوكيل برمجياً

```python
from ai_agent import AIAgent

# إنشاء وكيل جديد
agent = AIAgent()

# محادثة بسيطة
response = agent.chat("مرحبا، كيف حالك؟")
print(response)

# مع API خارجي
agent = AIAgent(api_key="your-key", provider="openai")
response = agent.chat("اشرح لي الذكاء الاصطناعي")
```

### استخدام الأدوات مباشرة

```python
from ai_agent.tools import ToolManager

tools = ToolManager()

# حساب رياضي
result = tools.execute_tool('calculator', 'calculate', expression='25 * 4')
print(result)  # {'success': True, 'result': 100, ...}

# الطقس
weather = tools.execute_tool('weather', 'get_weather', city='Riyadh')
print(weather)

# الترجمة
translation = tools.execute_tool('translator', 'translate', 
                                  text='مرحبا', to_lang='en')
print(translation)
```

## 🤝 المساهمة

نرحب بمساهماتكم! يمكنكم:

1. 🍴 Fork المشروع
2. 🌿 إنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. 💾 Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. 📤 Push للفرع (`git push origin feature/amazing-feature`)
5. 🔃 فتح Pull Request

## 📜 الرخصة

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

- [Streamlit](https://streamlit.io/) - لإطار العمل الرائع
- [OpenAI](https://openai.com/) - لنماذج الذكاء الاصطناعي
- [Anthropic](https://anthropic.com/) - لنموذج Claude

---

<div align="center">

**صُنع بـ ❤️ باستخدام Python و Streamlit**

⭐ لا تنسَ إعطاء نجمة للمشروع إذا أعجبك! ⭐

</div>
