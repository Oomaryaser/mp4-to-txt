import os
import uuid
import whisper
from flask import Flask, request, render_template, jsonify
from moviepy import VideoFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# تحميل موديل Whisper (base يعطي توازن بين السرعة والدقة)
print("⏳ جاري تحميل موديل Whisper ...")
model = whisper.load_model("base")
print("✅ الموديل جاهز!")


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

    # حفظ الفيديو
    unique_id = uuid.uuid4().hex[:8]
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{unique_id}_video.mp4')
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{unique_id}_audio.wav')

    try:
        video_file.save(video_path)

        # استخراج الصوت من الفيديو
        print("🎬 جاري استخراج الصوت من الفيديو...")
        video_clip = VideoFileClip(video_path)
        video_clip.audio.write_audiofile(audio_path, logger=None)
        video_clip.close()
        print("✅ تم استخراج الصوت!")

        # تحويل الصوت إلى نص
        print("📝 جاري تحويل الصوت إلى نص...")
        result = model.transcribe(audio_path)
        print("✅ تم التحويل!")

        transcript = result['text']
        language = result.get('language', 'غير معروف')

        # النتائج مع التوقيتات
        segments = []
        for seg in result.get('segments', []):
            segments.append({
                'start': format_time(seg['start']),
                'end': format_time(seg['end']),
                'text': seg['text'].strip()
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
        for path in [video_path, audio_path]:
            if os.path.exists(path):
                os.remove(path)


def format_time(seconds):
    """تحويل الثواني إلى صيغة mm:ss"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


if __name__ == '__main__':
    app.run(debug=True, port=5000)
