# Waver v1.1.0 Release

## 🎉 What's New in v1.1.0

### 🎵 Major New Features
- **Audio Analysis**: Automatic BPM and key signature detection for downloaded audio files
- **Video Downloads**: Full MP4 video download support with quality options (480p to 4K)
- **Smart Settings**: Enhanced settings persistence and dynamic download folder detection

### 🔧 Technical Improvements
- **PyQt6 Migration**: Complete upgrade from PyQt5 for better compatibility and performance
- **Async Processing**: Background operations for smoother UI experience
- **Enhanced UI**: Modern styling, better responsiveness, and improved user experience

## 📦 Installation

### Quick Start
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python Waver.py
   ```

### System Requirements
- Python 3.8 or higher
- Windows 10/11 (tested)
- FFmpeg (included in package)

## 🚀 Key Features

### Audio Downloads
- Convert YouTube videos to WAV or MP3
- Quality options: 128k, 192k, 256k, 320k
- Automatic audio analysis (BPM + Key detection)

### Video Downloads
- Download MP4 videos with resolution selection
- Quality options: 480p, 720p, 1080p, 1440p, 2160p (4K)
- Maintains all audio download features

### Smart Features
- **Auto-Analyze**: Automatically analyze downloaded audio files
- **Dynamic Folders**: Automatically detects user's Downloads folder
- **Settings Memory**: Remembers all preferences between sessions
- **Modern UI**: Clean, responsive interface with light/dark themes

## 🔧 New Options

### Auto-Analyze Key and BPM
- New checkbox in options menu
- Automatically analyzes audio files after download
- Can be toggled on/off and remembers setting

### Enhanced Settings
- Download directory (defaults to user's Downloads folder)
- Audio format and quality preferences
- Mute/unmute state persistence
- Auto-analyze preference

## 🐛 Bug Fixes

- Fixed audio playback issues on app startup
- Resolved download crashes and compatibility issues
- Fixed settings not saving properly
- Corrected analyze button visibility logic
- Eliminated NumPy deprecation warnings

## 📊 Performance Improvements

- Background video information fetching
- Asynchronous audio analysis
- Real-time download progress with speed/ETA
- Dynamic window resizing for better content display

## 🎨 UI/UX Enhancements

- Modern checkbox styling with custom SVG icons
- Enhanced dropdown appearance with custom arrows
- Improved text readability and layout
- Dynamic window sizing based on content
- Better color schemes for light/dark modes

## 📝 Migration Notes

### From v1.0 to v1.1
- **Settings**: Existing settings will be automatically migrated
- **Dependencies**: New dependencies required (see requirements.txt)
- **PyQt6**: Requires PyQt6 instead of PyQt5
- **FFmpeg**: Still included in the package, no changes needed

## 🔗 Files Changed

### New Files
- `CHANGELOG.md` - Detailed version history
- `VERSION` - Version tracking file
- `RELEASE_v1.1.0.md` - This release summary

### Updated Files
- `Waver.py` - Main application (PyQt6 migration + new features)
- `README.md` - Enhanced documentation
- `requirements.txt` - Updated dependencies

## 🎯 What's Next

Future versions may include:
- Batch download capabilities
- More audio analysis features
- Additional video format support
- Enhanced playlist handling
- Cloud storage integration

## 🤝 Support

- **Issues**: Report bugs to catwarez@proton.me
- **Features**: Request new features via email
- **Documentation**: See README.md for detailed usage

---

**Enjoy making music with Waver v1.1.0!** 🎵✨

*Released: February 8, 2025* 