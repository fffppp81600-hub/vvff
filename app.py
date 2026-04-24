from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:25px}
.menu,.box{max-width:500px;margin:20px auto}
.box{background:#181820;padding:25px;border-radius:20px;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:12px;border:0;background:#00ff99}
input{width:100%;padding:12px;margin-top:8px;border-radius:10px;border:0}
.resultBox{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center}
.resultCard{background:#181820;padding:30px;border-radius:22px}
</style>

<script>
function showBox(id){
 document.querySelectorAll('.box').forEach(b=>b.style.display='none');
 document.getElementById(id).style.display='block';
}
function limitGrade(i){
 if(i.value>100)i.value=100;
 if(i.value<0)i.value=0;
}
function closeResult(){
 document.getElementById("r").style.display="none";
}
window.onload=function(){showBox("{{active}}")}
</script>
</head>

<body>

<div class="menu">
<button onclick="showBox('mp3')">MP3 🔒</button>
<button onclick="showBox('pdf')">PDF ⚡</button>
<button onclick="showBox('grades')">النسبة</button>
</div>

<div id="mp3" class="box">
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="password" name="password" placeholder="الرقم السري">
<input type="file" name="file">
<button>تحويل</button>
</form>
</div>

<div id="pdf" class="box">
<form action="/images-to-pdf" method="post" enctype="multipart/form-data">
<input type="file" name="images" multiple>
<button>تحويل سريع ⚡</button>
</form>
</div>

<div id="grades" class="box">
<form action="/grades" method="post">
{% for n,w in subjects.items() %}
{{n}} ({{w}}%)
<input type="number" name="{{n}}" oninput="limitGrade(this)">
{% endfor %}
<button>احسب</button>
</form>
</div>

{% if total %}
<div id="r" class="resultBox">
<div class="resultCard">
<h2>{{total}}%</h2>
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
    s=0
    for k,w in SUBJECTS.items():
        v=request.form.get(k)
        if v:
            v=max(0,min(float(v),100))
            s+=v*w
    t=min(s/TOTAL_WEIGHT,100)
    return render_template_string(HTML, subjects=SUBJECTS, total=round(t,2), active="grades")

# ⚡ MP3 سريع
@app.route("/convert-mp3", methods=["POST"])
def mp3():
    if request.form.get("password")!=MP3_PASSWORD:
        return "خطأ",403

    f=request.files.get("file")
    fid=str(uuid.uuid4())
    inp=f"{UPLOAD_DIR}/{fid}"
    out=f"{OUTPUT_DIR}/{fid}.mp3"
    f.save(inp)

    try:
        subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except:
        subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    return f'<a href="/download/{fid}.mp3" download>تحميل MP3</a>'

# ⚡🔥 PDF سريع جداً بدون فقد جودة
@app.route("/images-to-pdf", methods=["POST"])
def pdf():
    files=request.files.getlist("images")
    fid=str(uuid.uuid4())

    paths=[]
    for i,f in enumerate(files):
        p=f"{UPLOAD_DIR}/{fid}_{i}.jpg"
        f.save(p)
        paths.append(p)

    out=f"{OUTPUT_DIR}/{fid}.pdf"

    subprocess.run(
        ["ffmpeg","-y","-pattern_type","glob","-i",f"{UPLOAD_DIR}/{fid}_*.jpg","-c:v","copy",out],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
    )

    return f'<a href="/download/{fid}.pdf" download>تحميل PDF</a>'

@app.route("/download/<f>")
def d(f):
    return send_file(os.path.join(OUTPUT_DIR,f), as_attachment=True)

if __name__=="__main__":
    app.run()
