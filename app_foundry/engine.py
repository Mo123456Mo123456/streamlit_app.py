"""محرك الورشة: يحوّل وصف العميل إلى تطبيق ويب كامل في ملف HTML واحد."""

import re

import anthropic

MODELS = {
    "claude-opus-4-8": "Opus 4.8 — الافتراضي، كود ممتاز ($5 / $25)",
    "claude-fable-5": "Fable 5 — الأقوى للتطبيقات المعقدة ($10 / $50)",
    "claude-sonnet-5": "Sonnet 5 — سريع ومتوازن ($3 / $15)",
    "claude-haiku-4-5": "Haiku 4.5 — للتجارب الرخيصة ($1 / $5)",
}
DEFAULT_MODEL = "claude-opus-4-8"

SYSTEM_BUILDER = """أنت مهندس واجهات أمامية خبير عالمي المستوى، متخصص في بناء تطبيقات ويب كاملة داخل ملف HTML واحد.

قواعد صارمة لا تُكسر أبدًا:
1. أخرج ملف HTML واحدًا كاملًا فقط داخل كتلة كود واحدة ```html ... ``` — لا شرح قبلها ولا بعدها.
2. الملف مكتفٍ ذاتيًا 100%: كل CSS و JavaScript مضمّن داخله. ممنوع أي روابط خارجية (CDN، خطوط جوجل، مكتبات، صور خارجية) — يجب أن يعمل الملف بدون إنترنت إطلاقًا.
3. الأيقونات والرسومات: استخدم SVG مضمّنًا أو رموز Emoji.
4. حفظ البيانات (إن لزم): localStorage فقط.
5. التصميم: عصري وفاخر، متجاوب للجوال أولًا (mobile-first)، مع دعم كامل للعربية RTL عند طلبها.
   تجنب مظهر القوالب الرخيصة: لا خلفيات بنفسجية متدرجة مبتذلة؛ استخدم لوحة ألوان متناسقة مستوحاة من هوية العميل، وظلالًا ناعمة، وحركات micro-interactions خفيفة.
6. الكود نظيف ومنظم مع تعليقات عربية قصيرة عند الأجزاء المهمة، وسهل التعديل (الألوان والنصوص في متغيرات CSS في الأعلى).
7. أضف في أعلى الملف تعليق HTML فيه اسم التطبيق وسطر "للتعديل: غيّر المتغيرات في :root".
8. إن كان التطبيق يعرض أسعارًا أو حسابات فاجعل المعادلات دقيقة وواضحة في الكود."""

SYSTEM_SALES = """أنت مستقل محترف حاصل على أعلى التقييمات في بيع خدمات البرمجة على منصات مستقل وخمسات.
تكتب عروضًا مقنعة ومختصرة تجعل صاحب المشروع يشعر أنك فهمت طلبه تمامًا. أخرج Markdown نظيفًا فقط."""

BUILD_PROMPT = """اسم التطبيق/العميل: {title}
نوع التطبيق: {kind}
لغة الواجهة: {language}
هوية بصرية مطلوبة: {brand}

وصف الطلب بالتفصيل:
{brief}

ابنِ التطبيق كاملًا الآن حسب القواعد."""

REFINE_PROMPT = """هذا الكود الحالي للتطبيق:

```html
{code}
```

طلب التعديل من العميل:
{change}

أعد إخراج الملف كاملًا بعد تطبيق التعديل، بنفس القواعد الصارمة (ملف واحد، كتلة ```html واحدة، لا روابط خارجية)."""

PROPOSAL_PROMPT = """هذا نص مشروع منشور على منصة عمل حر (مستقل/خمسات):

---
{project_text}
---

أنا أسلّم تطبيقات ويب مخصصة كملف واحد يعمل على أي جهاز بدون استضافة ولا اشتراكات، وأسلّم خلال 24 ساعة مع تعديلات مجانية.

اكتب لي:
1. **عرضًا للتقديم على المشروع** (120-180 كلمة): يفتتح بفهم دقيق لطلبه، ثم كيف سأنفذه وما يميز التسليم (ملف واحد، بدون استضافة، تسليم سريع، تعديلات)، بدون مبالغة وبدون ذكر الذكاء الاصطناعي.
2. **3 أسئلة ذكية** أطرحها عليه تُظهر احترافيتي.
3. **سعرًا مقترحًا** بالدولار مع مبرر سطر واحد (واذكر نطاق سعر معقول لهذا النوع في المنصات العربية).
"""

_HTML_BLOCK = re.compile(r"```html\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_html(text: str) -> str:
    """يستخرج كود HTML من رد النموذج. يقبل كتلة ```html أو ملفًا خامًا يبدأ بـ <!DOCTYPE."""
    m = _HTML_BLOCK.search(text)
    if m:
        return m.group(1).strip()
    stripped = text.strip()
    if stripped.lower().startswith("<!doctype") or stripped.lower().startswith("<html"):
        return stripped
    return ""


def validate_html(code: str) -> list:
    """فحوصات سريعة قبل التسليم — تعيد قائمة تحذيرات (فارغة = سليم)."""
    warnings = []
    low = code.lower()
    if "<!doctype" not in low:
        warnings.append("الملف لا يبدأ بـ <!DOCTYPE html>")
    for pattern, label in [
        ('src="http', "يحتوي على مورد خارجي (src)"),
        ("src='http", "يحتوي على مورد خارجي (src)"),
        ('href="http', "يحتوي على رابط ملف خارجي (href)"),
        ("@import url(http", "يحتوي على استيراد CSS خارجي"),
        ("fonts.googleapis", "يستخدم خطوط جوجل الخارجية"),
        ("cdn.", "يستخدم CDN خارجي"),
    ]:
        if pattern in low and label not in warnings:
            warnings.append(label + " — قد لا يعمل بدون إنترنت")
    return warnings


def stream_call(api_key: str, model: str, system: str, prompt: str,
                max_tokens: int = 64000):
    """مولّد متدفق مع رسائل أخطاء عربية — يُستهلك عبر st.write_stream."""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
            final = stream.get_final_message()
        if final.stop_reason == "refusal":
            yield "\n\n> ⚠️ رفض النموذج هذا الطلب. جرّب صياغة مختلفة أو نموذج Opus 4.8."
        elif final.stop_reason == "max_tokens":
            yield "\n\n> ⚠️ الرد وصل للحد الأقصى وقد يكون الكود مقطوعًا — اطلب «أكمل الملف» في خانة التعديل."
    except anthropic.AuthenticationError:
        yield "❌ **مفتاح API غير صحيح.** تأكد من المفتاح في الشريط الجانبي."
    except anthropic.RateLimitError:
        yield "⏳ **تجاوزت حد الطلبات مؤقتًا.** انتظر دقيقة وأعد المحاولة."
    except anthropic.NotFoundError:
        yield f"❌ **النموذج `{model}` غير متاح لحسابك.** اختر نموذجًا آخر."
    except anthropic.APIStatusError as e:
        yield f"❌ **خطأ من الخادم ({e.status_code}):** {e.message}"
    except anthropic.APIConnectionError:
        yield "❌ **تعذر الاتصال بالشبكة.** أعد المحاولة."
