from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

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
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:20px}
.box{background:#181820;padding:20px;border-radius:20px;max-width:400px;margin:auto;margin-top:15px}
input,button{width:100%;padding:12px;margin-top:8px;border-radius:12px;border:0}
button{background:#00ff99;font-weight:bold}
.error{color:red;margin-top:5px}
.resultBox{position:fixed;inset:0;background:#000a;display:flex;align-items:center;justify-content:center}
.card{background:#181820;padding:20px;border-radius:20px}
</style>

<script>
function limit(i){
 if(i.value>100)i.value=100;
 if(i.value<0)i.value=0;
}

function closeResult(){
 document.getElementById("r").style.display="none";
}

async function convertMP3(){
 let pass=document.getElementById("pass").value;
 let file=document.getElementById("file").files[0];
 let err=document.getElementById("err");
 let resBox=document.getElementById("res");

 err.innerHTML="";
 resBox.innerHTML="";

 if(!pass){err.innerHTML="اكتب الرقم السري";return;}
 if(!file){err.innerHTML="اختر ملف";return;}

 let form=new FormData();
 form.append("password",pass);
 form.append("file",file);

 let res=await fetch("/convert-mp3",{method:"POST",body:form});

 if(res.status==403){
   err.innerHTML="كلمة السر غلط";
   return;
 }

 let blob=await res.blob();
 let url=URL.createObjectURL(blob);

 resBox.innerHTML=`<a href="${url}" download="converted.mp3">تحميل MP3</a>`;
}
</script>
</head>

<body>

<div class="box">
<h3>🔒 تحويل MP3</h3>
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>
<input id="file" type="file" accept="audio/*,video/*">
<button onclick="convertMP3()">تحويل</button>
<div id="res"></div>
</div>

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
<div id="r" class="resultBox">
<div class="card">
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
    return render_template_string(HTML, subjects=SUBJECTS, total=None)

@app.route("/grades", methods=["POST"])
def grades():
    s=0
    for k,w in SUBJECTS.items():
        v=request.form.get(k)
        if v:
            v=max(0,min(float(v),100))
            s+=v*w

    total=min(s/TOTAL_WEIGHT,100)
    return render_template_string(HTML, subjects=SUBJECTS, total=round(total,2))

@app.route("/convert-mp3", methods=["POST"])
def mp3():
    if request.form.get("password")!=MP3_PASSWORD:
        return "wrong",403

    f=request.files.get("file")
    fid=str(uuid.uuid4())
    inp=f"{UPLOAD_DIR}/{fid}"
    out=f"{OUTPUT_DIR}/{fid}.mp3"
    f.save(inp)

    try:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
        )
    except:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
        )

    return send_file(out, as_attachment=True, download_name="converted.mp3")

if __name__=="__main__":
    app.run()
