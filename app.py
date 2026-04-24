<input type="number" name="{{name}}" min="0" max="100" step="0.01"
oninput="if(this.value>100)this.value=100"
placeholder="من 100">
import os, uuid, subprocess
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUBJECTS = {
    "رياضيات": 14.63,
    "المواظبه": 12.2,
    "لغتي": 12.2,
    "الاسلاميه": 12.2,
    "الانقليزي": 9.76,
    "العلوم": 9.76,
    "الاجتماعيات": 7.32,
    "الفنيه": 4.88,
    "مهارات رقميه": 4.88,
    "بدنيه": 4.88,
    "السلوك": 2.44,
    "نشاط": 2.44,
    "حياتيه": 2.44
}

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rakan Tools</title>
<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:25px}
.box{background:#181820;padding:25px;border-radius:20px;max-width:500px;margin:20px auto;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:12px;border:0;background:#00ff99;font-weight:bold;cursor:pointer}
input{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:0}
.menu{max-width:500px;margin:auto}
.subject{margin-top:8px;text-align:right}
.result{font-size:22px;color:#00ff99;margin-top:15px}
</style>

<script>
function showBox(id){
    document.querySelectorAll('.box').forEach(b => b.style.display='none');
    document.getElementById(id).style.display='block';
}
</script>
</head>

<body>

<div class="menu">
<h2>اختر الخدمة</h2>
<button onclick="showBox('mp3')">تحويل MP3</button>
<button onclick="showBox('pdf')">صور إلى PDF</button>
<button onclick="showBox('grades')">حاسبة النسبة</button>
</div>

<div id="mp3" class="box">
<h3>MP3 Converter</h3>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="file" name="file" required>
<button type="submit">تحويل</button>
</form>
</div>

<div id="pdf" class="box">
<h3>Images to PDF</h3>
<form action="/images-to-pdf" method="post" enctype="multipart/form-data">
<input type="file" name="images" multiple required>
<button type="submit">تحويل</button>
</form>
</div>

<div id="grades" class="box">
<h3>حاسبة النسبة</h3>
<form action="/grades" method="post">
{% for name, weight in subjects.items() %}
<div class="subject">
{{name}} ({{weight}}%)
<input type="number" name="{{name}}" min="0" max="100" step="0.01" placeholder="من 100">
</div>
{% endfor %}
<button type="submit">احسب</button>
</form>

{% if total is not none %}
<div class="result">{{total}}%</div>
{% endif %}
</div>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, subjects=SUBJECTS, total=None)

@app.route("/grades", methods=["POST"])
def grades():
    total = 0
    for subject, weight in SUBJECTS.items():
        val = request.form.get(subject)
        if val:
            grade = min(float(val), 100)  # حد أقصى 100
            total += (grade / 100) * weight

    return render_template_string(HTML, subjects=SUBJECTS, total=round(total, 2))

@app.route("/convert-mp3", methods=["POST"])
def convert_mp3():
    file = request.files.get("file")
    if not file:
        return "اختر ملف", 400

    fid = str(uuid.uuid4())
    inp = f"uploads/{fid}_{file.filename}"
    out = f"outputs/{fid}.mp3"
    file.save(inp)

    try:
        subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","192k",out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        return "فشل التحويل", 400
    finally:
        if os.path.exists(inp): os.remove(inp)

    return send_file(out, as_attachment=True)

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    files = request.files.getlist("images")
    if not files:
        return "اختر صور", 400

    fid = str(uuid.uuid4())
    out = f"outputs/{fid}.pdf"

    imgs = []
    for f in files:
        img = Image.open(f.stream).convert("RGB")
        imgs.append(img)

    imgs[0].save(out, save_all=True, append_images=imgs[1:])
    return send_file(out, as_attachment=True)

if __name__ == "__main__":
    app.run()from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUBJECTS = {
    "رياضيات": 14.63,
    "المواظبه": 12.2,
    "لغتي": 12.2,
    "الاسلاميه": 12.2,
    "الانقليزي": 9.76,
    "العلوم": 9.76,
    "الاجتماعيات": 7.32,
    "الفنيه": 4.88,
    "مهارات رقميه": 4.88,
    "بدنيه": 4.88,
    "السلوك": 2.44,
    "نشاط": 2.44,
    "حياتيه": 2.44
}

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rakan Tools</title>
<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:25px}
.box{background:#181820;padding:25px;border-radius:20px;max-width:500px;margin:20px auto;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:12px;border:0;background:#00ff99;font-weight:bold;cursor:pointer}
input{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:0}
.menu{max-width:500px;margin:auto}
.subject{margin-top:8px;text-align:right}
.result{font-size:22px;color:#00ff99;margin-top:15px}
</style>

<script>
function showBox(id){
    document.querySelectorAll('.box').forEach(b => b.style.display='none');
    document.getElementById(id).style.display='block';
}
</script>
</head>

<body>

<div class="menu">
<h2>اختر الخدمة</h2>
<button onclick="showBox('mp3')">تحويل MP3</button>
<button onclick="showBox('pdf')">صور إلى PDF</button>
<button onclick="showBox('grades')">حاسبة النسبة</button>
</div>

<div id="mp3" class="box">
<h3>MP3 Converter</h3>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="file" name="file" required>
<button type="submit">تحويل</button>
</form>
</div>

<div id="pdf" class="box">
<h3>Images to PDF</h3>
<form action="/images-to-pdf" method="post" enctype="multipart/form-data">
<input type="file" name="images" multiple required>
<button type="submit">تحويل</button>
</form>
</div>

<div id="grades" class="box">
<h3>حاسبة النسبة</h3>
<form action="/grades" method="post">
{% for name, weight in subjects.items() %}
<div class="subject">
{{name}} ({{weight}}%)
<input type="number" name="{{name}}" min="0" max="100" step="0.01" placeholder="من 100">
</div>
{% endfor %}
<button type="submit">احسب</button>
</form>

{% if total is not none %}
<div class="result">{{total}}%</div>
{% endif %}
</div>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, subjects=SUBJECTS, total=None)

@app.route("/grades", methods=["POST"])
def grades():
    total = 0
    for subject, weight in SUBJECTS.items():
        val = request.form.get(subject)
        if val:
            grade = min(float(val), 100)  # حد أقصى 100
            total += (grade / 100) * weight

    return render_template_string(HTML, subjects=SUBJECTS, total=round(total, 2))

@app.route("/convert-mp3", methods=["POST"])
def convert_mp3():
    file = request.files.get("file")
    if not file:
        return "اختر ملف", 400

    fid = str(uuid.uuid4())
    inp = f"uploads/{fid}_{file.filename}"
    out = f"outputs/{fid}.mp3"
    file.save(inp)

    try:
        subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","192k",out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        return "فشل التحويل", 400
    finally:
        if os.path.exists(inp): os.remove(inp)

    return send_file(out, as_attachment=True)

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    files = request.files.getlist("images")
    if not files:
        return "اختر صور", 400

    fid = str(uuid.uuid4())
    out = f"outputs/{fid}.pdf"

    imgs = []
    for f in files:
        img = Image.open(f.stream).convert("RGB")
        imgs.append(img)

    imgs[0].save(out, save_all=True, append_images=imgs[1:])
    return send_file(out, as_attachment=True)

if __name__ == "__main__":
    app.run()