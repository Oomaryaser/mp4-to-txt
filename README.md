# 🎬 MP4 to Text (mp4-to-txt)

تطبيق ويب لتحويل ملفات الفيديو والصوت إلى نص مكتوب (Script) باستخدام Whisper AI.

## المميزات
- ✅ رفع ملفات فيديو MP4 أو ملفات صوتية
- ✅ تحويل تلقائي للصوت إلى نص باستخدام Whisper Large V3 Turbo
- ✅ عرض النص مع التوقيتات
- ✅ دعم اللغة العربية والإنجليزية وأكثر من 50 لغة
- ✅ نسخ النص بضغطة زر
- ✅ واجهة عصرية وجميلة

## التشغيل محلياً

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your-groq-api-key"
python api/index.py
```

## النشر على Vercel

1. احصل على مفتاح API مجاني من [Groq Console](https://console.groq.com)
2. أضف `GROQ_API_KEY` في Environment Variables على Vercel
3. انشر المشروع

## التقنيات
- Flask (Python)
- Groq API (Whisper Large V3 Turbo)
- Vercel Serverless Functions
