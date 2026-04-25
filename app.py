from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

PASSWORD = "7db"

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
TOTAL = sum(SUBJECTS.values())

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Rakan Tools</title>

<style>
*{box-sizing:border-box}
body{
  margin:0;
  min-height:100vh;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial;
  background:
    radial-gradient(circle at top right,#103b34,transparent 35%),
    radial-gradient(circle at bottom left,#10243b,transparent 35%),
    #07080c;
  color:white;
  padding:22px;
}
.app{max-width:520px;margin:auto}
.title{text-align:center;margin:20px 0 18px}
.title h1{margin:0;font-size:34px}
.title p{margin:8px 0;color:#a9a9b5}

.menu{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px}
.menu button{
  padding:16px;border:0;border-radius:20px;
  background:#171820;color:white;font-weight:900;font-size:16px;
  border:1px solid rgba(255,255,255,.08)
}
.menu button.active{
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  color:#03110b;
}

.box{
  display:none;
  background:rgba(23,24,32,.92);
  border:1px solid rgba(255,255,255,.08);
  border-radius:30px;
  padding:26px;
  box-shadow:0 25px 80px rgba(0,0,0,.55);
  animation:pop .18s ease;
}
@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.box h2{margin:0 0 18px;text-align:center;font-size:28px}

input{
  width:100%;
  padding:15px;
  margin-top:10px;
  border:0;
  border-radius:18px;
  font-size:16px;
  background:white;
  color:#111;
}
.mainBtn{
  width:100%;
  padding:17px;
  margin-top:18px;
  border:0;
  border-radius:20px;
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  color:#03110b;
  font-weight:900;
  font-size:17px;
}
.error{color:#ff3838;margin-top:10px;font-weight:900;text-align:center}
.status{color:#c7c7d3;margin-top:12px;text-align:center;font-weight:800}
.download{
  display:block;
  margin-top:16px;
  padding:16px;
  border-radius:20px;
  background:#00f59b;
  color:#03110b;
  text-decoration:none;
  text-align:center;
  font-weight:900;
}
.subject{text-align:right;margin-top:14px;color:#e7e7ee;font-weight:800}
.subject small{color:#a7a7b5}

.modal{
  position:fixed;inset:0;background:rgba(0,0,0,.72);
  display:none;align-items:center;justify-content:center;
  padding:22px;z-index:99
}
.card{
  width:100%;max-width:380px;
  background:#171820;
  border-radius:28px;
  padding:28px;
  text-align:center;
  border:1px solid rgba(255,255,255,.08);
}
.big{font-size:42px;color:#00f59b;font-weight:900;margin:10px 0}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
.closeBtn,.resetBtn{
  padding:15px;border:0;border-radius:18px;font-weight:900;font-size:15px
}
.closeBtn{background:#2a2b33;color:white}
.resetBtn{background:#00f59b;color:#03110b}
</style>

<script>
const SUBJECTS={{ subjects|tojson }};
const TOTAL={{ total }};

function openBox(id, btn){
  document.querySelectorAll(".box").forEach(b=>b.style.display="none");
  document.querySelectorAll(".menu button").forEach(b=>b.classList.remove("active"));
  document.getElementById(id).style.display="block";
  btn.classList.add("active");
  window.scrollTo({top:0,behavior:"smooth"});
}

function limit(i){
  if(i.value>100)i.value=100;
  if(i.value<0)i.value=0;
}

async function convertMP3(){
  const pass=document.getElementById("pass").value;
  const file=document.getElementById("file").files[0];
  const err=document.getElementById("err");
  const res=document.getElementById("mp3res");

  err.innerHTML="";
  res.innerHTML="";

  if(!pass){err.innerHTML="اكتب الرقم السري";return;}
  if(!file){err.innerHTML="اختر ملف صوت أو فيديو";return;}

  const form=new FormData();
  form.append("password",pass);
  form.append("file",file);

  res.innerHTML="<div class='status'>جاري التحويل...</div>";

  const r=await fetch("/convert-mp3",{method:"POST",body:form});

  if(r.status===403){
    err.innerHTML="كلمة السر غير صحيحة";
    res.innerHTML="";
    return;
  }
  if(!r.ok){
    err.innerHTML="فشل التحويل";
    res.innerHTML="";
    return;
  }

  const blob=await r.blob();
  const url=URL.createObjectURL(blob);
  res.innerHTML=`<a class="download" href="${url}" download="audio.mp3">تحميل MP3</a>`;
}

function calc(){
  let sum=0;

  for(const k in SUBJECTS){
    const el=document.getElementsByName(k)[0];
    let v=el.value;
    if(v){
      v=Math.max(0,Math.min(100,parseFloat(v)));
      sum+=v*SUBJECTS[k];
    }
  }

  const total=Math.min(sum/TOTAL,100).toFixed(2);
  document.getElementById("resultValue").innerHTML=total+"%";
  document.getElementById("modal").style.display="flex";
}

function closeModal(){
  document.getElementById("modal").style.display="none";
}

function resetGrades(){
  document.querySelectorAll(".gradeInput").forEach(i=>i.value="");
  document.getElementById("modal").style.display="none";
}
</script>
</head>

<body>
<div class="app">

<div class="title">
<h1>Rakan Tools</h1>
<p>أدواتك السريعة بشكل مرتب وفخم</p>
</div>

<div class="menu">
<button onclick="openBox('mp3Box',this)">🔒 MP3</button>
<button onclick="openBox('calcBox',this)">🧮 النسبة</button>
</div>

<div id="mp3Box" class="box">
<h2>تحويل MP3 🔒</h2>
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>
<input id="file" type="file" accept="audio/*,video/*">
<button class="mainBtn" onclick="convertMP3()">تحويل</button>
<div id="mp3res"></div>
</div>

<div id="calcBox" class="box">
<h2>حاسبة النسبة</h2>
{% for n,w in subjects.items() %}
<div class="subject">{{n}} <small>({{w}}%)</small></div>
<input class="gradeInput" name="{{n}}" type="number" min="0" max="100" step="0.01" oninput="limit(this)" placeholder="درجتك من 100">
{% endfor %}
<button class="mainBtn" onclick="calc()">احسب النسبة</button>
</div>

<div id="modal" class="modal">
<div class="card">
<h2>نسبتك</h2>
<div id="resultValue" class="big"></div>
<p style="color:#aaa;margin:0">تبي تعيد إدخال الدرجات ولا تقفل وتخليها؟</p>
<div class="row">
<button class="resetBtn" onclick="resetGrades()">إعادة تعيين</button>
<button class="closeBtn" onclick="closeModal()">إغلاق</button>
</div>
</div>
</div>

</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, subjects=SUBJECTS, total=TOTAL)

@app.route("/convert-mp3", methods=["POST"])
def convert():
    if request.form.get("password") != PASSWORD:
        return "wrong", 403

    f = request.files.get("file")
    if not f:
        return "no file", 400

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

    return send_file(out, as_attachment=True, download_name="audio.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run()
