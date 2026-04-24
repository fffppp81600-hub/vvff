from flask import Flask, request, send_file, render_template_string, jsonify
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:25px}
.box{background:#181820;padding:20px;border-radius:20px;max-width:420px;margin:auto}
button{width:100%;padding:14px;margin-top:10px;border-radius:12px;border:0;background:#00ff99}
input{width:100%;padding:10px;margin-top:8px;border-radius:10px;border:0}
.progress{height:10px;background:#333;margin-top:10px;border-radius:10px;overflow:hidden}
.bar{height:100%;width:0;background:#00ff99}
.resultBox{position:fixed;inset:0;background:#000a;display:flex;justify-content:center;align-items:center}
.card{background:#181820;padding:20px;border-radius:20px}
</style>

<script>
function limit(i){
 if(i.value>100)i.value=100;
 if(i.value<0)i.value=0;
}

function convertPDF(){
 let files=document.getElementById("pdfFiles").files;
 let form=new FormData();

 for(let f of files){
   form.append("images",f);
 }

 let bar=document.getElementById("bar");
 let p=0;

 let fake=setInterval(()=>{
   if(p<90){
     p+=5;
     bar.style.width=p+"%";
   }
 },200);

 fetch("/images-to-pdf",{method:"POST",body:form})
 .then(r=>r.json())
 .then(d=>{
   clearInterval(fake);
   bar.style.width="100%";

   document.getElementById("pdfResult").innerHTML =
   `<br><a href="/download/${d.file}" style="color:#00ff99">تحميل PDF</a>`;
 });
}
</script>
</head>

<body>

<div class="box">
<h3>تحويل MP3 🔒</h3>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="password" name="password" placeholder="الرقم السري">
<input type="file" name="file">
<button>تحويل</button>
</form>
</div>

<br>

<div class="box">
<h3>تحويل صور إلى PDF ⚡</h3>
<input type="file" id="pdfFiles" multiple>
<button onclick="convertPDF()">تحويل</button>

<div class="progress"><div id="bar" class="bar"></div></div>
<div id="pdfResult"></div>
</div>

<br>

<div class="box">
<h3>حاسبة النسبة</h3>
<form action="/grades" method="post">
{% for n,w in subjects.items() %}
{{n}} ({{w}}%)
<input type="number" name="{{n}}" oninput="limit(this)">
{% endfor %}
<button>احسب</button>
</form>
</div>

{% if total %}
<div class="resultBox">
<div class="card">
<h2>{{total}}%</h2>
<a href="/">إغلاق</a>
</div>
</div>
{% endif %}

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, subjects=SUBJECTS, total=None)

@app.route("/grades", methods=["POST"])
def grades():
    s=0
    for k,w in SUBJECTS.items():
        v=request.form.get(k)
        if v:
            v=max(0,min(float(v),100))
            s+=v*w
    t=min(s/TOTAL_WEIGHT,100)
    return render_template_string(HTML, subjects=SUBJECTS, total=round(t,2))

# MP3 سريع
@app.route("/convert-mp3", methods=["POST"])
def mp3():
    if request.form.get("password")!=MP3_PASSWORD:
        return "الرقم السري غلط",403

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

# PDF سريع وثابت
@app.route("/images-to-pdf", methods=["POST"])
def pdf():
    files=request.files.getlist("images")
    fid=str(uuid.uuid4())
    out=f"{OUTPUT_DIR}/{fid}.pdf"

    imgs=[]
    for f in files:
        img=Image.open(f.stream)
        img=ImageOps.exif_transpose(img)
        img=img.convert("RGB")
        imgs.append(img)

    imgs[0].save(out,"PDF",save_all=True,append_images=imgs[1:])

    return jsonify({"file":fid+".pdf"})

@app.route("/download/<f>")
def d(f):
    return send_file(os.path.join(OUTPUT_DIR,f), as_attachment=True)

if __name__=="__main__":
    app.run()
