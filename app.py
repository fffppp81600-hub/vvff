from flask import Flask, request, send_file, render_template_string
import os, uuid, subprocess
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Converter</title>
<style>
body{font-family:Arial;background:#0b0b0f;color:white;text-align:center;padding:35px}
.box{background:#181820;padding:25px;border-radius:22px;max-width:450px;margin:20px auto}
input,button{width:100%;padding:15px;margin-top:15px;border-radius:14px;border:0}
button{background:#00ff99;font-weight:bold;font-size:16px;cursor:pointer}
p{color:#aaa}
hr{border:1px solid #333}
</style>
</head>
<body>

<div class="box">
<h1>MP3 Converter</h1>
<p>حوّل فيديو/صوت إلى MP3</p>
<form action="/convert-mp3" method="post" enctype="multipart/form-data">
<input type="file" name="file" required>
<button type="submit">تحويل MP3</button>
</form>
</div>

<div class="box">
<h1>Images to PDF</h1>
<p>حوّل صورة أو أكثر إلى PDF</p>
<form action="/images-to-pdf" method="post" enctype="multipart/form-data">
<input type="file" name="images" accept="image/*" multiple required>
<button type="submit">تحويل PDF</button>
</form>
</div>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/convert-mp3", methods=["POST"])
def convert_mp3():
    file = request.files.get("file")
    if not file or file.filename == "":
        return "اختر ملف أول", 400

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)
    output_path = os.path.join(OUTPUT_DIR, file_id + ".mp3")

    file.save(input_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-b:a", "192k",
        "-threads", "2",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        return "الملف ما فيه صوت أو صيغته ما تنفع", 400
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    return send_file(output_path, as_attachment=True, download_name="converted.mp3")

@app.route("/images-to-pdf", methods=["POST"])
def images_to_pdf():
    files = request.files.getlist("images")
    if not files:
        return "اختر صورة أو أكثر", 400

    file_id = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_DIR, file_id + ".pdf")

    images = []

    try:
        for file in files:
            if file.filename == "":
                continue

            img = Image.open(file.stream)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            else:
                img = img.convert("RGB")

            images.append(img)

        if not images:
            return "مافي صور صالحة", 400

        first_image = images[0]
        other_images = images[1:]

        first_image.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=other_images
        )

    except:
        return "فشل تحويل الصور إلى PDF", 400

    return send_file(output_path, as_attachment=True, download_name="images.pdf")

if __name__ == "__main__":
    app.run()