@echo off
:: الكود دا بيشغل التطبيق أوتوماتيك على الويندوز

:: أول حاجة بنتأكد إن بايثون مثبت
python --version >nul 2>&1
if %errorlevel% neq 0 (
echo خطأ: بايثون مش موجود. يرجى تثبيت بايثون 3.12 أو أحدث أولاً.
pause
exit
)

:: بنعمل إعدادات البيئة الافتراضية
python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt

:: بنشغل التطبيق
echo جاري تشغيل نظام التنبؤ بالأمراض...
echo افتح المتصفح على الرابط دا: http://localhost:5000
python app.py
pause