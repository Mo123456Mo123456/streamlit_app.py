"""تصدير المحتوى المولّد: ملفات HTML أنيقة (RTL) وملفات Markdown وحزم ZIP جاهزة للبيع."""

import io
import zipfile

import markdown as md

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{
    font-family: "Segoe UI", Tahoma, "Noto Kufi Arabic", Arial, sans-serif;
    background: #f7f5f0; color: #1f2430; margin: 0; padding: 0;
    line-height: 1.9;
  }}
  .page {{
    max-width: 820px; margin: 40px auto; background: #ffffff;
    padding: 56px 64px; border-radius: 14px;
    box-shadow: 0 6px 30px rgba(0,0,0,.08);
  }}
  h1 {{ color: #0f3d5c; border-bottom: 3px solid #d9a441; padding-bottom: 12px; }}
  h2 {{ color: #14507a; margin-top: 2em; }}
  h3 {{ color: #1a628f; }}
  code, pre {{
    background: #f0f3f7; border-radius: 8px; direction: ltr; text-align: left;
    font-family: "Cascadia Code", Consolas, monospace; font-size: .92em;
  }}
  pre {{ padding: 16px; overflow-x: auto; white-space: pre-wrap; }}
  code {{ padding: 2px 6px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #d8dde5; padding: 10px 12px; }}
  th {{ background: #0f3d5c; color: #fff; }}
  tr:nth-child(even) {{ background: #f7f9fc; }}
  blockquote {{ border-inline-start: 4px solid #d9a441; margin: 1em 0; padding: 4px 18px; background: #fdf9f0; }}
  .footer {{ text-align: center; color: #9aa3b2; font-size: .85em; margin: 24px 0; }}
  @media print {{ .page {{ box-shadow: none; margin: 0; }} }}
</style>
</head>
<body>
  <div class="page">{body}</div>
  <div class="footer">{title}</div>
</body>
</html>
"""


def markdown_to_html(title: str, md_text: str, arabic: bool = True) -> str:
    """يحوّل Markdown إلى صفحة HTML أنيقة جاهزة للبيع أو للطباعة كـ PDF."""
    body = md.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    return _HTML_TEMPLATE.format(
        title=title,
        body=body,
        lang="ar" if arabic else "en",
        direction="rtl" if arabic else "ltr",
    )


def build_zip(files: dict) -> bytes:
    """يبني حزمة ZIP من {اسم الملف: المحتوى النصي} جاهزة للرفع على منصات البيع."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()
