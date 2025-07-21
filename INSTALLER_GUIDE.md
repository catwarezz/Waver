# Waver v1.1.0 Installer Build Guide

This guide explains how to create professional installers for Waver v1.1.0, including handling the large FFmpeg dependency.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - For building the application
- **NSIS 3.0+** - For creating Windows installer
- **Git** - For version control (optional)

### Python Dependencies
- PyInstaller 5.0+
- All Waver runtime dependencies (see requirements.txt)

## 🚀 Quick Build Process

### Automated Build (Recommended)
```bash
# Run the automated build script
build_installer.bat
```

This script will:
1. Install all dependencies
2. Download FFmpeg automatically
3. Build the executable with PyInstaller
4. Create NSIS installer
5. Generate both installer and portable versions
6. Create checksums for verification

### Manual Build Process

#### Step 1: Setup Environment
```bash
# Install build dependencies
python build_setup.py

# Or manually:
pip install pyinstaller setuptools wheel
pip install -r requirements.txt
```

#### Step 2: Download FFmpeg
```bash
# Automated download
python setup.py --download-ffmpeg

# Manual download (if automated fails):
# 1. Download from https://github.com/BtbN/FFmpeg-Builds/releases
# 2. Extract to ffmpeg_bin/ folder
```

#### Step 3: Build Executable
```bash
# Clean previous builds
rmdir /s build dist

# Build with PyInstaller
pyinstaller Waver.spec --clean --noconfirm
```

#### Step 4: Create Installer
```bash
# Requires NSIS installed and in PATH
makensis installer.nsi
```

## 📦 Output Files

After successful build, you'll have:

### In `release/` folder:
- **WaverInstaller_v1.1.0.exe** - Windows installer
- **Waver_v1.1.0_Portable.zip** - Portable version
- **Documentation** - README, CHANGELOG, etc.
- **Checksums** - SHA256 verification files

### Installer Features:
- ✅ **Professional UI** with modern appearance
- ✅ **FFmpeg Download** during installation
- ✅ **Registry Integration** for Add/Remove Programs
- ✅ **Shortcuts** on Desktop and Start Menu
- ✅ **Uninstaller** with complete removal
- ✅ **Upgrade Detection** replaces old versions
- ✅ **Admin Privileges** for system-wide installation

## 🔧 Customization

### Modify Version Information
Update these files when creating new versions:
- `VERSION` - Version number
- `Waver.py` - `__version__` variable
- `setup.py` - VERSION constant
- `Waver.spec` - APP_VERSION
- `installer.nsi` - Version strings

### Add/Remove Components
Edit `installer.nsi` sections:
- **SecWaver** - Core application (required)
- **SecFFmpeg** - FFmpeg binaries
- **SecDesktop** - Desktop shortcut
- **SecStartMenu** - Start menu shortcuts

### Modify Build Settings
Edit `Waver.spec`:
- **datas** - Files to include
- **hiddenimports** - Python modules to bundle
- **excludes** - Modules to exclude (reduces size)

## 🐛 Troubleshooting

### Common Issues

#### FFmpeg Download Fails
If the automated FFmpeg download fails during installation, you can install it manually:

**Option 1: During Installer**
1. When the installer fails to download FFmpeg, continue with installation
2. Download FFmpeg manually after installation (see Option 2)

**Option 2: Manual Installation**
```bash
# Step 1: Download FFmpeg
# Go to: https://github.com/BtbN/FFmpeg-Builds/releases
# Download: ffmpeg-master-latest-win64-gpl.zip

# Step 2: Extract and copy files
1. Extract the downloaded ZIP file
2. Navigate to the extracted folder (e.g., ffmpeg-master-latest-win64-gpl)
3. Copy these folders to your Waver installation directory:
   - bin/ → [Waver Install Dir]/ffmpeg_bin/bin/
   - doc/ → [Waver Install Dir]/ffmpeg_bin/doc/
   - presets/ → [Waver Install Dir]/ffmpeg_bin/presets/
   - LICENSE → [Waver Install Dir]/ffmpeg_bin/LICENSE
   - README.txt → [Waver Install Dir]/ffmpeg_bin/README.txt

# Step 3: Verify installation
# Check that ffmpeg.exe exists at:
# [Waver Install Dir]/ffmpeg_bin/bin/ffmpeg.exe
```

**Option 3: Use Your Own FFmpeg**
If you already have FFmpeg installed system-wide:
1. Copy your ffmpeg.exe to [Waver Install Dir]/ffmpeg_bin/bin/
2. Or add your FFmpeg location to system PATH

**Common Download Issues:**
- **Corporate Firewall**: Download manually from a different network
- **Antivirus Blocking**: Temporarily disable real-time protection
- **PowerShell Restrictions**: Run installer as Administrator
- **Network Issues**: Try the installer on a different internet connection

#### PyInstaller Missing Modules
```bash
# Add to hiddenimports in Waver.spec:
hiddenimports = [
    'your_missing_module',
    # ... existing imports
]
```

#### Large File Size
```bash
# Add to excludes in Waver.spec:
excludes = [
    'unnecessary_module',
    # ... existing excludes
]
```

#### NSIS Plugins Missing
Install additional NSIS plugins:
- **nsisunz** - For ZIP extraction
- **NSISdl** - For downloads (usually included)

### Build Environment Issues

#### Virtual Environment Recommended
```bash
# Create isolated environment
python -m venv build_env
build_env\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

#### Clean Build
```bash
# Remove all build artifacts
rmdir /s /q build dist __pycache__
del *.spec
# Then rebuild
```

## 📋 Distribution Checklist

Before releasing:

### ✅ Pre-Build
- [ ] Update version numbers in all files
- [ ] Test application functionality
- [ ] Update CHANGELOG.md
- [ ] Commit all changes to git

### ✅ Build Process
- [ ] Clean previous builds
- [ ] Run full build script
- [ ] Verify installer creation
- [ ] Test installer on clean machine
- [ ] Verify FFmpeg download works

### ✅ Testing
- [ ] Install on Windows 10/11
- [ ] Test all application features
- [ ] Verify uninstaller works
- [ ] Check shortcuts function
- [ ] Test portable version

### ✅ Release
- [ ] Generate checksums
- [ ] Create release notes
- [ ] Upload to distribution platform
- [ ] Test download links
- [ ] Update documentation

## 🔐 Security Considerations

### Code Signing (Recommended)
```bash
# Sign the installer with your certificate
signtool sign /f certificate.pfx /p password WaverInstaller_v1.1.0.exe
```

### Virus Scanner False Positives
- PyInstaller executables sometimes trigger antivirus
- Submit to VirusTotal before release
- Consider code signing to reduce false positives

### FFmpeg Security
- Downloads from official GitHub releases only
- Verify checksums if implementing custom verification
- Users can provide their own FFmpeg if preferred

## 📞 Support

For build issues:
1. Check this guide first
2. Verify all prerequisites are installed
3. Try clean build environment
4. Check GitHub Issues for similar problems

---

**Happy Building!** 🎵✨

*For more information, see README.md and CHANGELOG.md* 