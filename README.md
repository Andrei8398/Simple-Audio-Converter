# Simple Audio Converter

A Python-based GUI application that allows users to easily batch-convert audio files between various formats (MP3, AAC, WAV, OGG, WMA, FLAC, ALAC) with granular control over bitrates and quality.

## Features
* **Batch Processing:** Convert multiple files at once.
* **Granular Options:** Choose between CBR, VBR, and ABR bitrates.
* **Silence Removal:** Automatically trim silence from the start or end of audio tracks.
* **Real-time Log:** View FFmpeg conversion progress in real-time within the app.

## Prerequisites
This application uses `tkinter` (which comes pre-installed with standard Python) and requires **FFmpeg**.

1. Install Python 3.x
2. Download [FFmpeg](https://ffmpeg.org/download.html).
3. Place `ffmpeg.exe` in the exact same folder as the `convertor_audio.py` script (or add it to your system PATH).

## How to Run
Open your terminal or command prompt in the project folder and run:
`python convertor_audio.py`
