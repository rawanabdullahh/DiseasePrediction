DISEASE PREDICTION SYSTEM - SETUP GUIDE

DOWNLOAD:

Download this entire folder to your PC

Recommended location: C:\DiseasePrediction

INSTALL PYTHON:

Download Python 3.12+ from python.org

During install, CHECK "Add Python to PATH"

RUN THE APP:

Double-click RUN.bat (or follow manual steps below)

MANUAL STEPS (if RUN.bat fails):

Open Command Prompt in this folder:

Press Win+R, type "cmd", then:
cd /d "C:\path\to\DiseasePrediction"

Setup virtual environment:
python -m venv venv
.\venv\Scripts\activate

Install requirements:
pip install -r requirements.txt

Launch the app:
python app.py

Access in browser:
http://localhost:5000


نظام التنبؤ بالأمراض - دليل الإعداد

التحميل:

حمل هذا المجلد كاملًا إلى جهازك

المكان الموصى به: C:\DiseasePrediction

تثبيت بايثون:

حمل بايثون 3.12 أو أحدث من python.org

أثناء التثبيت، تأكد من اختيار "Add Python to PATH"

تشغيل التطبيق:

انقر نقرًا مزدوجًا على ملف RUN.bat (أو اتبع الخطوات اليدوية بالأسفل)

الخطوات اليدوية (إذا فشل RUN.bat):

افتح موجه الأوامر في هذا المجلد:

اضغط Win+R، اكتب "cmd"، ثم:
cd /d "C:\مسار\المجلد\DiseasePrediction"

إعداد البيئة الافتراضية:
python -m venv venv
.\venv\Scripts\activate

تثبيت المتطلبات:
pip install -r requirements.txt

تشغيل التطبيق:
python app.py

الدخول عبر المتصفح:
http://localhost:5000