#!/usr/bin/env python3
"""
Waver v1.1.0 Build Setup Script
Handles FFmpeg download and dependency management for developers
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def check_git():
    """Check if git is available"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✓ Git is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Git not found - version control features may be limited")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    requirements = [
        "PyQt6>=6.4.0",
        "yt-dlp>=2023.1.0", 
        "librosa>=0.10.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
    ]
    
    build_requirements = [
        "pyinstaller>=5.0",
        "setuptools>=65.0",
        "wheel>=0.37.0",
    ]
    
    try:
        # Update pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✓ Pip updated")
        
        # Install runtime dependencies
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        
        # Install build dependencies
        print("\n🛠 Installing build dependencies...")
        for package in build_requirements:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        
        print("✓ All dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def download_ffmpeg():
    """Download and extract FFmpeg binaries"""
    print("\n🎬 Setting up FFmpeg...")
    
    ffmpeg_dir = "ffmpeg_bin"
    ffmpeg_exe = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_exe):
        print(f"✓ FFmpeg already exists at {ffmpeg_exe}")
        return True
    
    # Determine platform and URL
    system = platform.system().lower()
    if system == "windows":
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        executable = "ffmpeg.exe"
    else:
        print(f"⚠ Platform {system} not supported for automatic FFmpeg download")
        print("Please install FFmpeg manually and place it in ffmpeg_bin/bin/")
        return False
    
    try:
        print("Downloading FFmpeg (this may take a while)...")
        
        # Create directories
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # Download
        zip_path = "ffmpeg_temp.zip"
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    f.write(block)
                    downloaded += len(block)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end="", flush=True)
        
        print("\n📦 Extracting FFmpeg...")
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_ffmpeg")
        
        # Find extracted folder
        temp_dir = Path("temp_ffmpeg")
        extracted_folders = [f for f in temp_dir.iterdir() if f.is_dir()]
        
        if not extracted_folders:
            raise Exception("No folders found in extracted archive")
        
        source_dir = extracted_folders[0]
        
        # Copy files
        dirs_to_copy = ["bin", "doc", "presets"]
        for dir_name in dirs_to_copy:
            src = source_dir / dir_name
            dst = Path(ffmpeg_dir) / dir_name
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Copy license files
        for file_name in ["LICENSE", "README.txt"]:
            src = source_dir / file_name
            dst = Path(ffmpeg_dir) / file_name
            if src.exists():
                shutil.copy2(src, dst)
        
        # Cleanup
        os.remove(zip_path)
        shutil.rmtree("temp_ffmpeg")
        
        print("✓ FFmpeg setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up FFmpeg: {e}")
        # Cleanup on error
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists("temp_ffmpeg"):
            shutil.rmtree("temp_ffmpeg")
        return False

def setup_development_environment():
    """Set up the development environment"""
    print("\n🔧 Setting up development environment...")
    
    # Create virtual environment if not exists
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
        print("To activate: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
    else:
        print("✓ Virtual environment already exists")
    
    return True

def verify_installation():
    """Verify that everything is set up correctly"""
    print("\n✅ Verifying installation...")
    
    # Check if main files exist
    required_files = [
        "Waver.py",
        "requirements.txt",
        "setup.py",
        "Waver.spec",
        "build_installer.bat",
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠ Missing files: {', '.join(missing_files)}")
        return False
    
    # Check FFmpeg
    ffmpeg_exe = os.path.join("ffmpeg_bin", "bin", "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        print("⚠ FFmpeg not found")
        return False
    
    # Try importing main dependencies
    try:
        import PyQt6
        import yt_dlp
        import librosa
        import numpy
        import scipy
        print("✓ All dependencies can be imported")
    except ImportError as e:
        print(f"⚠ Import error: {e}")
        return False
    
    print("✓ Installation verified successfully")
    return True

def main():
    """Main setup function"""
    print("="*60)
    print("🎵 Waver v1.1.0 Development Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check git
    check_git()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Download FFmpeg
    if not download_ffmpeg():
        print("⚠ FFmpeg setup failed, but continuing...")
    
    # Setup development environment
    if not setup_development_environment():
        return 1
    
    # Verify installation
    if not verify_installation():
        print("⚠ Verification failed, but setup may still work")
    
    print("\n" + "="*60)
    print("🎉 Setup completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate virtual environment: venv\\Scripts\\activate")
    print("2. Run the application: python Waver.py")
    print("3. Build installer: build_installer.bat")
    print("\nFor more information, see README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 