from flask import Flask, request, send_file, render_template_string, jsonify
import os, uuid, subprocess

app = Flask(__name__)

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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial;background:#0b0c10;color:white;padding:20px}
.box{background:#181820;padding:20px;border-radius:20px;margin-top:15px}
input,button{width:100%;padding:12px;margin-top:10px;border-radius:12px;border:0}
button{background:#00f59b;font-weight:bold}
.error{color:red}
.resultBox{position:fixed;inset:0;background:#000a;display:none;align-items:center;justify-content:center}
.card{background:#181820;padding:20px;border-radius:20px;text-align:center}
</style>

<script>
function toggle(id){
 let el=document.getElementById(id);
 el.style.display = el.style.display==="none"?"block":"none";
}

function limit(i){
 if(i.value>100)i.value=100;
 if(i.value<0)i.value=0;
}

async function convertMP3(){
 let pass=document.getElementById("pass").value;
 let file=document.getElementById("file").files[0];
 let err=document.getElementById("err");

 err.innerHTML="";

 if(!pass){err.innerHTML="اكتب الرقم السري";return;}
 if(!file){err.innerHTML="اختر ملف";return;}

 let form=new FormData();
 form.append("password",pass);
 form.append("file",file);

 let res=await fetch("/convert-mp3",{method:"POST",body:form});

 if(res.status==403){
   err.innerHTML="كلمة السر غير صحيحة";
   return;
 }

 let blob=await res.blob();
 let url=URL.createObjectURL(blob);

 let a=document.createElement("a");
 a.href=url;
 a.download="audio.mp3";
 a.click();
}

async function calc(){
 let total=0;

 for(let key in SUBJECTS){
   let v=document.getElementsByName(key)[0].value;
   if(v){
     v=Math.max(0,Math.min(100,parseFloat(v)));
     total+=v*SUBJECTS[key];
   }
 }

 total=Math.min(total/TOTAL,100);

 document.getElementById("resultValue").innerHTML=total.toFixed(2)+"%";
 document.getElementById("resultBox").style.display="flex";
}
</script>
</head>

<body>

<button onclick="toggle('mp3Box')">🔒 MP3</button>

<div id="mp3Box" class="box" style="display:none;">
<h3>تحويل MP3</h3>
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>
<input id="file" type="file" accept="audio/*,video/*">
<button onclick="convertMP3()">تحويل</button>
</div>

<button onclick="toggle('calcBox')">🧮 الحاسبة</button>

<div id="calcBox" class="box" style="display:none;">
<h3>حاسبة النسبة</h3>

{% for n,w in subjects.items() %}
{{n}} ({{w}}%)
<input name="{{n}}" type="number" oninput="limit(this)">
{% endfor %}

<button onclick="calc()">احسب</button>
</div>

<div id="resultBox" class="resultBox">
<div class="card">
<h2 id="resultValue"></h2>
<button onclick="document.getElementById('resultBox').style.display='none'">إغلاق</button>
</div>
</div>

<script>
const SUBJECTS = {{ subjects|tojson }};
const TOTAL = {{ total }};
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
    fid = str(uuid.uuid4())

    inp = f"{UPLOAD_DIR}/{fid}"
    out = f"{OUTPUT_DIR}/{fid}.mp3"

    f.save(inp)

    subprocess.run(
        ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return send_file(out, as_attachment=True, download_name="audio.mp3")

if __name__ == "__main__":
    app.run()
