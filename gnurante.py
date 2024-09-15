#!/usr/bin/env python

import os
import sys
from concurrent.futures import ThreadPoolExecutor
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
import argparse

class VideoProcessor:
    def __init__(self, video_url, resolution=None, gpu_type=None):
        """
        Inizializza l'oggetto VideoProcessor.
        
        :param video_url: URL del video YouTube da processare
        :param resolution: Risoluzione desiderata per il video di output (opzionale)
        :param gpu_type: Tipo di GPU da utilizzare per l'encoding ('nvidia', 'amd', o None per CPU)
        """
        self.video_url = video_url
        self.resolution = resolution
        self.gpu_type = gpu_type
        self.file_names = {
            'video': "video.mp4",
            'audio': "audio.wav",
            'cleaned_audio': "cleaned_audio.wav",
            'transcription': "trascrizione_completa.txt",
            'translation': "traduzione_completa.txt",
            'srt': "sottotitoli.srt",
            'output_video': "video_con_sottotitoli.mp4"
        }

    def download_video(self):
        """
        Scarica il video YouTube utilizzando yt-dlp.
        Seleziona il formato migliore disponibile e gestisce eventuali errori durante il download.
        """
        ydl_opts = {
            'outtmpl': self.file_names['video'],
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4'
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(self.video_url, download=False)
                formats = info.get('formats', [])
                best_format = max(formats, key=lambda f: f.get('height', 0) if f.get('acodec') != 'none' and f.get('vcodec') != 'none' else 0)
                print(f"Scaricamento del video alla risoluzione: {best_format.get('height', 'sconosciuta')}p")
                ydl.download([self.video_url])
                print(f"Video scaricato con successo: {self.file_names['video']}")
            except Exception as e:
                print(f"Errore nel download del video: {e}")
                sys.exit(1)

    def extract_and_clean_audio(self):
        """
        Estrae l'audio dal video scaricato e applica la riduzione del rumore.
        Utilizza moviepy per l'estrazione dell'audio e noisereduce per la pulizia.
        """
        with VideoFileClip(self.file_names['video']) as video:
            video.audio.write_audiofile(self.file_names['audio'])

        audio_data, rate = librosa.load(self.file_names['audio'], sr=None)
        reduced_noise = nr.reduce_noise(y=audio_data, sr=rate, prop_decrease=0.5, stationary=True)
        sf.write(self.file_names['cleaned_audio'], reduced_noise, rate)

    def transcribe_audio(self):
        """
        Trascrive l'audio pulito utilizzando il modello Whisper.
        Salva la trascrizione in un file di testo e memorizza i segmenti per l'uso successivo.
        """
        model = whisper.load_model("large")
        result = model.transcribe(self.file_names['cleaned_audio'], verbose=True)

        with open(self.file_names['transcription'], "w", encoding="utf-8") as file:
            file.write(result['text'])
        
        self.segments = result['segments']
        print("Trascrizione completata con successo!")

    def translate_text(self):
        """
        Traduce il testo trascritto in italiano.
        Utilizza langid per rilevare la lingua di origine e translate per la traduzione.
        Esegue la traduzione in parallelo utilizzando ThreadPoolExecutor.
        """
        with open(self.file_names['transcription'], 'r', encoding="utf-8") as file:
            text_content = file.read()

        language, _ = langid.classify(text_content)
        translator = Translator(to_lang="it", from_lang=language)

        with ThreadPoolExecutor() as executor:
            sentences = list(executor.map(translator.translate, [segment['text'] for segment in self.segments]))

        translated_text = " ".join(sentences)
        with open(self.file_names['translation'], 'w', encoding="utf-8") as file:
            file.write(translated_text)

        for segment, translated in zip(self.segments, sentences):
            segment['translated_text'] = translated

        print("Traduzione completata con successo!")

    def create_srt_file(self):
        """
        Crea un file di sottotitoli in formato SRT utilizzando i segmenti tradotti.
        """
        with open(self.file_names['srt'], 'w', encoding="utf-8") as f:
            for i, segment in enumerate(self.segments, 1):
                f.write(f"{i}\n")
                f.write(f"{self.format_time(segment['start'])} --> {self.format_time(segment['end'])}\n")
                f.write(f"{segment['translated_text']}\n\n")

    def add_subtitles_to_video(self):
        """
        Aggiunge i sottotitoli al video utilizzando ffmpeg.
        Se specificato, ridimensiona il video alla risoluzione desiderata.
        Utilizza l'accelerazione GPU se specificata.
        """
        input_video = ffmpeg.input(self.file_names['video'])
        
        if self.resolution:
            width, height = map(int, self.resolution.split('x'))
            video = input_video.video.filter('scale', width, height)
        else:
            video = input_video.video
        
        audio = input_video.audio
        
        video = video.filter('subtitles', self.file_names['srt'])
        
        output_args = {
            'acodec': 'aac',  # Specifica il codec audio
            'strict': 'experimental'  # Necessario per alcuni codec audio
        }
        
        if self.gpu_type == 'nvidia':
            output_args['vcodec'] = 'h264_nvenc'
            output_args['preset'] = 'slow'
            output_args['crf'] = '23'
        elif self.gpu_type == 'amd':
            output_args['vcodec'] = 'h264_amf'
            output_args['quality'] = 'balanced'
            output_args['usage'] = 'transcoding'
        else:
            # Use CPU encoding if no GPU is specified
            output_args['vcodec'] = 'libx264'
            output_args['preset'] = 'medium'
            output_args['crf'] = '23'
        
        output = ffmpeg.output(video, audio, self.file_names['output_video'], **output_args)
        
        ffmpeg.run(output)
        
        print(f"Video con sottotitoli salvato come {self.file_names['output_video']}")


    def clean_up(self):
        """
        Rimuove i file temporanei creati durante il processo.
        """
        for file in self.file_names.values():
            if file != self.file_names['output_video'] and os.path.exists(file):
                os.remove(file)

    @staticmethod
    def format_time(seconds):
        """
        Formatta il tempo in secondi nel formato SRT (HH:MM:SS,mmm).
        
        :param seconds: Tempo in secondi
        :return: Stringa formattata nel formato SRT
        """
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

def main():
    """
    Funzione principale che gestisce l'intero processo di elaborazione del video.
    Analizza gli argomenti della riga di comando, inizializza il processore video e esegue tutti i passaggi.
    """
    parser = argparse.ArgumentParser(description="Processa un video YouTube con sottotitoli tradotti.")
    parser.add_argument("video_url", help="URL del video YouTube da processare")
    parser.add_argument("--resolution", help="Risoluzione finale del video (es. 1280x720)")
    parser.add_argument("--gpu", choices=['nvidia', 'amd', 'cpu'], default='cpu', 
                        help="Tipo di GPU da utilizzare per l'encoding (nvidia, amd) o CPU")
    
    args = parser.parse_args()

    gpu_type = None if args.gpu == 'cpu' else args.gpu
    print(f"Utilizzo {'accelerazione GPU ' + args.gpu.upper() if gpu_type else 'CPU'} per l'encoding.")

    nltk.download('punkt', quiet=True)
    processor = VideoProcessor(args.video_url, args.resolution, gpu_type)

    steps = [
        processor.download_video,
        processor.extract_and_clean_audio,
        processor.transcribe_audio,
        processor.translate_text,
        processor.create_srt_file,
        processor.add_subtitles_to_video,
        processor.clean_up
    ]

    for step in steps:
        step()

if __name__ == "__main__":
    main()
