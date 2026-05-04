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
body{
  font-family:-apple-system;
  background:#0b0c10;
  color:white;
  padding:20px;
}
.box{
  background:#181820;
  padding:20px;
  border-radius:20px;
  margin-top:10px;
}
input{
  width:100%;
  padding:12px;
  margin-top:10px;
  border-radius:12px;
  border:none;
}
button{
  width:100%;
  padding:12px;
  margin-top:10px;
  border-radius:12px;
  border:none;
  background:#00f59b;
  font-weight:bold;
}
.error{color:red}
.progress{height:6px;background:#222;margin-top:10px}
.bar{height:100%;width:0;background:#00f59b}
</style>
</head>

<body>

<h2>تحويل MP3</h2>

<div class="box">
<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>

<!-- 🔥 هنا التعديل -->
<input id="file" type="file">

<button onclick="convertMP3()">تحويل</button>

<div class="progress"><div id="bar" class="bar"></div></div>
</div>

<script>
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
    return render_template_string(HTML)

@app.route("/convert-mp3", methods=["POST"])
def convert():
    if request.form.get("password") != PASSWORD:
        return "wrong", 403

    f = request.files.get("file")
    fid = str(uuid.uuid4())

    inp = f"{UPLOAD_DIR}/{fid}"
    out = f"{OUTPUT_DIR}/{fid}.mp3"
    f.save(inp)

    try:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
        )
    except:
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame",
             "-b:a","96k","-threads","4","-preset","ultrafast",out],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
        )

    return send_file(out, as_attachment=True, download_name="audio.mp3")

if __name__ == "__main__":
    app.run()
