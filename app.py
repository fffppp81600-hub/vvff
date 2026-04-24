from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess, io, tempfile
from PIL import Image, ImageOps
import img2pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 250 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MP3_PASSWORD = "7db"

SUBJECTS = {
    "رياضيات":14.63,"المواظبه":12.2,"لغتي":12.2,"الاسلاميه":12.2,
    "الانقليزي":9.76,"العلوم":9.76,"الاجتماعيات":7.32,
    "الفنيه":4.88,"مهارات رقميه":4.88,"بدنيه":4.88,
    "السلوك":2.44,"نشاط":2.44,"حياتيه":2.44
}
TOTAL_WEIGHT=sum(SUBJECTS.values())

HTML="""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rakan Tools</title>
<style>
body{font-family:Arial;background:#07080c;color:white;text-align:center;padding:18px}
.menu{max-width:520px;margin:10px auto 18px;display:flex;gap:8px}
.box{background:#171820;padding:24px;border-radius:24px;max-width:520px;margin:18px auto;display:none}
button{width:100%;padding:15px;margin-top:12px;border-radius:16px;border:0;background:#00f59b;font-weight:bold;font-size:16px}
input{width:100%;padding:14px;margin-top:10px;border-radius:14px;border:0;box-sizing:border-box;font-size:16px}
.error{color:#ff4d4d;margin-top:8px;font-weight:bold;display:none}
.status{margin-top:12px;color:#ccc;font-weight:bold}
.progress{height:14px;background:#333;margin-top:14px;border-radius:20px;overflow:hidden;display:none}
.bar{height:100%;width:0;background:#00f59b;transition:.25s}
.download{display:block;background:#00f59b;color:#000;padding:15px;border-radius:16px;text-decoration:none;font-weight:bold;margin-top:18px}
.subject{text-align:right;margin-top:10px}
.resultBox{position:fixed;inset:0;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center;z-index:9}
.card{background:#171820;padding:28px;border-radius:24px;width:85%;max-width:360px}
.big{font-size:34px;color:#00f59b;font-weight:bold}
</style>
<script>
function showBox(id){
 document.querySelectorAll('.box').forEach(b=>b.style.display='none');
 document.getElementById(id).style.display='block';
 window.scrollTo({top:0,behavior:'smooth'});
}
function limit(i){if(i.value>100)i.value=100;if(i.value<0)i.value=0;}
function closeResult(){document.getElementById("resultBox").style.display="none";}
window.onload=function(){showBox("{{active}}");}

async function convertMP3(){
 let form=new FormData();
 let pass=document.getElementById("mp3pass").value;
 let file=document.getElementById("mp3file").files[0];
 let err=document.getElementById("mp3err");
 let result=document.getElementById("mp3result");
 err.style.display="none"; result.innerHTML="";
 if(!pass){err.innerHTML="اكتب الرقم السري";err.style.display="block";return;}
 if(!file){err.innerHTML="اختر ملف صوت أو فيديو";err.style.display="block";return;}
 form.append("password",pass); form.append("file",file);
 result.innerHTML="<div class='status'>جاري التحويل...</div>";
 let res=await fetch("/convert-mp3",{method:"POST",body:form});
 if(res.status===403){err.innerHTML="كلمة السر غير صحيحة";err.style.display="block";result.innerHTML="";return;}
 if(!res.ok){err.innerHTML="فشل التحويل";err.style.display="block";result.innerHTML="";return;}
 let blob=await res.blob();
 let url=URL.createObjectURL(blob);
 result.innerHTML='<a class="download" href="'+url+'" download="converted.mp3">تنزيل MP3</a>';
}

async function convertPDF(){
 let files=document.getElementById("pdfFiles").files;
 let status=document.getElementById("pdfStatus");
 let progress=document.getElementById("pdfProgress");
 let bar=document.getElementById("pdfBar");
 let result=document.getElementById("pdfResult");

 if(files.length===0){status.innerHTML="اختر الصور أول";return;}

 let form=new FormData();
 for(let f of files){form.append("images",f);}

 result.innerHTML="";
 progress.style.display="block";
 bar.style.width="0%";

 let seconds=Math.max(15, files.length*2);
 let start=seconds;
 status.innerHTML="باقي تقريباً "+seconds+" ثانية";

 let timer=setInterval(()=>{
   seconds--;
   if(seconds<0)seconds=0;
   let done=((start-seconds)/start)*95;
   bar.style.width=done+"%";
   status.innerHTML= seconds>0 ? "باقي تقريباً "+seconds+" ثانية" : "ثواني ويجهز...";
 },1000);

 try{
   let res=await fetch("/images-to-pdf",{method:"POST",body:form});
   clearInterval(timer);

   if(!res.ok){
     let txt=await res.text();
     status.innerHTML="خطأ: "+txt;
     return;
   }

   let blob=await res.blob();
   let url=URL.createObjectURL(blob);
   bar.style.width="100%";
   status.innerHTML="جاهز ✅";
   result.innerHTML='<a class="download" href="'+url+'" download="images.pdf">تنزيل PDF</a>';
 }catch(e){
   clearInterval(timer);
   status.innerHTML="فشل الاتصال، جرّب تحديث الصفحة";
 }
}
</script>
</head>
<body>

<div class="menu">
<button onclick="showBox('mp3')">MP3</button>
<button onclick="showBox('pdf')">PDF</button>
<button onclick="showBox('grades')">النسبة</button>
</div>

<div id="mp3" class="box">
<h2>🔒 تحويل MP3</h2>
<input id="mp3pass" type="password" placeholder="الرقم السري">
<div id="mp3err" class="error"></div>
<input id="mp3file" type="file" accept="audio/*,video/*">
<button type="button" onclick="convertMP3()">تحويل</button>
<div id="mp3result"></div>
</div>

<div id="pdf" class="box">
<h2>⚡ تحويل صور إلى PDF</h2>
<input id="pdfFiles" type="file" accept="image/*" multiple>
<button type="button" onclick="convertPDF()">تحويل PDF</button>
<div id="pdfProgress" class="progress"><div id="pdfBar" class="bar"></div></div>
<div id="pdfStatus" class="status"></div>
<div id="pdfResult"></div>
</div>

<div id="grades" class="box">
<h2>حاسبة النسبة</h2>
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
    return render_template_string(HTML,subjects=SUBJECTS,total=None,active="pdf")

@app.route("/grades",methods=["POST"])
def grades():
    s=0
    for k,w in SUBJECTS.items():
        v=request.form.get(k)
        if v:
            v=max(0,min(float(v),100))
            s+=v*w
    total=min(s/TOTAL_WEIGHT,100)
    return render_template_string(HTML,subjects=SUBJECTS,total=round(total,2),active="grades")

@app.route("/convert-mp3",methods=["POST"])
def mp3():
    if request.form.get("password")!=MP3_PASSWORD:
        return "wrong password",403

    f=request.files.get("file")
    if not f:
        return "no file",400

    fid=str(uuid.uuid4())
    inp=os.path.join(UPLOAD_DIR,fid)
    out=os.path.join(OUTPUT_DIR,fid+".mp3")
    f.save(inp)

    try:
        r=subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if r.returncode!=0:
            raise Exception()
    except:
        subprocess.run(["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    finally:
        if os.path.exists(inp):
            os.remove(inp)

    return send_file(out,as_attachment=True,download_name="converted.mp3",mimetype="audio/mpeg")

@app.route("/images-to-pdf",methods=["POST"])
def pdf():
    files=request.files.getlist("images")
    if not files:
        return "مافي صور",400

    try:
        temp_paths=[]

        with tempfile.TemporaryDirectory() as tmp:
            for i,f in enumerate(files):
                img=Image.open(f.stream)
                img=ImageOps.exif_transpose(img)

                path=os.path.join(tmp,f"{i}.jpg")
                img.convert("RGB").save(path,"JPEG",quality=95,optimize=False)
                temp_paths.append(path)

            pdf_bytes=img2pdf.convert(temp_paths)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="images.pdf"
        )

    except Exception as e:
        return "فشل التحويل: الصور ثقيلة جدًا أو الصيغة غير مدعومة",500

if __name__=="__main__":
    app.run()
