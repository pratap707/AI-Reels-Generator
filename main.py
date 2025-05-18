from flask import Flask, render_template, request
import uuid
import os
from werkzeug.utils import secure_filename
from gtts import gTTS
import subprocess

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSION = {'jpg', 'jpeg', 'png'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid4())
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        input_files = []

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(folder_path, exist_ok=True)

        for key, file in request.files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
                input_files.append(filename)

        # Save description
        with open(os.path.join(folder_path, "desc.txt"), "w") as f:
            f.write(desc)

        # Save input.txt
        with open(os.path.join(folder_path, "input.txt"), "w") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\n")
                f.write("duration 2\n")
            if input_files:
                f.write(f"file '{input_files[-1]}'\n")

        # Generate audio and reel
        text_to_audio(rec_id)
        create_reel(rec_id)

        # Mark as done
        with open("done.txt", "a") as f:
            f.write(rec_id + "\n")

    return render_template("create.html", myid=myid)

def text_to_audio(folder):
    desc_path = f"user_uploads/{folder}/desc.txt"
    audio_path = f"user_uploads/{folder}/audio.mp3"

    if not os.path.exists(desc_path):
        return

    with open(desc_path, "r", encoding="cp1252") as f:
        text = f.read().strip()

    if text:
        tts = gTTS(text)
        tts.save(audio_path)

def create_reel(folder):
    input_txt_path = f"user_uploads/{folder}/input.txt"
    audio_path = f"user_uploads/{folder}/audio.mp3"
    output_path = f"static/reels/{folder}.mp4"

    command = f'''ffmpeg -y -f concat -safe 0 -i "{input_txt_path}" -i "{audio_path}" \
-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p "{output_path}"'''

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

@app.route("/gallery")
def gallery():
    reels_folder = "static/reels"
    os.makedirs(reels_folder, exist_ok=True)  # Ensure it exists
    reels = [f for f in os.listdir(reels_folder) if f.endswith('.mp4')]
    return render_template("gallery.html", reels=reels)


app.run(debug=True)