from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
MP3_PASSWORD = "7db"

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
.menu,.box{max-width:500px;margin:20px auto}
.box{background:#181820;padding:25px;border-radius:20px;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:12px;border:0;background:#00ff99;font-weight:bold;cursor:pointer}
input{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:0;box-sizing:border-box}
.subject{margin-top:8px;text-align:right}
.resultBox{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center}
.resultCard{background:#181820;padding:30px;border-radius:22px;width:85%;max-width:360px}
.resultText{font-size:28px;color:#00ff99;font-weight:bold}
</style>
<script>
function showBox(id){
    if(id === "mp3"){
        let pass = prompt("اكتب الرقم السري");
        if(pass !== "7db"){
            alert("الرقم السري غلط");
            return;
        }
    }
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
<button onclick="showBox('mp3')">تحويل MP3</button>
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
<input type="number" name="{{name}}" min="0" max="100" step="0.01" placeholder="درجتك من 100" oninput="limitGrade(this)">
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
    return render_template_string(HTML, subjects=SUBJECTS, total=None, active="pdf")

@app.route("/grades", methods=["POST"])
def grades():
    total = 0
    for subject, weight in SUBJECTS.items():
        val = request.form.get(subject)
        if val:
            grade = max(0, min(float(val), 100))
            total += (grade / 100) * weight

    return render_template_string(HTML, subjects=SUBJECTS, total=round(total, 2), active="grades")

@app.route("/convert-mp3", methods=["POST"])
def convert_mp3():
    if request.form.get("password") != MP3_PASSWORD:
        return "الرقم السري غلط", 403

    file = request.files.get("file")
    if not file:
        return "اختر ملف", 400

    fid = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    inp = os.path.join(UPLOAD_DIR, f"{fid}_{safe_name}")
    out = os.path.join(OUTPUT_DIR, f"{fid}.mp3")

    file.save(inp)

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", inp, "-vn", "-acodec", "libmp3lame", "-b:a", "192k", out],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        return "فشل التحويل", 400
    finally:
        if os.path.exists(inp):
            os.remove(inp)

    return render_template_string("""
    <html lang="ar" dir="rtl">
    <body style="font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:40px">
    <h2>تم التحويل ✅</h2>
    <a style="display:block;background:#00ff99;color:#000;padding:16px;border-radius:14px;text-decoration:none;font-weight:bold"
    href="/download/{{filename}}">تنزيل MP3</a>
    </body>
    </html>
    """, filename=fid + ".mp3")

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    files = request.files.getlist("images")
    if not files:
        return "اختر صور", 400

    fid = str(uuid.uuid4())
    out = os.path.join(OUTPUT_DIR, f"{fid}.pdf")
    imgs = []

    try:
        for f in files:
            img = Image.open(f.stream)
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            imgs.append(img)

        if not imgs:
            return "اختر صور صحيحة", 400

        imgs[0].save(out, "PDF", save_all=True, append_images=imgs[1:])

    except:
        return "فشل تحويل الصور", 400

    return render_template_string("""
    <html lang="ar" dir="rtl">
    <body style="font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:40px">
    <h2>تم تحويل الصور إلى PDF ✅</h2>
    <a style="display:block;background:#00ff99;color:#000;padding:16px;border-radius:14px;text-decoration:none;font-weight:bold"
    href="/download/{{filename}}?download=1">تنزيل PDF</a>
    </body>
    </html>
    """, filename=fid + ".pdf")

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        return "الملف غير موجود", 404

    if filename.endswith(".pdf"):
        return send_file(
            path,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="images.pdf"
        )

    if filename.endswith(".mp3"):
        return send_file(
            path,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="converted.mp3"
        )

    return "ملف غير معروف", 400

if __name__ == "__main__":
    app.run()
