import os
import subprocess
import tempfile
from moviepy.video.io.VideoFileClip import VideoFileClip
import whisper
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def extract_audio(video_path: str, audio_path: str):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, logger=None)

def transcribe_audio(audio_path: str, model_size: str = "base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]

def write_pdf(text: str, pdf_path: str):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    lines = text.split("\n")
    for line in lines:
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= 12  # interligne
    c.save()

def main():
    video_file = "10signesquiprouventquevousnetespasfaitlunpourlautre.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        audio_file = os.path.join(tmp, "extrait.wav")
        print("1️⃣ Extraction de l’audio…")
        extract_audio(video_file, audio_file)

        print("2️⃣ Transcription avec Whisper…")
        transcription = transcribe_audio(audio_file, model_size="small")

        output_pdf = "transcription_video.pdf"
        print(f"3️⃣ Écriture du PDF → {output_pdf}")
        write_pdf(transcription, output_pdf)

    print("✅ Terminé !")

if __name__ == "__main__":
    main()
