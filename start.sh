#!/bin/bash

# نص تشغيل نظام الوكيل الذكي
# AI Agent System Startup Script

echo "🤖 نظام الوكيل الذكي المتكامل"
echo "================================"
echo ""

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيت Python 3.8 أو أحدث."
    exit 1
fi

echo "✓ تم العثور على Python"

# التحقق من pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip غير مثبت."
    exit 1
fi

echo "✓ تم العثور على pip"

# تثبيت المتطلبات
echo ""
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ فشل تثبيت المتطلبات"
    exit 1
fi

echo "✓ تم تثبيت المتطلبات بنجاح"

# إنشاء المجلدات المطلوبة
echo ""
echo "📁 إنشاء المجلدات..."
mkdir -p data logs database

echo "✓ تم إنشاء المجلدات"

# تشغيل التطبيق
echo ""
echo "🚀 تشغيل التطبيق..."
echo "================================"
echo ""

streamlit run ai_agent_app.py

# في حالة الخروج
echo ""
echo "👋 شكراً لاستخدام نظام الوكيل الذكي!"
