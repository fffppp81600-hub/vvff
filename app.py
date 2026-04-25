from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

PASSWORD = "7db"

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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:-apple-system;background:#0b0c10;color:white;padding:20px}
.menu{display:flex;gap:10px}
.menu button{flex:1;padding:15px;border-radius:15px;border:0;background:#171820;color:white;font-weight:bold}
.menu button.active{background:#00f59b;color:black}
.box{display:none;background:#181820;padding:20px;border-radius:20px;margin-top:15px}
input{width:100%;padding:12px;margin-top:10px;border-radius:12px;border:0}
.main{width:100%;padding:12px;margin-top:10px;border-radius:12px;border:0;background:#00f59b;font-weight:bold}
.error{color:red;margin-top:5px}
.progress{height:8px;background:#222;margin-top:10px;border-radius:10px;overflow:hidden}
.bar{height:100%;width:0;background:#00f59b;transition:.2s}
.resultBox{position:fixed;inset:0;background:#000a;display:none;align-items:center;justify-content:center}
.card{background:#181820;padding:20px;border-radius:20px;text-align:center}
.big{font-size:30px;color:#00f59b;font-weight:bold}
</style>

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

// 🔥 أسرع MP3 + progress
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
</head>

<body>

<div class="menu">
<button onclick="openBox('mp3',this)">MP3</button>
<button onclick="openBox('calc',this)">النسبة</button>
</div>

<div id="mp3" class="box">
<h3>تحويل MP3</h3>
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>
<input id="file" type="file" accept="audio/*,video/*">
<button class="main" onclick="convertMP3()">تحويل</button>
<div class="progress"><div id="bar" class="bar"></div></div>
</div>

<div id="calc" class="box">
<h3>حاسبة النسبة</h3>
{% for n,w in subjects.items() %}
{{n}} ({{w}}%)
<input class="g" name="{{n}}" type="number" oninput="limit(this)">
{% endfor %}
<button class="main" onclick="calc()">احسب</button>
</div>

<div id="modal" class="resultBox">
<div class="card">
<h2>نسبتك</h2>
<div id="val" class="big"></div>
<button onclick="resetG()">إعادة تعيين</button>
<button onclick="closeM()">إغلاق</button>
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
            ["ffmpeg","-y","-i",inp,"-vn",
             "-acodec","libmp3lame",
             "-b:a","96k",
             "-threads","4",
             "-preset","ultrafast",
             out],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return send_file(out, as_attachment=True, download_name="audio.mp3")

if __name__ == "__main__":
    app.run()
