from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess, io
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
.box{background:#181820;padding:22px;border-radius:22px;display:none}
button{width:100%;padding:15px;margin-top:10px;border-radius:14px;border:0;background:#00ff99;font-weight:bold;font-size:16px}
input{width:100%;padding:12px;margin-top:9px;border-radius:12px;border:0;box-sizing:border-box}
.progress{height:14px;background:#333;margin-top:15px;border-radius:20px;overflow:hidden}
.bar{height:100%;width:0;background:#00ff99;transition:.2s}
.status{margin-top:12px;color:#ccc}
.download{display:block;background:#00ff99;color:#000;padding:15px;border-radius:14px;text-decoration:none;font-weight:bold;margin-top:18px}
.subject{text-align:right;margin-top:8px}
.resultBox{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center}
.card{background:#181820;padding:28px;border-radius:22px;width:85%;max-width:360px}
.big{font-size:32px;color:#00ff99;font-weight:bold}
</style>

<script>
function showBox(id){
  document.querySelectorAll('.box').forEach(b=>b.style.display='none');
  document.getElementById(id).style.display='block';
}

function limit(i){
  if(i.value>100)i.value=100;
  if(i.value<0)i.value=0;
}

function closeResult(){
  document.getElementById("resultBox").style.display="none";
}

window.onload=function(){showBox("{{active}}")}

async function convertPDF(){
  let files=document.getElementById("pdfFiles").files;
  if(files.length===0){
    alert("اختر الصور أول");
    return;
  }

  let form=new FormData();
  for(let f of files){
    form.append("images",f);
  }

  let bar=document.getElementById("pdfBar");
  let status=document.getElementById("pdfStatus");
  let result=document.getElementById("pdfResult");

  bar.style.width="0%";
  result.innerHTML="";
  status.innerHTML="بدأ التحويل...";

  let seconds=Math.max(5, files.length * 2);
  let progress=0;

  let timer=setInterval(()=>{
    if(seconds>0) seconds--;

    if(progress < 90){
      progress += 4;
      bar.style.width = progress + "%";
    }

    status.innerHTML = "جاري تجهيز PDF... باقي تقريباً " + seconds + " ثانية";
  },1000);

  try{
    let response = await fetch("/images-to-pdf", {
      method:"POST",
      body:form
    });

    clearInterval(timer);

    if(!response.ok){
      status.innerHTML="صار خطأ بالسيرفر، جرّب صور أقل";
      return;
    }

    let blob = await response.blob();
    let url = window.URL.createObjectURL(blob);

    bar.style.width="100%";
    status.innerHTML="جاهز ✅";

    result.innerHTML = '<a class="download" href="'+url+'" download="images.pdf">تنزيل PDF</a>';

  }catch(e){
    clearInterval(timer);
    status.innerHTML="فشل الاتصال، جرّب مرة ثانية";
  }
}
</script>
</head>

<body>

<div class="menu">
<h2>اختر الخدمة</h2>
<button onclick="showBox('mp3')">تحويل MP3 🔒</button>
<button onclick="showBox('pdf')">صور إلى PDF ⚡</button>
<button onclick="showBox('grades')">حاسبة النسبة</button>
</div>

<div id="mp3" class="box">
<h3>تحويل MP3</h3>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="password" name="password" placeholder="الرقم السري">
<input type="file" name="file">
<button type="submit">تحويل MP3</button>
</form>
</div>

<div id="pdf" class="box">
<h3>صور إلى PDF</h3>
<input type="file" id="pdfFiles" accept="image/*" multiple>
<button type="button" onclick="convertPDF()">تحويل PDF</button>
<div class="progress"><div id="pdfBar" class="bar"></div></div>
<div id="pdfStatus" class="status"></div>
<div id="pdfResult"></div>
</div>

<div id="grades" class="box">
<h3>حاسبة النسبة</h3>
<form action="/grades" method="post">
{% for n,w in subjects.items() %}
<div class="subject">
{{n}} ({{w}}%)
<input type="number" name="{{n}}" min="0" max="100" step="0.01" oninput="limit(this)" placeholder="من 100">
</div>
{% endfor %}
<button type="submit">احسب</button>
</form>
</div>

{% if total is not none %}
<div id="resultBox" class="resultBox">
<div class="card">
<h2>نسبتك</h2>
<div class="big">{{total}}%</div>
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
    s = 0
    for k, w in SUBJECTS.items():
        v = request.form.get(k)
        if v:
            v = max(0, min(float(v), 100))
            s += v * w

    total = min(s / TOTAL_WEIGHT, 100)
    return render_template_string(HTML, subjects=SUBJECTS, total=round(total, 2), active="grades")

@app.route("/convert-mp3", methods=["POST"])
def mp3():
    if request.form.get("password") != MP3_PASSWORD:
        return "الرقم السري غلط", 403

    f = request.files.get("file")
    if not f:
        return "اختر ملف", 400

    fid = str(uuid.uuid4())
    inp = os.path.join(UPLOAD_DIR, fid)
    out = os.path.join(OUTPUT_DIR, fid + ".mp3")
    f.save(inp)

    try:
        r = subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if r.returncode != 0:
            raise Exception()
    except:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    finally:
        if os.path.exists(inp):
            os.remove(inp)

    return send_file(out, as_attachment=True, download_name="converted.mp3")

@app.route("/images-to-pdf", methods=["POST"])
def pdf():
    files = request.files.getlist("images")
    if not files:
        return "مافي صور", 400

    imgs = []

    try:
        for f in files:
            img = Image.open(f.stream)
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            imgs.append(img)

        pdf_buffer = io.BytesIO()
        imgs[0].save(pdf_buffer, "PDF", save_all=True, append_images=imgs[1:])
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="images.pdf"
        )

    except Exception as e:
        return "فشل تحويل الصور", 500

if __name__ == "__main__":
    app.run()
