; Waver v1.1.0 NSIS Installer Script
; Creates a professional Windows installer with FFmpeg download
; Requires NSIS 3.0+ with additional plugins

;--------------------------------
; Include Modern UI
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"
!include "FileFunc.nsh"
!include "nsDialogs.nsh"

;--------------------------------
; General
Name "Waver v1.1.0"
OutFile "WaverInstaller_v1.1.0.exe"
Unicode True

; Default installation folder
InstallDir "$PROGRAMFILES64\Waver"

; Get installation folder from registry if available
InstallDirRegKey HKLM "Software\Waver" "InstallDir"

; Request application privileges
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma

;--------------------------------
; Version Information
VIProductVersion "1.1.0.0"
VIAddVersionKey "ProductName" "Waver"
VIAddVersionKey "ProductVersion" "1.1.0"
VIAddVersionKey "CompanyName" "catwarez"
VIAddVersionKey "LegalCopyright" "© 2025 catwarez"
VIAddVersionKey "FileDescription" "Waver - YouTube Audio/Video Downloader"
VIAddVersionKey "FileVersion" "1.1.0"

;--------------------------------
; Variables
Var StartMenuFolder
Var SkipFFmpegDownload

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "UI_Photos\favicon.ico"
!define MUI_UNICON "UI_Photos\favicon.ico"

; Header image
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "UI_Photos\uiia.png"
!define MUI_HEADERIMAGE_RIGHT

; Welcome page
!define MUI_WELCOMEFINISHPAGE_BITMAP "UI_Photos\background.jpg"

;--------------------------------
; Pages

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Waver" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "Waver Application" SecWaver
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    ; Application files
    File "dist\Waver_v1.1.0\*.*"
    
    ; Copy application directory structure
    File /r "dist\Waver_v1.1.0\*"
    
    ; Additional files
    File "README.md"
    File "CHANGELOG.md"
    File "VERSION"
    File "requirements.txt"
    File "test_ffmpeg.py"
    File "manual_ffmpeg_install.bat"
    
    ; Store installation folder
    WriteRegStr HKLM "Software\Waver" "InstallDir" $INSTDIR
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Add/Remove Programs entry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "DisplayName" "Waver v1.1.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "DisplayIcon" "$INSTDIR\Waver.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "Publisher" "catwarez"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "DisplayVersion" "1.1.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "NoRepair" 1
    
    ; Calculate size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "EstimatedSize" "$0"
    
SectionEnd

