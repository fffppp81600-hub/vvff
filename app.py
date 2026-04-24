from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess
from PIL import Image, ImageOps

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MP3_PASSWORD = "7db"

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

TOTAL_WEIGHT = sum(SUBJECTS.values())

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rakan Tools</title>

<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:25px}
.menu,.box{max-width:500px;margin:20px auto}
.box{background:#181820;padding:25px;border-radius:20px;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:12px;border:0;background:#00ff99;font-weight:bold;cursor:pointer}
input{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:0;box-sizing:border-box}
.subject{text-align:right;margin-top:8px}
.resultBox{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center}
.resultCard{background:#181820;padding:30px;border-radius:22px;width:85%;max-width:360px}
.resultText{font-size:30px;color:#00ff99;font-weight:bold}
a.download{display:block;background:#00ff99;color:#000;padding:16px;border-radius:14px;text-decoration:none;font-weight:bold;margin-top:20px}
</style>

<script>
function showBox(id){
    document.querySelectorAll('.box').forEach(b => b.style.display='none');
    document.getElementById(id).style.display='block';
}
function limitGrade(input){
    if(input.value > 100) input.value = 100;
    if(input.value < 0) input.value = 0;
}
function closeResult(){
    document.getElementById("resultBox").style.display="none";
}
window.onload=function(){showBox("{{active}}")}
</script>
</head>

<body>

<div class="menu">
<h2>اختر الخدمة</h2>
<button onclick="showBox('mp3')">تحويل MP3 🔒</button>
<button onclick="showBox('pdf')">صور إلى PDF</button>
<button onclick="showBox('grades')">حاسبة النسبة</button>
</div>

<div id="mp3" class="box">
<h3>تحويل MP3</h3>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="password" name="password" placeholder="الرقم السري" required>
<input type="file" name="file" required>
<button type="submit">تحويل</button>
</form>
</div>

<div id="pdf" class="box">
<h3>صور إلى PDF</h3>
<form action="/images-to-pdf" method="post" enctype="multipart/form-data">
<input type="file" name="images" accept="image/*" multiple required>
<button type="submit">تحويل PDF</button>
</form>
</div>

<div id="grades" class="box">
<h3>حاسبة النسبة</h3>
<form action="/grades" method="post">
{% for name, weight in subjects.items() %}
<div class="subject">
{{name}} ({{weight}}%)
<input type="number" name="{{name}}" min="0" max="100" step="0.01" oninput="limitGrade(this)">
</div>
{% endfor %}
<button type="submit">احسب</button>
</form>
</div>

{% if total is not none %}
<div id="resultBox" class="resultBox">
<div class="resultCard">
<h2>نسبتك</h2>
<div class="resultText">{{total}}%</div>
<button onclick="closeResult()">إغلاق</button>
</div>
</div>
{% endif %}

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, subjects=SUBJECTS, total=None, active="mp3")

@app.route("/grades", methods=["POST"])
def grades():
    weighted_sum = 0
    for subject, weight in SUBJECTS.items():
        val = request.form.get(subject)
        if val:
            grade = max(0, min(float(val), 100))
            weighted_sum += grade * weight

    total = weighted_sum / TOTAL_WEIGHT
    total = min(total, 100)

    return render_template_string(HTML, subjects=SUBJECTS, total=round(total, 2), active="grades")

@app.route("/convert-mp3", methods=["POST"])
def convert_mp3():
    if request.form.get("password") != MP3_PASSWORD:
        return "الرقم السري غلط", 403

    file = request.files.get("file")
    if not file:
        return "اختر ملف", 400

    fid = str(uuid.uuid4())
    inp = f"{UPLOAD_DIR}/{fid}_{file.filename}"
    out = f"{OUTPUT_DIR}/{fid}.mp3"
    file.save(inp)

    try:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    finally:
        if os.path.exists(inp):
            os.remove(inp)

    return render_template_string("""
    <h2>تم التحويل ✅</h2>
    <a href="/download/{{f}}" download>تنزيل MP3</a>
    """, f=fid + ".mp3")

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    files = request.files.getlist("images")
    fid = str(uuid.uuid4())
    out = f"{OUTPUT_DIR}/{fid}.pdf"

    imgs = []
    for f in files:
        img = ImageOps.exif_transpose(Image.open(f.stream)).convert("RGB")
        imgs.append(img)

    imgs[0].save(out, "PDF", save_all=True, append_images=imgs[1:])

    return render_template_string("""
    <h2>تم إنشاء PDF ✅</h2>
    <a href="/download/{{f}}" download>تنزيل PDF</a>
    """, f=fid + ".pdf")

@app.route("/download/<f>")
def download(f):
    path = os.path.join(OUTPUT_DIR, f)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run()
