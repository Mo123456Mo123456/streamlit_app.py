#!/bin/bash
# سكريبت تشغيل التطبيق

echo "🚀 بدء تشغيل نظام التداول الذكي..."
echo "📦 تثبيت المكتبات المطلوبة..."

pip install -r requirements.txt --quiet

echo "✅ تم التثبيت بنجاح!"
echo "🌐 بدء تشغيل التطبيق على http://localhost:8501"
echo ""

streamlit run streamlit_app.py
