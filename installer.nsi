; Waver v1.1.0 NSIS Installer Script
; Creates a professional Windows installer with FFmpeg download
; Requires NSIS 3.0+ with additional plugins

;--------------------------------
; Include Modern UI
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"
!include "FileFunc.nsh"

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
    
    DetailPrint "Downloading FFmpeg binaries..."
    
    ; Create temporary directory
    CreateDirectory "$TEMP\WaverInstaller"
    
    ; Download FFmpeg
    NSISdl::download "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" "$TEMP\WaverInstaller\ffmpeg.zip"
    Pop $0
    StrCmp $0 "success" +3
        MessageBox MB_OK "FFmpeg download failed: $0"
        Goto SkipFFmpegDownload
    
    DetailPrint "Extracting FFmpeg..."
    
    ; Extract FFmpeg
    nsisunz::UnzipToLog "$TEMP\WaverInstaller\ffmpeg.zip" "$TEMP\WaverInstaller\"
    Pop $0
    StrCmp $0 "success" +3
        MessageBox MB_OK "FFmpeg extraction failed"
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