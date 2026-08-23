from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

PASSWORD = "76B"

SUBJECTS = {
    "رياضيات": 14.63,"المواظبه": 12.2,"لغتي": 12.2,"الاسلاميه": 12.2,
    "الانقليزي": 9.76,"العلوم": 9.76,"الاجتماعيات": 7.32,
    "الفنيه": 4.88,"مهارات رقميه": 4.88,"بدنيه": 4.88,
    "السلوك": 2.44,"نشاط": 2.44,"حياتيه": 2.44
}
TOTAL = sum(SUBJECTS.values())

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">

<style>
*{box-sizing:border-box}

body{
  margin:0;
  font-family:-apple-system,BlinkMacSystemFont;
  background:
    radial-gradient(circle at 20% 20%, #00f59b33, transparent),
    radial-gradient(circle at 80% 80%, #00d9ff33, transparent),
    #05060a;
  color:white;
  padding:18px;
}

.app{max-width:480px;margin:auto}

.header{text-align:center;margin-bottom:20px}
.header h1{
  font-size:36px;
  margin:0;
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}
.header p{color:#aaa}

.menu{
  display:flex;
  gap:8px;
  background:#12131a;
  padding:6px;
  border-radius:20px;
}
.menu button{
  flex:1;
  border:0;
  border-radius:16px;
  padding:14px;
  background:transparent;
  color:#aaa;
  font-weight:900;
  transition:.25s;
}
.menu button.active{
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  color:#000;
  box-shadow:0 0 20px #00f59b88;
}

.box{
  display:none;
  margin-top:15px;
  padding:24px;
  border-radius:28px;
  background:rgba(255,255,255,0.05);
  backdrop-filter:blur(25px);
  border:1px solid rgba(255,255,255,0.1);
  box-shadow:0 30px 80px rgba(0,0,0,.7);
  animation:fade .25s ease;
}
@keyframes fade{
  from{opacity:0;transform:translateY(10px)}
  to{opacity:1}
}

h3{text-align:center}

input{
  width:100%;
  padding:15px;
  margin-top:10px;
  border-radius:18px;
  border:none;
  background:#1c1e26;
  color:white;
  font-size:15px;
}
input:focus{box-shadow:0 0 15px #00f59b66}

.main{
  width:100%;
  padding:16px;
  margin-top:12px;
  border-radius:20px;
  border:none;
  font-weight:900;
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  color:black;
  box-shadow:0 10px 30px #00f59b55;
  transition:.2s;
}
.main:hover{transform:scale(1.04)}

.error{color:#ff4444;text-align:center;margin-top:8px}

.progress{
  height:8px;
  margin-top:10px;
  background:#222;
  border-radius:10px;
  overflow:hidden;
}
.bar{
  height:100%;
  width:0%;
  background:linear-gradient(90deg,#00f59b,#00d9ff);
  transition:.2s;
}

.subject{margin-top:10px;color:#ddd;font-weight:700}

.resultBox{
  position:fixed;
  inset:0;
  display:none;
  align-items:center;
  justify-content:center;
  background:rgba(0,0,0,.7);
  z-index:99;
}
.card{
  background:#111218;
  padding:30px;
  border-radius:30px;
  text-align:center;
}
.big{
  font-size:42px;
  color:#00f59b;
}
</style>
</head>

<body>

<div class="app">

<div class="header">
<h1>Rakan Tools</h1>
<p>نسخة فخمة 🔥</p>
</div>

<div class="menu">
<button onclick="openBox('mp3',this)">MP3</button>
<button onclick="openBox('calc',this)">النسبة</button>
</div>

<div id="mp3" class="box">
<h3>تحويل MP3</h3>
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>

<input id="file" type="file">

<button class="main" onclick="convertMP3()">تحويل</button>
<div class="progress"><div id="bar" class="bar"></div></div>
</div>

<div id="calc" class="box">
<h3>حاسبة النسبة</h3>
{% for n,w in subjects.items() %}
<div class="subject">{{n}} ({{w}}%)</div>
<input class="g" name="{{n}}" type="number" min="0" max="100" step="0.01" oninput="limit(this)">
{% endfor %}
<button class="main" onclick="calc()">احسب</button>
</div>

<div id="modal" class="resultBox">
<div class="card">
<h2>نسبتك</h2>
<div id="val" class="big"></div>
<button class="main" onclick="resetG()">إعادة تعيين</button>
<button class="main" style="background:#333;color:white" onclick="closeM()">إغلاق</button>
</div>
</div>

</div>

<script>
const SUBJECTS = {{ subjects|tojson }};
const TOTAL = {{ total }};

function openBox(id,btn){
 document.querySelectorAll(".box").forEach(b=>b.style.display="none");
 document.querySelectorAll(".menu button").forEach(b=>b.classList.remove("active"));
 document.getElementById(id).style.display="block";
 btn.classList.add("active");
}

function limit(i){
 if(i.value>100)i.value=100;
 if(i.value<0)i.value=0;
}

function closeM(){document.getElementById("modal").style.display="none";}
function resetG(){document.querySelectorAll(".g").forEach(i=>i.value="");closeM();}

function calc(){
 let sum=0;
 for(let k in SUBJECTS){
   let v=document.getElementsByName(k)[0].value;
   if(v){
     v=Math.max(0,Math.min(100,parseFloat(v)));
     sum+=v*SUBJECTS[k];
   }
 }
 let total=Math.min(sum/TOTAL,100).toFixed(2);
 document.getElementById("val").innerHTML=total+"%";
 document.getElementById("modal").style.display="flex";
}

function convertMP3(){
 let pass=document.getElementById("pass").value;
 let file=document.getElementById("file").files[0];
 let err=document.getElementById("err");
 let bar=document.getElementById("bar");

 err.innerHTML="";
 bar.style.width="0%";

 if(!pass){err.innerHTML="اكتب الرقم السري";return;}
 if(!file){err.innerHTML="اختر ملف";return;}

 let form=new FormData();
 form.append("password",pass);
 form.append("file",file);

 let xhr=new XMLHttpRequest();

 xhr.upload.onprogress=function(e){
   if(e.lengthComputable){
     bar.style.width=((e.loaded/e.total)*100)+"%";
   }
 };

 xhr.onload=function(){
   if(xhr.status==403){
     err.innerHTML="كلمة السر غير صحيحة";
     return;
   }

   let blob=new Blob([xhr.response]);
   let url=URL.createObjectURL(blob);

   let a=document.createElement("a");
   a.href=url;
   a.download="audio.mp3";
   a.click();

   bar.style.width="100%";
 };

 xhr.open("POST","/convert-mp3");
 xhr.responseType="arraybuffer";
 xhr.send(form);
}
</script>

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
    inp = f"{UPLOAD_DIR}/{fid}"
    out = f"{OUTPUT_DIR}/{fid}.mp3"
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
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame",
             "-b:a","96k","-threads","4","-preset","ultrafast",out],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return send_file(out, as_attachment=True, download_name="audio.mp3")

if __name__ == "__main__":
    app.run()
