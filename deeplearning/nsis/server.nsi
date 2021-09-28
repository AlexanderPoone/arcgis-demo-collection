;NSIS Modern User Interface
;Multilingual Example Script
;Written by Joost Verburg

!pragma warning error all

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"
  !include "LogicLib.nsh"

!define MUI_ICON "C:\Users\Alex\Desktop\favicon.ico"

BrandingText "Esri China (Hong Kong)"
;--------------------------------
;General

  ;Properly display all languages (Installer will not work on Windows 95, 98 or ME!)
  Unicode true

  ;Name and file
  Name "Preprocessing Utility for Oriented Images"
  OutFile "ptool_server_installer.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES64\Video Server for Oriented Images"
  
  ;Get installation folder from registry if available
  ;InstallDirRegKey HKCU "Software\Modern UI Test" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

  ;Show all languages, despite user's codepage
  !define MUI_LANGDLL_ALLLANGUAGES

;--------------------------------
;Language Selection Dialog Settings

  ;Remember the installer language
  ;!define MUI_LANGDLL_REGISTRY_ROOT "HKCU" 
  ;!define MUI_LANGDLL_REGISTRY_KEY "Software\Modern UI Test" 
  ;!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "$(localizedLicenseFile)"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH
  
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_LICENSE "$(localizedLicenseFile)"
  !insertmacro MUI_UNPAGE_COMPONENTS
  ;!insertmacro MUI_UNPAGE_DIRECTORY
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English" ; The first language is the default language
  !insertmacro MUI_LANGUAGE "TradChinese"

LicenseLangString localizedLicenseFile ${LANG_ENGLISH} "${NSISDIR}\Examples\license_en.txt"
LicenseLangString localizedLicenseFile ${LANG_TRADCHINESE} "${NSISDIR}\Examples\license_zh_HK.txt"
;--------------------------------
;Reserve Files
  
  ;If you are using solid compression, files that are required before
  ;the actual installation should be stored first in the data block,
  ;because this will make your installer start faster.
  
  ;!insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
;Installer Sections

LangString ClientName ${LANG_ENGLISH} "Client"
LangString ClientName ${LANG_TRADCHINESE} "客戶端"

LangString ServerName ${LANG_ENGLISH} "Server"
LangString ServerName ${LANG_TRADCHINESE} "伺服器"

SectionGroup !$(ServerName) ServerPackage

  Section "CUDA 10.0"
    SectionIn RO
    SetOutPath "$INSTDIR"
    File "C:\Users\Alex\Desktop\cuda_10.0.130_win10_network.exe"
    ExecWait "$INSTDIR\cuda_10.0.130_win10_network.exe -s nvcc_10.0 cuobjdump_10.0 nvprune_10.0 cupti_10.0 gpu_library_advisor_10.0 memcheck_10.0 nvprof_10.0 cublas_10.0 cudart_10.0 cufft_10.0 curand_10.0 cusolver_10.0 cusparse_10.0 nvgraph_10.0 npp_10.0 nvrtc_10.0"
    Delete "$INSTDIR\cuda_10.0.130_win10_network.exe"
  SectionEnd

  Section /o "Video server"
      ExecWait "Dism /online /Enable-Feature /FeatureName:IIS-FTPExtensibility /All /Quiet /NoRestart"

      SetOutPath "C:\inetpub\wwwroot\app"
      File /r "C:\Users\Alex\Desktop\oiclayout\"

      SetOutPath "C:\ffmpeg"

      IfFileExists "$PROGRAMFILES64\NVIDIA Corporation" 0 +3
        File /r "C:\Users\Alex\Desktop\ffmpeg\"
        Goto +2
        File "C:\Users\Alex\Desktop\ffmpeg\ffmpeg.exe"
        
  SectionEnd

SectionGroupEnd

;--------------------------------
;Installer Functions

Function .onInit

  !insertmacro MUI_LANGDLL_DISPLAY

FunctionEnd

;--------------------------------
;Descriptions

  ;USE A LANGUAGE STRING IF YOU WANT YOUR DESCRIPTIONS TO BE LANGAUGE SPECIFIC

  ;Assign descriptions to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${ServerPackage} "The server."
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

 
;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  
  ExecWait '"C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\conda-env.exe" remove --name my-env'
  
  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR"

  ;DeleteRegKey /ifempty HKCU "Software\Modern UI Test"

SectionEnd

;--------------------------------
;Uninstaller Functions

Function un.onInit

  !insertmacro MUI_UNGETLANGUAGE
  
FunctionEnd