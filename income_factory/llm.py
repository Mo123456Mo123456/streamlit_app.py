"""طبقة الاتصال بنموذج Claude — توليد متدفق مع معالجة أخطاء عربية واضحة."""

import anthropic

# النماذج المتاحة مع أسعارها (دولار لكل مليون توكن: إدخال / إخراج)
MODELS = {
    "claude-opus-4-8": "Opus 4.8 — الافتراضي، جودة عالية ($5 / $25)",
    "claude-sonnet-5": "Sonnet 5 — متوازن وسريع ($3 / $15)",
    "claude-haiku-4-5": "Haiku 4.5 — الأرخص للتجربة ($1 / $5)",
    "claude-fable-5": "Fable 5 — الأقوى على الإطلاق ($10 / $50)",
}
DEFAULT_MODEL = "claude-opus-4-8"


def stream_generate(api_key: str, model: str, system: str, prompt: str,
                    max_tokens: int = 32000):
    """مولّد نصي متدفق. يعيد أجزاء النص أولًا بأول ليعرضها Streamlit مباشرة.

    عند حدوث خطأ يُعاد نص عربي مفهوم بدل انهيار الواجهة.
    """
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
            yield "\n\n> ⚠️ رفض النموذج إكمال هذا الطلب لأسباب تتعلق بالسلامة. جرّب صياغة مختلفة أو نموذجًا آخر (مثل Opus 4.8)."
        elif final.stop_reason == "max_tokens":
            yield "\n\n> ⚠️ وصل الرد للحد الأقصى من الطول وقد يكون مقطوعًا."
    except anthropic.AuthenticationError:
        yield "❌ **مفتاح API غير صحيح.** تأكد من المفتاح في الشريط الجانبي (يبدأ بـ `sk-ant-`)."
    except anthropic.RateLimitError:
        yield "⏳ **تجاوزت حد الطلبات مؤقتًا.** انتظر دقيقة ثم أعد المحاولة."
    except anthropic.NotFoundError:
        yield f"❌ **النموذج `{model}` غير متاح لحسابك.** جرّب نموذجًا آخر من الشريط الجانبي."
    except anthropic.APIStatusError as e:
        yield f"❌ **خطأ من الخادم ({e.status_code}):** {e.message}"
    except anthropic.APIConnectionError:
        yield "❌ **تعذر الاتصال بالشبكة.** تحقق من اتصالك بالإنترنت وأعد المحاولة."