Section "FFmpeg Binaries" SecFFmpeg
    ; Check if FFmpeg already exists
    IfFileExists "$INSTDIR\ffmpeg_bin\bin\ffmpeg.exe" 0 +3
        MessageBox MB_YESNO "FFmpeg binaries already exist. Download again?" IDYES +2
        Goto SkipFFmpegDownload
    
    ; Ask user if they want to skip FFmpeg download (for troubleshooting)
    MessageBox MB_YESNOCANCEL "Download FFmpeg binaries now?$\n$\nThis is required for audio/video conversion.$\n$\nYes = Download now$\nNo = Skip (download manually later)$\nCancel = Abort installation" IDYES +3 IDNO SkipFFmpegDownload
    MessageBox MB_OK "Installation cancelled by user."
    Abort
    
    DetailPrint "Downloading FFmpeg binaries..."
    
    ; Create temporary directory
    CreateDirectory "$TEMP\WaverInstaller"
    
    ; Download FFmpeg using PowerShell with better error handling and retry logic
    DetailPrint "Downloading FFmpeg (this may take a few minutes)..."
    nsExec::ExecToLog 'powershell -NoProfile -ExecutionPolicy Bypass -Command "& {$maxRetries = 3; $attempt = 0; do { $attempt++; try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = ''SilentlyContinue''; Write-Host \"Attempt $attempt/$maxRetries - Starting download...\"; $webClient = New-Object System.Net.WebClient; $webClient.Headers.Add(''User-Agent'', ''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36''); $webClient.DownloadFile(''https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'', ''$env:TEMP\WaverInstaller\ffmpeg.zip''); Write-Host ''Download completed successfully''; if (Test-Path ''$env:TEMP\WaverInstaller\ffmpeg.zip'') { Write-Host \"File size: $((Get-Item ''$env:TEMP\WaverInstaller\ffmpeg.zip'').Length) bytes\" }; exit 0 } catch { Write-Host \"Attempt $attempt failed: $_\"; if ($attempt -lt $maxRetries) { Start-Sleep -Seconds 2 } } } while ($attempt -lt $maxRetries); Write-Host ''All download attempts failed''; exit 1}" /TIMEOUT=600000'
    Pop $0
    StrCmp $0 "0" +5
        DetailPrint "Primary download failed, trying fallback method..."
        ; Fallback: Try using bitsadmin (older but more reliable on some systems)
        nsExec::ExecToLog 'bitsadmin /transfer "FFmpeg Download" /priority normal "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" "$TEMP\WaverInstaller\ffmpeg.zip" && echo "Bitsadmin download completed" || echo "Bitsadmin download failed"' /TIMEOUT=600000
        Pop $0
        StrCmp $0 "0" +5
            DetailPrint "Both download methods failed, trying minimal fallback..."
            ; Final fallback: Try with curl if available
            nsExec::ExecToLog 'curl -L -o "$TEMP\WaverInstaller\ffmpeg.zip" -A "Mozilla/5.0" "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" || echo "Curl also failed"' /TIMEOUT=600000
            Pop $0
            StrCmp $0 "0" +3
                MessageBox MB_OK "FFmpeg download failed with all methods. Please check your internet connection and firewall settings.$\n$\nCommon solutions:$\n- Run installer as Administrator$\n- Temporarily disable antivirus$\n- Check corporate firewall settings$\n$\nYou can also download FFmpeg manually - see the installer guide for instructions."
                Goto SkipFFmpegDownload
    
    ; Verify download was successful
    DetailPrint "Verifying downloaded file..."
    IfFileExists "$TEMP\WaverInstaller\ffmpeg.zip" +3 0
        MessageBox MB_OK "FFmpeg download verification failed - file not found.$\n$\nThis may be caused by antivirus software blocking the download."
        Goto SkipFFmpegDownload
    
    ; Check file size (should be > 50MB for FFmpeg)
    ${GetSize} "$TEMP\WaverInstaller\ffmpeg.zip" "" $0 $1 $2
    IntCmp $0 50000 +3 0 +3
        MessageBox MB_OK "FFmpeg download appears corrupted (file too small).$\n$\nThis may be caused by network issues or partial download."
        Goto SkipFFmpegDownload
    
    DetailPrint "FFmpeg download verified successfully. Extracting..."
    
    ; Extract FFmpeg using PowerShell with timeout and better error handling
    nsExec::ExecToLog 'powershell -NoProfile -ExecutionPolicy Bypass -Command "& {try { Write-Host ''Starting extraction...''; Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory(''$env:TEMP\WaverInstaller\ffmpeg.zip'', ''$env:TEMP\WaverInstaller\''); Write-Host ''Extraction completed''; exit 0 } catch { Write-Host ''Extraction failed: $_''; exit 1 }}" /TIMEOUT=300000'
    Pop $0
    StrCmp $0 "0" +5
        DetailPrint "PowerShell extraction failed, trying alternative method..."
        ; Fallback: Try using built-in Windows extraction
        nsExec::ExecToLog 'powershell -NoProfile -ExecutionPolicy Bypass -Command "& {$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace(''$env:TEMP\WaverInstaller\ffmpeg.zip''); $dest = $shell.NameSpace(''$env:TEMP\WaverInstaller\''); $dest.CopyHere($zip.Items(), 4); exit 0}" /TIMEOUT=300000'
        Pop $0
        StrCmp $0 "0" +3
            MessageBox MB_OK "FFmpeg extraction failed with both methods. The download may be corrupted or blocked by antivirus software.$\n$\nPlease try running the installer as Administrator or disable antivirus temporarily."
            Goto SkipFFmpegDownload
    
    ; Find extracted folder
    FindFirst $0 $1 "$TEMP\WaverInstaller\ffmpeg-*"
    StrCmp $1 "" SkipFFmpegDownload
    
    ; Copy binaries
    CreateDirectory "$INSTDIR\ffmpeg_bin"
    CreateDirectory "$INSTDIR\ffmpeg_bin\bin"
    CreateDirectory "$INSTDIR\ffmpeg_bin\doc"
    CreateDirectory "$INSTDIR\ffmpeg_bin\presets"
    
    CopyFiles "$TEMP\WaverInstaller\$1\bin\*.*" "$INSTDIR\ffmpeg_bin\bin\"
    CopyFiles "$TEMP\WaverInstaller\$1\doc\*.*" "$INSTDIR\ffmpeg_bin\doc\"
    CopyFiles "$TEMP\WaverInstaller\$1\presets\*.*" "$INSTDIR\ffmpeg_bin\presets\"
    CopyFiles "$TEMP\WaverInstaller\$1\LICENSE" "$INSTDIR\ffmpeg_bin\"
    CopyFiles "$TEMP\WaverInstaller\$1\README.txt" "$INSTDIR\ffmpeg_bin\"
    
    SkipFFmpegDownload:
    
    ; Cleanup
    RMDir /r "$TEMP\WaverInstaller"
    
    ; Final verification and user guidance
    IfFileExists "$INSTDIR\ffmpeg_bin\bin\ffmpeg.exe" +4 0
        MessageBox MB_OK "FFmpeg was not installed automatically.$\n$\nWaver will still work, but you need FFmpeg for audio/video conversion.$\n$\nQuick fix: Run 'manual_ffmpeg_install.bat' in the installation folder as Administrator.$\n$\nSee README.md for detailed instructions."
        DetailPrint "FFmpeg not installed - run manual_ffmpeg_install.bat to fix"
        Goto +2
        DetailPrint "FFmpeg installation completed successfully"
    
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\Waver.lnk" "$INSTDIR\Waver.exe" "" "$INSTDIR\Waver.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Waver.lnk" "$INSTDIR\Waver.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall Waver.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\README.lnk" "$INSTDIR\README.md"
    
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

;--------------------------------
; Descriptions

; Language strings
LangString DESC_SecWaver ${LANG_ENGLISH} "Waver application and core files (required)"
LangString DESC_SecFFmpeg ${LANG_ENGLISH} "Download FFmpeg binaries for audio/video processing"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create start menu shortcuts"

; Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecWaver} $(DESC_SecWaver)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecFFmpeg} $(DESC_SecFFmpeg)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section

Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver"
    DeleteRegKey HKLM "Software\Waver"
    
    ; Remove files and directories
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\Waver.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall Waver.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\README.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    
    Delete "$DESKTOP\Waver.lnk"
    
SectionEnd

;--------------------------------
; Functions

Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Waver" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
        "Waver is already installed. $\n$\nClick 'OK' to remove the previous version or 'Cancel' to cancel this upgrade." \
        IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
        
        IfErrors no_remove_uninstaller done
        IfFileExists "$INSTDIR\Uninstall.exe" 0 no_remove_uninstaller
            Delete $R0
            RMDir $INSTDIR
        
        no_remove_uninstaller:
    
    done:
FunctionEnd 