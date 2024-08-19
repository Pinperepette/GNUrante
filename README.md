# GNUrante

**GNUrante** is a Python script that simplifies the process of downloading YouTube, X etc ... videos, extracting and cleaning audio, transcribing and translating the audio into Italian, and finally adding subtitles to the video. The script automates these complex tasks, making it easy for anyone to generate videos with subtitles.

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

\`\`\`bash
pip install yt-dlp moviepy librosa noisereduce soundfile whisper langid translate nltk ffmpeg-python
\`\`\`

Additionally, make sure `ffmpeg` is installed on your system. You can install it via package managers like `apt` on Linux, `brew` on macOS, or download it from [ffmpeg.org](https://ffmpeg.org/download.html).

## Usage

To use GNUrante, simply provide the URL of the YouTube video as a command-line argument:

\`\`\`bash
python gnurante.py <video_url>
\`\`\`

The script will:

1. Download the video.
2. Extract and clean the audio.
3. Transcribe and translate the audio.
4. Generate subtitles.
5. Add subtitles to the video.
6. Cleanup all temporary files.

The final video with subtitles will be saved as `video_con_sottotitoli.mp4` in the current directory.

## Example

\`\`\`bash
python gnurante.py https://www.youtube.com/watch?v=example
\`\`\`

After the script completes, you'll find a new file named `video_con_sottotitoli.mp4` in your directory.

## License

GNUrante is released under the MIT License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
