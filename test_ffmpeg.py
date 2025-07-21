#!/usr/bin/env python3
"""
FFmpeg Installation Test Script for Waver v1.1.0
Run this script to verify that FFmpeg is properly installed and accessible
"""

import os
import sys
import subprocess
from pathlib import Path

def test_ffmpeg_installation():
    """Test if FFmpeg is properly installed and accessible"""
    print("🎬 Testing FFmpeg Installation for Waver")
    print("=" * 50)
    
    # Get the directory where this script is located (should be Waver root)
    script_dir = Path(__file__).parent
    ffmpeg_bin_dir = script_dir / "ffmpeg_bin" / "bin"
    ffmpeg_exe = ffmpeg_bin_dir / "ffmpeg.exe"
    
    print(f"Looking for FFmpeg at: {ffmpeg_exe}")
    
    # Test 1: Check if FFmpeg executable exists
    if ffmpeg_exe.exists():
        print("✅ FFmpeg executable found")
    else:
        print("❌ FFmpeg executable not found")
        print("\nPossible solutions:")
        print("1. Run the installer again and ensure FFmpeg downloads")
        print("2. Download FFmpeg manually from: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("3. Extract and place ffmpeg.exe in: ffmpeg_bin/bin/")
        return False
    
    # Test 2: Check if FFmpeg is executable and get version
    try:
        print("\n🔍 Testing FFmpeg functionality...")
        result = subprocess.run([str(ffmpeg_exe), "-version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Extract version info from output
            lines = result.stdout.split('\n')
            version_line = lines[0] if lines else "Unknown version"
            print(f"✅ FFmpeg is working: {version_line}")
            
            # Show some key capabilities
            output = result.stdout.lower()
            formats = []
            if 'libx264' in output:
                formats.append("H.264/MP4")
            if 'libmp3lame' in output or 'mp3' in output:
                formats.append("MP3")
            if 'libvorbis' in output or 'vorbis' in output:
                formats.append("OGG/Vorbis")
            
            if formats:
                print(f"📋 Supported formats: {', '.join(formats)}")
            
        else:
            print("❌ FFmpeg exists but failed to run")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg test timed out")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg executable not found or not executable")
        return False
    except Exception as e:
        print(f"❌ Error testing FFmpeg: {e}")
        return False
    
    # Test 3: Check directory structure
    print("\n📁 Checking directory structure...")
    required_dirs = [
        ffmpeg_bin_dir.parent / "doc",
        ffmpeg_bin_dir.parent / "presets"
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.name}/ directory found")
        else:
            print(f"⚠️  {dir_path.name}/ directory missing (optional)")
    
    # Test 4: Test with Waver's expected path resolution
    print("\n🎵 Testing Waver integration...")
    try:
        # Simulate how Waver finds FFmpeg
        def resource_path(relative_path):
            """Simulate Waver's resource_path function"""
            base_path = getattr(sys, '_MEIPASS', os.getcwd())
            return os.path.join(base_path, relative_path)
        
        waver_ffmpeg_dir = resource_path("ffmpeg_bin/bin")
        waver_ffmpeg_exe = os.path.join(waver_ffmpeg_dir, "ffmpeg.exe")
        
        if os.path.exists(waver_ffmpeg_exe):
            print("✅ FFmpeg accessible via Waver's path resolution")
        else:
            print("⚠️  FFmpeg may not be accessible to Waver")
            print(f"Expected path: {waver_ffmpeg_exe}")
            
    except Exception as e:
        print(f"⚠️  Error testing Waver integration: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 FFmpeg Installation Test Complete!")
    print("\nIf all tests passed, Waver should work properly.")
    print("If there were issues, see the installer guide for manual setup.")
    
    return True

def main():
    """Main function"""
    try:
        success = test_ffmpeg_installation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 