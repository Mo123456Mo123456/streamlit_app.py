#!/bin/bash
# Silver / سيلفر — startup script

echo "💠 Silver / سيلفر"
echo "================================"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. Python 3.10+ مطلوب."
    exit 1
fi

echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt || exit 1

echo "🧪 تشغيل اختبارات القبول..."
python3 -m unittest tests.test_silver_acceptance || exit 1

echo "🚀 تشغيل التطبيق..."
streamlit run streamlit_app.py
