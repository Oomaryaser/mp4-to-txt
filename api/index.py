import os
import uuid
import tempfile
from flask import Flask, request, render_template, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB max (حد Groq)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'video' not in request.files:
        return jsonify({'error': 'لم يتم رفع أي ملف'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400

    # حفظ الملف مؤقتاً
    tmp_dir = tempfile.mkdtemp()
    unique_id = uuid.uuid4().hex[:8]
    
    # تحديد الامتداد
    original_ext = os.path.splitext(video_file.filename)[1].lower()
    if not original_ext:
        original_ext = '.mp4'
    
    file_path = os.path.join(tmp_dir, f'{unique_id}{original_ext}')

    try:
        video_file.save(file_path)

        # إرسال الملف مباشرة لـ Groq Whisper API
        # Groq يقبل ملفات الفيديو والصوت مباشرة
        with open(file_path, "rb") as audio_file:
            # الحصول على النص مع التوقيتات
            result = client.audio.transcriptions.create(
                file=(video_file.filename, audio_file),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
            )

        transcript = result.text
        language = getattr(result, 'language', 'auto')

        # استخراج المقاطع مع التوقيتات
        segments = []
        if hasattr(result, 'segments') and result.segments:
            for seg in result.segments:
                segments.append({
                    'start': format_time(seg.get('start', seg.start) if isinstance(seg, dict) else seg.start),
                    'end': format_time(seg.get('end', seg.end) if isinstance(seg, dict) else seg.end),
                    'text': (seg.get('text', '') if isinstance(seg, dict) else seg.text).strip()
                })

        return jsonify({
            'success': True,
            'transcript': transcript,
            'language': language,
            'segments': segments
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(tmp_dir):
            os.rmdir(tmp_dir)


def format_time(seconds):
    """تحويل الثواني إلى صيغة mm:ss"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


if __name__ == '__main__':
    app.run(debug=True, port=5000)
