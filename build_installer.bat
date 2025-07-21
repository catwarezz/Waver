@echo off
REM Waver v1.1.0 Installer Build Script
REM Automates the entire build process for creating the installer
REM Requires: Python 3.8+, PyInstaller, NSIS 3.0+

echo ================================================
echo Waver v1.1.0 Installer Build Script
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if NSIS is available
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo ERROR: NSIS is not installed or not in PATH
    echo Please install NSIS 3.0+ and add it to PATH
    echo Download from: https://nsis.sourceforge.io/
    pause
    exit /b 1
)

echo Step 1: Installing build dependencies...
echo ================================================
python -m pip install --upgrade pip
python -m pip install pyinstaller setuptools wheel

echo.
echo Step 2: Installing application dependencies...
echo ================================================
python -m pip install -r requirements.txt

echo.
echo Step 3: Downloading FFmpeg (if needed)...
echo ================================================
python setup.py --download-ffmpeg

echo.
echo Step 4: Cleaning previous builds...
echo ================================================
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del "*.spec"

echo.
echo Step 5: Building executable with PyInstaller...
echo ================================================
pyinstaller Waver.spec --clean --noconfirm

REM Check if build was successful
if not exist "dist\Waver_v1.1.0\Waver.exe" (
    echo ERROR: PyInstaller build failed
    echo Check the console output for errors
    pause
    exit /b 1
)

echo.
echo Step 6: Creating LICENSE.txt for installer...
echo ================================================
if not exist "LICENSE.txt" (
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright ^(c^) 2025 catwarez >> LICENSE.txt
    echo. >> LICENSE.txt
    echo Permission is hereby granted, free of charge, to any person obtaining a copy >> LICENSE.txt
    echo of this software and associated documentation files ^(the "Software"^), to deal >> LICENSE.txt
    echo in the Software without restriction, including without limitation the rights >> LICENSE.txt
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> LICENSE.txt
    echo copies of the Software, and to permit persons to whom the Software is >> LICENSE.txt
    echo furnished to do so, subject to the following conditions: >> LICENSE.txt
    echo. >> LICENSE.txt
    echo The above copyright notice and this permission notice shall be included in all >> LICENSE.txt
    echo copies or substantial portions of the Software. >> LICENSE.txt
    echo. >> LICENSE.txt
    echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR >> LICENSE.txt
    echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, >> LICENSE.txt
    echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE >> LICENSE.txt
    echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER >> LICENSE.txt
    echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, >> LICENSE.txt
    echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE >> LICENSE.txt
    echo SOFTWARE. >> LICENSE.txt
)

echo.
echo Step 7: Building NSIS installer...
echo ================================================
makensis installer.nsi

REM Check if installer was created
if not exist "WaverInstaller_v1.1.0.exe" (
    echo ERROR: NSIS installer build failed
    echo Check the console output for errors
    pause
    exit /b 1
)

echo.
echo Step 8: Creating distribution package...
echo ================================================
if not exist "release" mkdir "release"

REM Copy installer to release folder
copy "WaverInstaller_v1.1.0.exe" "release\"

REM Create portable version (optional)
echo Creating portable package...
if not exist "release\Waver_v1.1.0_Portable" mkdir "release\Waver_v1.1.0_Portable"
xcopy "dist\Waver_v1.1.0\*" "release\Waver_v1.1.0_Portable\" /E /I /H /Y

REM Copy documentation to release
copy "README.md" "release\"
copy "CHANGELOG.md" "release\"
copy "RELEASE_v1.1.0.md" "release\"
copy "VERSION" "release\"

REM Create ZIP for portable version
echo Creating portable ZIP...
powershell -command "Compress-Archive -Path 'release\Waver_v1.1.0_Portable\*' -DestinationPath 'release\Waver_v1.1.0_Portable.zip' -Force"

echo.
echo Step 9: Generating checksums...
echo ================================================
cd release
powershell -command "Get-FileHash WaverInstaller_v1.1.0.exe -Algorithm SHA256 | Select-Object Hash | Format-Table -HideTableHeaders" > WaverInstaller_v1.1.0.exe.sha256
powershell -command "Get-FileHash Waver_v1.1.0_Portable.zip -Algorithm SHA256 | Select-Object Hash | Format-Table -HideTableHeaders" > Waver_v1.1.0_Portable.zip.sha256
cd ..

echo.
echo ================================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo Files created in 'release' folder:
echo - WaverInstaller_v1.1.0.exe     (Windows Installer)
echo - Waver_v1.1.0_Portable.zip     (Portable Version)
echo - WaverInstaller_v1.1.0.exe.sha256 (Checksum)
echo - Waver_v1.1.0_Portable.zip.sha256 (Checksum)
echo - README.md, CHANGELOG.md, etc. (Documentation)
echo.
echo The installer includes:
echo - Waver application executable
echo - All required dependencies
echo - FFmpeg binaries download during installation
echo - Desktop and Start Menu shortcuts
echo - Uninstaller
echo - Registry entries for Add/Remove Programs
echo.
echo Ready for distribution!
echo.
pause 