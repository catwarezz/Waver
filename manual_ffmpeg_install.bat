@echo off
REM Manual FFmpeg Installation Script for Waver v1.1.0
REM Use this if the installer hangs during FFmpeg download

echo ================================================
echo Manual FFmpeg Installation for Waver v1.1.0
echo ================================================
echo.
echo This script will help you manually install FFmpeg
echo if the installer hangs or fails during FFmpeg download.
echo.

REM Check if we're in the right directory
if not exist "Waver.exe" (
    echo ERROR: This script must be run from the Waver installation directory
    echo Expected location: C:\Program Files\Waver\ or similar
    echo.
    echo Please:
    echo 1. Navigate to your Waver installation folder
    echo 2. Copy this script there
    echo 3. Run it again
    echo.
    pause
    exit /b 1
)

echo Found Waver installation. Proceeding with FFmpeg setup...
echo.

REM Check if FFmpeg already exists
if exist "ffmpeg_bin\bin\ffmpeg.exe" (
    echo FFmpeg is already installed!
    echo Location: %CD%\ffmpeg_bin\bin\ffmpeg.exe
    echo.
    echo Running verification test...
    "ffmpeg_bin\bin\ffmpeg.exe" -version 2>nul
    if errorlevel 1 (
        echo WARNING: FFmpeg exists but may not be working properly
    ) else (
        echo ✓ FFmpeg is working correctly!
        echo.
        echo You can now use Waver normally.
        pause
        exit /b 0
    )
)

echo FFmpeg not found. Starting manual installation...
echo.

REM Create directories
echo Creating directories...
if not exist "ffmpeg_bin" mkdir "ffmpeg_bin"
if not exist "ffmpeg_bin\bin" mkdir "ffmpeg_bin\bin"
if not exist "ffmpeg_bin\doc" mkdir "ffmpeg_bin\doc"
if not exist "ffmpeg_bin\presets" mkdir "ffmpeg_bin\presets"

REM Check if PowerShell is available
powershell -command "Write-Host 'PowerShell available'" 2>nul
if errorlevel 1 (
    echo PowerShell not available. Manual download required.
    goto MANUAL_DOWNLOAD
)

echo Attempting to download FFmpeg...
echo This may take several minutes depending on your internet connection.
echo.

REM Try downloading with PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Write-Host 'Starting download...'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'Continue'; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg_temp.zip' -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'; Write-Host 'Download completed'; exit 0 } catch { Write-Host 'Download failed:' $_; exit 1 }}"

if errorlevel 1 (
    echo PowerShell download failed. Trying alternative method...
    
    REM Try with bitsadmin
    bitsadmin /transfer "FFmpeg Download" /priority normal "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" "%CD%\ffmpeg_temp.zip"
    
    if errorlevel 1 (
        echo Automatic download failed. Please download manually.
        goto MANUAL_DOWNLOAD
    )
)

REM Check if download was successful
if not exist "ffmpeg_temp.zip" (
    echo Download verification failed - file not found.
    goto MANUAL_DOWNLOAD
)

echo Download successful! Extracting...

REM Extract using PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Write-Host 'Extracting...'; Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('ffmpeg_temp.zip', 'temp_extract'); Write-Host 'Extraction completed'; exit 0 } catch { Write-Host 'Extraction failed:' $_; exit 1 }}"

if errorlevel 1 (
    echo Extraction failed. Please extract manually.
    goto MANUAL_EXTRACT
)

echo Copying files...

REM Find the extracted folder
for /d %%i in (temp_extract\ffmpeg-*) do (
    echo Found FFmpeg folder: %%i
    
    REM Copy files
    if exist "%%i\bin\" xcopy "%%i\bin\*" "ffmpeg_bin\bin\" /E /I /H /Y
    if exist "%%i\doc\" xcopy "%%i\doc\*" "ffmpeg_bin\doc\" /E /I /H /Y  
    if exist "%%i\presets\" xcopy "%%i\presets\*" "ffmpeg_bin\presets\" /E /I /H /Y
    if exist "%%i\LICENSE" copy "%%i\LICENSE" "ffmpeg_bin\"
    if exist "%%i\README.txt" copy "%%i\README.txt" "ffmpeg_bin\"
)

REM Cleanup
echo Cleaning up temporary files...
if exist "ffmpeg_temp.zip" del "ffmpeg_temp.zip"
if exist "temp_extract" rmdir /s /q "temp_extract"

REM Verify installation
echo.
echo Verifying installation...
if exist "ffmpeg_bin\bin\ffmpeg.exe" (
    echo ✓ FFmpeg executable found
    
    REM Test if it works
    "ffmpeg_bin\bin\ffmpeg.exe" -version >nul 2>&1
    if errorlevel 1 (
        echo ⚠ FFmpeg exists but may not be working properly
        echo Try running: ffmpeg_bin\bin\ffmpeg.exe -version
    ) else (
        echo ✓ FFmpeg is working correctly!
        echo.
        echo ================================================
        echo SUCCESS! FFmpeg has been installed successfully.
        echo ================================================
        echo.
        echo You can now use Waver normally.
        echo Location: %CD%\ffmpeg_bin\bin\ffmpeg.exe
    )
) else (
    echo ✗ FFmpeg installation failed
    goto MANUAL_DOWNLOAD
)

echo.
pause
exit /b 0

:MANUAL_DOWNLOAD
echo.
echo ================================================
echo MANUAL DOWNLOAD REQUIRED
echo ================================================
echo.
echo Automatic download failed. Please follow these steps:
echo.
echo 1. Open your web browser
echo 2. Go to: https://github.com/BtbN/FFmpeg-Builds/releases
echo 3. Download: ffmpeg-master-latest-win64-gpl.zip
echo 4. Save it to this folder: %CD%
echo 5. Run this script again (it will extract automatically)
echo.
echo OR extract manually:
echo 1. Extract the ZIP file
echo 2. Copy the contents to:
echo    - bin\ files to:      %CD%\ffmpeg_bin\bin\
echo    - doc\ files to:      %CD%\ffmpeg_bin\doc\
echo    - presets\ files to:  %CD%\ffmpeg_bin\presets\
echo    - LICENSE to:         %CD%\ffmpeg_bin\
echo    - README.txt to:      %CD%\ffmpeg_bin\
echo.
pause
exit /b 1

:MANUAL_EXTRACT
echo.
echo ================================================
echo MANUAL EXTRACTION REQUIRED
echo ================================================
echo.
echo The FFmpeg ZIP file was downloaded but extraction failed.
echo.
echo Please:
echo 1. Find the file: %CD%\ffmpeg_temp.zip
echo 2. Right-click and select "Extract All..."
echo 3. Extract to a temporary folder
echo 4. Copy the extracted files to the ffmpeg_bin folder as shown above
echo.
echo Then run: test_ffmpeg.py to verify the installation
echo.
pause
exit /b 1 