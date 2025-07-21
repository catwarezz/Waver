#!/usr/bin/env python3
"""
Waver v1.1.0 Setup Script
Handles installation of dependencies and application packaging
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
from setuptools import setup, find_packages

# Version information
VERSION = "1.1.0"
DESCRIPTION = "Modern desktop application for downloading and converting YouTube videos"
LONG_DESCRIPTION = """
Waver is a modern desktop application for downloading and converting YouTube videos 
to audio files (WAV, MP3) or video files (MP4) with advanced features including 
automatic BPM and key detection.

Features:
- Audio Downloads: Convert YouTube videos to WAV or MP3 with quality options
- Video Downloads: Download MP4 videos with resolution selection (480p to 4K)
- Audio Analysis: Automatic BPM (tempo) and key signature detection
- Smart Settings: Remembers download location, format preferences, and analysis settings
- Modern UI: Clean, responsive interface with light/dark mode support
"""

AUTHOR = "catwarez"
AUTHOR_EMAIL = "catwarez@proton.me"
URL = "https://github.com/catwarezz/Waver"

# Dependencies
INSTALL_REQUIRES = [
    "PyQt6>=6.4.0",
    "yt-dlp>=2023.1.0",
    "librosa>=0.10.0",
    "numpy>=1.21.0",
    "scipy>=1.7.0",
]

# Additional dependencies for building
BUILD_REQUIRES = [
    "pyinstaller>=5.0",
    "setuptools>=65.0",
    "wheel>=0.37.0",
]

# FFmpeg download configuration
FFMPEG_VERSION = "6.1.1"
FFMPEG_URL = f"https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_DIR = "ffmpeg_bin"

def download_ffmpeg():
    """Download and extract FFmpeg binaries if not present"""
    print("Checking for FFmpeg binaries...")
    
    ffmpeg_exe = os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe):
        print(f"FFmpeg already exists at {ffmpeg_exe}")
        return True
    
    print("FFmpeg not found. Downloading...")
    try:
        # Create ffmpeg directory
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        
        # Download FFmpeg
        zip_path = "ffmpeg.zip"
        print(f"Downloading from {FFMPEG_URL}")
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
        
        # Extract FFmpeg
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all files
            zip_ref.extractall("temp_ffmpeg")
            
            # Find the extracted folder (it will have a specific name)
            temp_dir = "temp_ffmpeg"
            extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
            
            if extracted_folders:
                source_dir = os.path.join(temp_dir, extracted_folders[0])
                
                # Copy bin folder
                if os.path.exists(os.path.join(source_dir, "bin")):
                    shutil.copytree(os.path.join(source_dir, "bin"), 
                                  os.path.join(FFMPEG_DIR, "bin"), 
                                  dirs_exist_ok=True)
                
                # Copy doc folder if it exists
                if os.path.exists(os.path.join(source_dir, "doc")):
                    shutil.copytree(os.path.join(source_dir, "doc"), 
                                  os.path.join(FFMPEG_DIR, "doc"), 
                                  dirs_exist_ok=True)
                
                # Copy presets folder if it exists
                if os.path.exists(os.path.join(source_dir, "presets")):
                    shutil.copytree(os.path.join(source_dir, "presets"), 
                                  os.path.join(FFMPEG_DIR, "presets"), 
                                  dirs_exist_ok=True)
                
                # Copy license files
                for file in ["LICENSE", "README.txt"]:
                    src_file = os.path.join(source_dir, file)
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, os.path.join(FFMPEG_DIR, file))
        
        # Cleanup
        os.remove(zip_path)
        shutil.rmtree("temp_ffmpeg")
        
        print("FFmpeg download and extraction completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        for package in INSTALL_REQUIRES:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("Dependencies installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def install_build_dependencies():
    """Install build-time dependencies"""
    print("Installing build dependencies...")
    try:
        for package in BUILD_REQUIRES:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("Build dependencies installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing build dependencies: {e}")
        return False

class CustomInstallCommand:
    """Custom installation command that handles FFmpeg download"""
    
    def run(self):
        # Download FFmpeg
        if not download_ffmpeg():
            print("Warning: FFmpeg download failed. You may need to install it manually.")
        
        # Install dependencies
        install_dependencies()

# Setup configuration
setup(
    name="waver",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    py_modules=["Waver"],
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "build": BUILD_REQUIRES,
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "waver=Waver:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "music/*.mp3",
            "UI_Photos/*",
            "ffmpeg_bin/bin/*",
            "ffmpeg_bin/doc/*",
            "ffmpeg_bin/presets/*",
            "ffmpeg_bin/LICENSE",
            "ffmpeg_bin/README.txt",
            "*.md",
            "VERSION",
            "requirements.txt",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Video :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Win32 (MS Windows)",
    ],
    keywords="youtube downloader audio video converter mp3 wav mp4 bpm key detection",
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}#readme",
    },
)

# Custom commands for manual execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Waver Setup Script")
    parser.add_argument("--download-ffmpeg", action="store_true", 
                       help="Download FFmpeg binaries")
    parser.add_argument("--install-deps", action="store_true", 
                       help="Install Python dependencies")
    parser.add_argument("--install-build-deps", action="store_true", 
                       help="Install build dependencies")
    parser.add_argument("--full-setup", action="store_true", 
                       help="Run complete setup (FFmpeg + dependencies)")
    
    args = parser.parse_args()
    
    if args.download_ffmpeg:
        download_ffmpeg()
    elif args.install_deps:
        install_dependencies()
    elif args.install_build_deps:
        install_build_dependencies()
    elif args.full_setup:
        download_ffmpeg()
        install_dependencies()
        install_build_dependencies()
    else:
        print("Waver v1.1.0 Setup Script")
        print("Use --help for available options")
        print("For normal installation, run: pip install .") 