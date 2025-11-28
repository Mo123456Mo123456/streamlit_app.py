# 📦 دليل التثبيت المفصل

## المتطلبات الأساسية

### 1. Python

**الإصدار المطلوب:** Python 3.8 أو أحدث

#### التحقق من وجود Python

```bash
python --version
# أو
python3 --version
```

#### تثبيت Python

**Windows:**
1. قم بتنزيل Python من [python.org](https://www.python.org/downloads/)
2. شغل المثبت
3. تأكد من تحديد "Add Python to PATH"

**macOS:**
```bash
# باستخدام Homebrew
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Linux (Fedora):**
```bash
sudo dnf install python3 python3-pip
```

### 2. pip (مدير الحزم)

عادة يأتي pip مع Python. للتحقق:

```bash
pip --version
# أو
pip3 --version
```

إذا لم يكن مثبتاً:

```bash
# Linux/macOS
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

## طرق التثبيت

### الطريقة 1: التثبيت التلقائي (موصى به)

#### Linux / macOS

```bash
# 1. اذهب إلى مجلد المشروع
cd /workspace

# 2. امنح صلاحية التنفيذ
chmod +x start.sh

# 3. شغل السكريبت
./start.sh
```

السكريبت سيقوم بـ:
- ✅ التحقق من Python و pip
- ✅ تثبيت جميع المتطلبات
- ✅ إنشاء المجلدات المطلوبة
- ✅ تشغيل التطبيق

#### Windows

```batch
# شغل الملف مباشرة
start.bat
```

أو انقر مرتين على `start.bat`

### الطريقة 2: التثبيت اليدوي

#### الخطوة 1: تنزيل المشروع

```bash
# إذا كان المشروع على Git
git clone <repository-url>
cd ai-agent-system

# أو فك الضغط إذا كان ملف مضغوط
unzip ai-agent-system.zip
cd ai-agent-system
```

#### الخطوة 2: إنشاء بيئة افتراضية (اختياري لكن موصى به)

```bash
# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيل البيئة
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### الخطوة 3: تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

إذا واجهت مشاكل، جرب:

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

#### الخطوة 4: إنشاء المجلدات

```bash
mkdir -p data logs database
```

أو في Windows:
```batch
mkdir data
mkdir logs
mkdir database
```

#### الخطوة 5: تشغيل التطبيق

```bash
streamlit run ai_agent_app.py
```

## التثبيت المخصص

### تثبيت مكتبات إضافية (اختياري)

```bash
# لمعالجة اللغات الطبيعية المتقدمة
pip install nltk spacy

# لقدرات AI متقدمة
pip install openai anthropic

# لدعم قواعد بيانات أخرى
pip install psycopg2-binary pymongo

# للتطوير والاختبار
pip install pytest black flake8 mypy
```

### تثبيت للتطوير

```bash
# استنساخ المشروع
git clone <repository-url>
cd ai-agent-system

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate  # أو venv\Scripts\activate في Windows

# تثبيت في وضع التطوير
pip install -e .

# تثبيت أدوات التطوير
pip install -r requirements-dev.txt
```

## التحقق من التثبيت

### 1. اختبار الاستيراد

```bash
python3 -c "from ai_agent import MasterAgent; print('✓ التثبيت ناجح!')"
```

يجب أن ترى:
```
✓ التثبيت ناجح!
```

### 2. تشغيل الاختبارات

```bash
python tests/test_agent.py
```

يجب أن تمر جميع الاختبارات بنجاح.

### 3. تشغيل مثال

```bash
python examples/basic_usage.py
```

يجب أن يعمل بدون أخطاء.

## حل المشاكل الشائعة

### المشكلة 1: خطأ "command not found: python"

**الحل:**
```bash
# جرب python3 بدلاً من python
python3 --version

# أو أنشئ alias
alias python=python3
```

### المشكلة 2: خطأ "Permission denied"

**الحل:**
```bash
# امنح صلاحيات التنفيذ
chmod +x start.sh

# أو شغل بـ bash
bash start.sh
```

### المشكلة 3: خطأ في تثبيت المكتبات

**الحل 1:** حدّث pip
```bash
pip install --upgrade pip setuptools wheel
```

**الحل 2:** ثبت بدون cache
```bash
pip install -r requirements.txt --no-cache-dir
```

**الحل 3:** ثبت كل مكتبة على حدة
```bash
pip install streamlit
pip install pandas
pip install plotly
# ... إلخ
```

### المشكلة 4: خطأ "ModuleNotFoundError"

**الحل:**
```bash
# تأكد من أنك في المجلد الصحيح
cd /workspace

# أعد تثبيت المتطلبات
pip install -r requirements.txt --force-reinstall
```

### المشكلة 5: Streamlit لا يفتح تلقائياً

**الحل:**
افتح المتصفح يدوياً واذهب إلى:
```
http://localhost:8501
```

أو غيّر المنفذ:
```bash
streamlit run ai_agent_app.py --server.port 8502
```

### المشكلة 6: خطأ في قاعدة البيانات

**الحل:**
```bash
# احذف قاعدة البيانات القديمة
rm ai_agent_knowledge.db
rm -rf database/

# أعد إنشاء المجلدات
mkdir -p database logs data
```

## التثبيت على أنظمة مختلفة

### Docker (اختياري)

إذا كنت تفضل Docker:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ai_agent_app.py"]
```

تشغيل:
```bash
docker build -t ai-agent .
docker run -p 8501:8501 ai-agent
```

### Conda (اختياري)

إذا كنت تستخدم Anaconda:

```bash
# إنشاء بيئة جديدة
conda create -n aiagent python=3.9

# تفعيل البيئة
conda activate aiagent

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل التطبيق
streamlit run ai_agent_app.py
```

## الإعدادات المتقدمة

### تخصيص المنفذ

```bash
streamlit run ai_agent_app.py --server.port 8080
```

### تفعيل HTTPS

```bash
streamlit run ai_agent_app.py \
  --server.port 443 \
  --server.sslCertFile cert.pem \
  --server.sslKeyFile key.pem
```

### الوصول من الشبكة المحلية

```bash
streamlit run ai_agent_app.py --server.address 0.0.0.0
```

ثم افتح من جهاز آخر:
```
http://[YOUR-IP]:8501
```

### تشغيل في الخلفية

```bash
# Linux/macOS
nohup streamlit run ai_agent_app.py &

# أو باستخدام screen
screen -S aiagent
streamlit run ai_agent_app.py
# اضغط Ctrl+A ثم D للخروج
```

## المتطلبات الكاملة

### المكتبات الأساسية

```
streamlit>=1.28.0          # واجهة المستخدم
pandas>=2.1.0              # معالجة البيانات
plotly>=5.17.0             # الرسوم البيانية
numpy>=1.24.0              # العمليات الرياضية
python-dateutil>=2.8.2     # معالجة التواريخ
```

### المكتبات الاختيارية

```
requests>=2.31.0           # طلبات HTTP
openai>=1.0.0              # تكامل مع OpenAI
anthropic>=0.5.0           # تكامل مع Claude
nltk>=3.8                  # معالجة اللغات
spacy>=3.6.0               # NLP متقدم
```

## التحديثات

### تحديث النظام

```bash
# سحب آخر التحديثات
git pull

# تحديث المتطلبات
pip install -r requirements.txt --upgrade

# إعادة التشغيل
streamlit run ai_agent_app.py
```

### التحقق من الإصدار

```python
import ai_agent
print(ai_agent.__version__)
```

## الإزالة

### إزالة البيئة الافتراضية

```bash
# إلغاء التفعيل
deactivate

# حذف المجلد
rm -rf venv/
```

### إزالة المكتبات

```bash
pip uninstall -r requirements.txt -y
```

### حذف المشروع

```bash
rm -rf /workspace
```

## الدعم الفني

إذا واجهت أي مشكلة:

1. تحقق من [QUICK_START.md](QUICK_START.md)
2. اطلع على [README.md](README.md)
3. جرب الأمثلة في `examples/`
4. افتح Issue على GitHub

---

**تم التحديث:** Nov 28, 2025  
**الإصدار:** 1.0.0
