from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

PASSWORD = "7db"

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="UTF-8">
<title>MP3 Fast</title>

<style>
body{
  margin:0;
  font-family:-apple-system;
  background:#07080c;
  color:white;
  display:flex;
  justify-content:center;
  align-items:center;
  height:100vh;
}
.card{
  background:#171820;
  padding:25px;
  border-radius:28px;
  width:90%;
  max-width:420px;
}
input,button{
  width:100%;
  padding:14px;
  margin-top:12px;
  border-radius:16px;
  border:none;
}
button{
  background:#00f59b;
  font-weight:bold;
}
.error{
  color:red;
  margin-top:8px;
  display:none;
}
.status{
  margin-top:10px;
  color:#aaa;
}
a{
  display:block;
  margin-top:15px;
  background:#00f59b;
  color:black;
  padding:14px;
  border-radius:16px;
  text-decoration:none;
  font-weight:bold;
}
</style>
</head>

<body>

<div class="card">

<h2>🔒 تحويل MP3</h2>

<input id="pass" type="password" placeholder="الرقم السري">
<div id="err" class="error"></div>

<input id="file" type="file" accept="audio/*,video/*">

<button onclick="go()">تحويل</button>

<div id="status" class="status"></div>
<div id="result"></div>

</div>

<script>
async function go(){
  let pass=document.getElementById("pass").value;
  let file=document.getElementById("file").files[0];
  let err=document.getElementById("err");
  let status=document.getElementById("status");
  let result=document.getElementById("result");

  err.style.display="none";
  result.innerHTML="";

  if(!pass){
    err.innerHTML="اكتب الرقم السري";
    err.style.display="block";
    return;
  }

  if(!file){
    err.innerHTML="اختر ملف";
    err.style.display="block";
    return;
  }

  let form=new FormData();
  form.append("password",pass);
  form.append("file",file);

  status.innerHTML="جاري التحويل...";

  let res=await fetch("/convert",{method:"POST",body:form});

  if(res.status===403){
    err.innerHTML="كلمة السر غير صحيحة";
    err.style.display="block";
    status.innerHTML="";
    return;
  }

  if(!res.ok){
    err.innerHTML="فشل التحويل";
    err.style.display="block";
    status.innerHTML="";
    return;
  }

  let blob=await res.blob();
  let url=URL.createObjectURL(blob);

  status.innerHTML="جاهز ✅";

  result.innerHTML=`<a href="${url}" download="audio.mp3" onclick="alert('بدأ التنزيل ✅')">تنزيل MP3</a>`;
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return HTML

@app.route("/convert", methods=["POST"])
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
        # سريع جداً بدون إعادة ترميز
        r = subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","copy",out],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if r.returncode != 0:
            raise Exception()
    except:
        # fallback لو ما ينفع copy
        subprocess.run(
            ["ffmpeg","-y","-i",inp,"-vn","-acodec","libmp3lame","-b:a","128k",out],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    finally:
        if os.path.exists(inp):
            os.remove(inp)

    return send_file(out, as_attachment=True, download_name="audio.mp3")

if __name__ == "__main__":
    app.run()
