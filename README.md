# Waver v1.1

Waver is a modern desktop application for downloading and converting YouTube videos to audio files (WAV, MP3) or video files (MP4) with advanced features including automatic BPM and key detection.

## 🎵 Features

- **Audio Downloads**: Convert YouTube videos to WAV or MP3 with quality options
- **Video Downloads**: Download MP4 videos with resolution selection (480p to 4K)
- **Audio Analysis**: Automatic BPM (tempo) and key signature detection
- **Smart Settings**: Remembers download location, format preferences, and analysis settings
- **Modern UI**: Clean, responsive interface with light/dark mode support
- **Batch Processing**: Download multiple files with progress tracking

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg (included in the package)

### Setup
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python Waver.py
   ```

## 📋 Requirements

- PyQt6
- yt-dlp
- librosa (for audio analysis)
- numpy
- scipy

## 🎛️ Usage

1. **Paste YouTube URL**: Copy a YouTube link and paste it into the URL field
2. **Select Format**: Choose between WAV, MP3 (audio) or MP4 (video)
3. **Set Quality**: Select bitrate for audio or resolution for video
4. **Download**: Click download and monitor progress
5. **Analyze**: Enable auto-analysis or manually analyze downloaded audio files

## 🔧 Options

- **Auto-Analyze Key and BPM**: Automatically analyze downloaded audio files
- **Open Folder After Download**: Automatically open download folder
- **Light/Dark Mode**: Toggle between themes
- **Custom Download Location**: Set your preferred download directory

## 📝 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 🤝 Contributing

Feel free to provide feedback and request new or improved features.
Please report any issues to catwarez@proton.me

## 📄 License

This project is open source. Feel free to modify and distribute.

---

**Enjoy making music with Waver!** 🎵✨
