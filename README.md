# GNUrante

**GNUrante** is a Python script that simplifies the process of downloading YouTube, X etc ... videos, extracting and cleaning audio, transcribing and translating the audio into Italian, and finally adding subtitles to the video. The script automates these complex tasks, making it easy for anyone to generate videos with subtitles.

![GNUrante Logo](./gnurante-logo.png)


## Features

- **Video Download**: Downloads videos from YouTube using `yt-dlp`.
- **Audio Processing**: Extracts audio from the video and reduces noise using `librosa` and `noisereduce`.
- **Transcription**: Automatically transcribes the cleaned audio using OpenAI's `whisper`.
- **Translation**: Detects the language of the transcription and translates it into Italian.
- **Subtitle Creation**: Generates subtitles in SRT format, synchronized with the video duration.
- **Video Subtitling**: Adds the subtitles to the video using `ffmpeg`.
- **Cleanup**: Removes all temporary files after the final video with subtitles is created.

## Dependencies

To run GNUrante, you'll need the following Python libraries:

- **yt-dlp**: For downloading videos from YouTube.
- **moviepy**: For handling video and audio files.
- **librosa**: For audio processing and noise reduction.
- **noisereduce**: For reducing noise in audio files.
- **soundfile**: For saving processed audio files.
- **whisper**: For automatic transcription of audio.
- **langid**: For detecting the language of the transcription.
- **translate**: For translating text from one language to another.
- **nltk**: For sentence tokenization when creating subtitles.
- **ffmpeg**: For adding subtitles to the video.

You can install all dependencies using pip:

```bash
pip install yt-dlp moviepy librosa noisereduce soundfile whisper langid translate nltk ffmpeg-python
```
or
```bash
pip install -r requirements.txt
```

Additionally, make sure `ffmpeg` is installed on your system. You can install it via package managers like `apt` on Linux, `brew` on macOS, or download it from [ffmpeg.org](https://ffmpeg.org/download.html).

## Usage

To use GNUrante, simply provide the URL of the YouTube video as a command-line argument:

```bash
python gnurante.py <video_url>
```

The script will:

1. Download the video.
2. Extract and clean the audio.
3. Transcribe and translate the audio.
4. Generate subtitles.
5. Add subtitles to the video.
6. Cleanup all temporary files.

The final video with subtitles will be saved as `video_con_sottotitoli.mp4` in the current directory.

## Example

```bash
python gnurante.py https://x.com/{user}/status/{number}
```

After the script completes, you'll find a new file named `video_con_sottotitoli.mp4` in your directory.

## Customizing Subtitle Language

By default, GNUrante generates subtitles in Italian. However, you can easily customize the script to create subtitles in any language supported by the translation service.

### How to Change the Subtitle Language

To change the subtitle language, simply modify the following line in the script:

translator = Translator(to_lang="it", from_lang=language)

- `to_lang="it"`: Change `"it"` to the code of your desired language (e.g., `"en"` for English, `"es"` for Spanish, `"fr"` for French, etc.).
- `from_lang=language`: This detects the original language of the video. You can leave this unchanged to automatically detect the source language.

### Example settings Language

If you want to generate subtitles in English instead of Italian, you would modify the line as follows:

translator = Translator(to_lang="en", from_lang=language)

After making this change, the script will generate subtitles in English.

This flexibility allows you to generate subtitles in any language supported by the translation service, making GNUrante a versatile tool for a global audience.


## License

GNUrante is released under the MIT License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
