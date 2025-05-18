import os
import time
import subprocess
from gtts import gTTS

def text_to_audio(folder):
    print("TTA -", folder)
    desc_path = f"user_uploads/{folder}/desc.txt"
    audio_path = f"user_uploads/{folder}/audio.mp3"

    if not os.path.exists(desc_path):
        print(f"Missing desc.txt in {folder}")
        return

    # Fixed: Use cp1252 to avoid UnicodeDecodeError from Windows-encoded files
    with open(desc_path, "r", encoding="cp1252") as f:
        text = f.read().strip()
        print("Text:", text)

    if text:
        tts = gTTS(text)
        tts.save(audio_path)
        print(f"Audio saved to {audio_path}")
    else:
        print("Empty desc.txt")

def create_input_txt(folder):
    folder_path = os.path.join("user_uploads", folder)
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))])

    if not image_files:
        print(f"No images found in {folder}")
        return

    input_path = os.path.join(folder_path, "input.txt")
    with open(input_path, "w", encoding="utf-8") as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write("duration 2\n")
        f.write(f"file '{image_files[-1]}'\n")  # Last image shown until audio ends
    print(f"input.txt created in {folder}")

def create_reel(folder):
    input_txt_path = f"user_uploads/{folder}/input.txt"
    audio_path = f"user_uploads/{folder}/audio.mp3"
    output_path = f"static/reels/{folder}.mp4"

    # Ensure paths with backslashes are properly escaped or use raw strings
    command = f'''ffmpeg -y -f concat -safe 0 -i "{input_txt_path}" -i "{audio_path}" \
-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p "{output_path}"'''

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Reel created: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error in folder {folder}:\n{e}")

def main_loop():
    os.makedirs("user_uploads", exist_ok=True)
    os.makedirs("static/reels", exist_ok=True)
    open("done.txt", "a").close()

    while True:
        print("Processing queue...")
        with open("done.txt", "r") as f:
            done_folders = [line.strip() for line in f]

        folders = os.listdir("user_uploads")
        folders = [f for f in folders if os.path.isdir(os.path.join("user_uploads", f))]

        for folder in folders:
            if folder not in done_folders:
                create_input_txt(folder)
                text_to_audio(folder)
                create_reel(folder)

                with open("done.txt", "a") as f:
                    f.write(folder + "\n")

        time.sleep(4)

if __name__ == "__main__":
    main_loop()
