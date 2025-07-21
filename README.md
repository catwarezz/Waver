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

### Option 1: Windows Installer (Recommended)
1. Download `WaverInstaller_v1.1.0.exe` from the [Releases](https://github.com/catwarezz/Waver/releases) page
2. Run the installer as administrator
3. Follow the installation wizard
4. The installer will automatically download FFmpeg during installation
5. Launch Waver from the Start Menu or Desktop shortcut

### Option 2: Portable Version
1. Download `Waver_v1.1.0_Portable.zip` from the [Releases](https://github.com/catwarezz/Waver/releases) page
2. Extract to any folder
3. Run `Waver.exe`
4. No installation required - run from anywhere!

### Option 3: From Source (Developers)

#### Prerequisites
- Python 3.8 or higher
- Git (optional)

#### Quick Setup
```bash
# Clone the repository
git clone https://github.com/catwarezz/Waver.git
cd Waver

# Run the automated setup script
python build_setup.py
```

#### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download FFmpeg (Windows only)
python setup.py --download-ffmpeg

# Run the application
python Waver.py
```

#### Building Your Own Installer
```bash
# Install NSIS (https://nsis.sourceforge.io/)
# Then run the build script
build_installer.bat
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
