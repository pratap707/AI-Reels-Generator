from gtts import gTTS
import os
import uuid

def text_to_speech_file(text: str, folder: str) -> str:
    os.makedirs(f"user_uploads/{folder}", exist_ok=True)
    file_name = f"audio_{uuid.uuid4().hex}.mp3"
    save_file_path = os.path.join(f"user_uploads/{folder}", file_name)

    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(save_file_path)
        print(f"{save_file_path}: A new audio file was saved successfully!")
    except Exception as e:
        print("❌ Error during text-to-speech:", e)

    return save_file_path

# Test it
#text_to_speech_file("Hello! This is a test using gTTS.", "cc61e79d-30e8-11f0-997a-e4b97a2e502d")
