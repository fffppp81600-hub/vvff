from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MP3 Converter</title>
<style>
body{font-family:Arial;background:#111;color:white;text-align:center;padding:40px}
.box{background:#1c1c1c;padding:30px;border-radius:18px;max-width:420px;margin:auto}
input,button{width:100%;padding:14px;margin-top:15px;border-radius:12px;border:0}
button{background:#00ff99;font-weight:bold;cursor:pointer}
</style>
</head>
<body>
<div class="box">
<h1>حوّل إلى MP3</h1>
<p>ارفع مقطع 5 دقايق أو أقل</p>
<form action="/convert" method="post" enctype="multipart/form-data">
<input type="file" name="file" accept="video/*,audio/*" required>
<button type="submit">تحويل سريع</button>
</form>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return "مافي ملف", 400

    file = request.files["file"]
    if file.filename == "":
        return "اختر ملف", 400

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)
    output_path = os.path.join(OUTPUT_DIR, file_id + ".mp3")

    file.save(input_path)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-b:a", "192k",
        "-threads", "2",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        return "فشل التحويل، جرّب ملف ثاني", 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    return send_file(output_path, as_attachment=True, download_name="converted.mp3")

if __name__ == "__main__":
    app.run()