# Changelog

All notable changes to Waver will be documented in this file.

## [1.1.0] - 2025-02-08

### 🎉 Major New Features
- **🎵 Audio Analysis**: Added automatic BPM (tempo) and key signature detection
  - Analyzes the first 60 seconds of audio files using librosa
  - Displays results in a clean, horizontal layout
  - Supports both automatic and manual analysis modes
- **📹 Video Downloads**: Added MP4 video download capability
  - Quality options: 480p, 720p, 1080p, 1440p, 2160p (4K)
  - Automatic format selection based on quality preference
  - Maintains all existing audio download features

### 🔧 Core Improvements
- **🔄 PyQt6 Migration**: Complete upgrade from PyQt5 to PyQt6
  - Updated all imports and API calls
  - Fixed enum syntax changes (e.g., `Qt.AlignCenter` → `Qt.AlignmentFlag.AlignCenter`)
  - Improved audio playback compatibility
- **💾 Smart Settings**: Enhanced settings persistence
  - Remembers download directory (defaults to user's Downloads folder)
  - Saves audio format and quality preferences
  - Persists mute/unmute state between sessions
  - Remembers auto-analyze preference
- **🎨 UI/UX Enhancements**:
  - Dynamic window resizing to accommodate analysis results
  - Improved video information display with better formatting
  - Enhanced checkbox visibility with custom SVG icons
  - Modern dropdown styling with custom arrows
  - Better text readability and layout

### 🐛 Bug Fixes
- **🔊 Audio Playback**: Fixed audio not playing on app startup
  - Resolved muted state persistence issues
  - Fixed QAudioOutput compatibility in PyQt6
- **💥 Download Crashes**: Fixed crashes during download functionality
  - Resolved QFont enum compatibility issues
  - Fixed file path handling for converted audio files
- **⚙️ Settings Issues**: Fixed settings not saving properly
  - Removed duplicate saveSettings method
  - Ensured immediate settings persistence
- **🎯 Button Logic**: Fixed analyze button visibility issues
  - Button now properly hides when auto-analyze is enabled
  - Conditional display based on file type and settings
- **⚠️ Warnings**: Fixed NumPy deprecation warnings
  - Updated array-to-scalar conversion for compatibility

### 🚀 Performance Improvements
- **⚡ Async Operations**: Added background processing for better UI responsiveness
  - Video information fetching now runs in background thread
  - Audio analysis runs asynchronously to prevent UI freezing
  - Download progress updates without blocking the interface
- **📊 Progress Tracking**: Enhanced download progress display
  - Real-time speed and ETA information
  - Better status messages and error handling

### 🎛️ New Options
- **Auto-Analyze Key and BPM**: New checkbox in options menu
  - Automatically analyzes audio files after download
  - Can be toggled on/off and remembers setting
- **Dynamic Download Folder**: 
  - Automatically detects user's default Downloads folder
  - Supports custom folder selection with reset option
- **Quality Selection**: 
  - Audio: 128k, 192k, 256k, 320k bitrates
  - Video: 480p to 4K resolution options

### 🔧 Technical Improvements
- **📦 Dependencies**: Updated requirements.txt with new libraries
  - Added librosa for audio analysis
  - Added numpy and scipy for numerical processing
  - Updated PyQt6 version requirements
- **🏗️ Code Structure**: Improved code organization
  - Separated concerns with dedicated worker classes
  - Better error handling and user feedback
  - Cleaner signal/slot connections

### 🎨 Visual Enhancements
- **🎨 Modern Styling**: Enhanced QSS styling throughout
  - Custom checkbox indicators with SVG icons
  - Improved dropdown appearance with custom arrows
  - Better color schemes for light/dark modes
- **📱 Responsive Design**: Dynamic window sizing
  - Automatically adjusts height based on content
  - Better handling of analysis results display
  - Improved text wrapping and layout

---

## [1.0.0] - Initial Release

### 🎉 Initial Features
- Basic YouTube to audio conversion (WAV/MP3)
- Simple download interface
- Basic settings management
- PyQt5-based GUI

---

## 📝 Version Numbering

We use [Semantic Versioning](https://semver.org/) for version numbers:
- **MAJOR.MINOR.PATCH**
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

## 🔗 Migration Notes

### From v1.0 to v1.1
- **Settings**: Existing settings will be automatically migrated
- **Dependencies**: New dependencies required (see requirements.txt)
- **PyQt6**: Requires PyQt6 instead of PyQt5
- **FFmpeg**: Still included in the package, no changes needed

---

**For detailed installation instructions, see [README.md](README.md)** 