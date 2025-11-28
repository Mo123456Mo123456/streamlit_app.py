@echo off
REM نص تشغيل نظام الوكيل الذكي لـ Windows
REM AI Agent System Startup Script for Windows

echo 🤖 نظام الوكيل الذكي المتكامل
echo ================================
echo.

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت. يرجى تثبيت Python 3.8 أو أحدث.
    pause
    exit /b 1
)

echo ✓ تم العثور على Python

REM التحقق من pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip غير مثبت.
    pause
    exit /b 1
)

echo ✓ تم العثور على pip

REM تثبيت المتطلبات
echo.
echo 📦 تثبيت المتطلبات...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ فشل تثبيت المتطلبات
    pause
    exit /b 1
)

echo ✓ تم تثبيت المتطلبات بنجاح

REM إنشاء المجلدات المطلوبة
echo.
echo 📁 إنشاء المجلدات...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "database" mkdir database

echo ✓ تم إنشاء المجلدات

REM تشغيل التطبيق
echo.
echo 🚀 تشغيل التطبيق...
echo ================================
echo.

streamlit run ai_agent_app.py

REM في حالة الخروج
echo.
echo 👋 شكراً لاستخدام نظام الوكيل الذكي!
pause
