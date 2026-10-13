Unicode True
!include "MUI2.nsh"
!include "x64.nsh"
Name "VLC Juxtopposed (unofficial redesign)"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\VLC Juxtopposed"
InstallDirRegKey HKCU "Software\Quite\VLCJuxtopposed" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
VIProductVersion "4.0.0.0"
VIAddVersionKey "ProductName" "VLC Juxtopposed — unofficial redesign"
VIAddVersionKey "FileDescription" "VLC Juxtopposed Windows x64 installer"
VIAddVersionKey "FileVersion" "4.0.0-dev"
VIAddVersionKey "LegalCopyright" "VideoLAN contributors; design by Juxtopposed (CC BY 4.0)"
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${PAYLOAD}\COPYING.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Russian"
Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "This build requires Windows x64."
    Abort
  ${EndIf}
FunctionEnd
Section "VLC Juxtopposed"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  !include "${INSTALL_MANIFEST}"
  WriteUninstaller "$INSTDIR\Uninstall-Juxtopposed.exe"
  WriteRegStr HKCU "Software\Quite\VLCJuxtopposed" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "DisplayName" "VLC Juxtopposed (unofficial redesign)"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "DisplayVersion" "4.0.0-dev"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "UninstallString" '"$INSTDIR\Uninstall-Juxtopposed.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "DisplayIcon" "$INSTDIR\vlc.exe"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed" "NoRepair" 1
  CreateDirectory "$INSTDIR\portable"
  SetOutPath "$INSTDIR"
  ; WinVLC's upstream crash handler uses stock RoamingAppData even in portable mode.
  CreateShortCut "$SMPROGRAMS\VLC Juxtopposed.lnk" "$INSTDIR\vlc.exe" '--no-crashdump --config="$INSTDIR\portable\vlcrc"'
SectionEnd
Section "Uninstall"
  SetShellVarContext current
  !include "${UNINSTALL_MANIFEST}"
  Delete "$INSTDIR\Uninstall-Juxtopposed.exe"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\VLC Juxtopposed.lnk"
  DeleteRegKey HKCU "Software\Quite\VLCJuxtopposed"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\VLCJuxtopposed"
  ; Keep user preferences and any non-package files. Never touch stock VLC keys.
SectionEnd
