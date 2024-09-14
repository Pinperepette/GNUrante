#!/usr/bin/env python

import os
import sys
import shutil
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
import noisereduce as nr
import librosa
import soundfile as sf
import whisper
import langid
from translate import Translator
import ffmpeg
import nltk


class VideoProcessor:
    def __init__(self, video_url):
        self.video_url = video_url
        self.video_file = "video.mp4"
        self.audio_file = "audio.wav"
        self.cleaned_audio_file = "cleaned_audio.wav"
        self.transcription_file = "trascrizione_completa.txt"
        self.translation_file = "traduzione_completa.txt"
        self.srt_file = "sottotitoli.srt"
        self.output_video_file = "video_con_sottotitoli.mp4"

    def download_video(self):
        ydl_opts = {
            'outtmpl': self.video_file,
            'format': 'best',
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(self.video_url, download=True)
                print(f"Video scaricato con successo: {self.video_file}")
            except Exception as e:
                print(f"Errore nel download del video: {e}")
                sys.exit(1)

    def extract_and_clean_audio(self):
        video = VideoFileClip(self.video_file)
        video.audio.write_audiofile(self.audio_file)

        audio_data, rate = librosa.load(self.audio_file, sr=None)
        reduced_noise = nr.reduce_noise(y=audio_data, sr=rate, prop_decrease=0.5, stationary=True)
        sf.write(self.cleaned_audio_file, reduced_noise, rate)

    def transcribe_audio(self):
        model = whisper.load_model("large")
        result = model.transcribe(self.cleaned_audio_file, verbose=True)

        text = result['text']
        with open(self.transcription_file, "w", encoding="utf-8") as file:
            file.write(text)
        
        self.segments = result['segments']
        print("Trascrizione completata con successo!")

    def translate_text(self):
        with open(self.transcription_file, 'r', encoding="utf-8") as file:
            text_content = file.read()

        language, confidence = langid.classify(text_content)
        print(f"Language detected: {language} with confidence: {confidence}")

        translator = Translator(to_lang="it", from_lang=language)

        sentences = [translator.translate(segment['text']) for segment in self.segments]

        translated_text = " ".join(sentences)

        with open(self.translation_file, 'w', encoding="utf-8") as file:
            file.write(translated_text)

        for i, segment in enumerate(self.segments):
            self.segments[i]['translated_text'] = sentences[i]

        print("Traduzione completata con successo!")

    def create_srt_file(self):
        with open(self.srt_file, 'w', encoding="utf-8") as f:
            for i, segment in enumerate(self.segments):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['translated_text']

                start_time_formatted = self.format_time(start_time)
                end_time_formatted = self.format_time(end_time)

                f.write(f"{i + 1}\n")
                f.write(f"{start_time_formatted} --> {end_time_formatted}\n")
                f.write(f"{text}\n\n")

    def add_subtitles_to_video(self):
        ffmpeg.input(self.video_file).output(self.output_video_file, vf=f"subtitles={self.srt_file}").run()
        print(f"Video con sottotitoli salvato come {self.output_video_file}")

    def clean_up(self):
        files_to_delete = [
            self.video_file,
            self.audio_file,
            self.cleaned_audio_file,
            self.transcription_file,
            self.translation_file,
            self.srt_file
        ]

        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)

    @staticmethod
    def format_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python gnurante.py <video_url>")
        sys.exit(1)

    video_url = sys.argv[1]
    nltk.download('punkt')

    processor = VideoProcessor(video_url)
    processor.download_video()
    processor.extract_and_clean_audio()
    processor.transcribe_audio()
    processor.translate_text()
    processor.create_srt_file()
    processor.add_subtitles_to_video()
    processor.clean_up()


if __name__ == "__main__":
    main()
