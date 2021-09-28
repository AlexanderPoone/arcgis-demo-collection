;NSIS Modern User Interface
;Multilingual Example Script
;Written by Joost Verburg

!pragma warning error all

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"
!define MUI_ICON "C:\Users\Alex\Desktop\favicon.ico"

BrandingText "Esri China (Hong Kong)"
;--------------------------------
;General

  ;Properly display all languages (Installer will not work on Windows 95, 98 or ME!)
  Unicode true

  ;Name and file
  Name "Preprocessing Utility for Oriented Images"
  OutFile "ptool_installer.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES64\Preprocessing Utility for Oriented Images"
  
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


SectionGroup /e !$(ClientName) ClientPackage

  Section "CUDA 10.0"
    SetOutPath "$INSTDIR"
    File "C:\Users\Alex\Desktop\cuda_10.0.130_win10_network.exe"
    ExecWait "$INSTDIR\cuda_10.0.130_win10_network.exe -s nvcc_10.0 cuobjdump_10.0 nvprune_10.0 cupti_10.0 gpu_library_advisor_10.0 memcheck_10.0 nvprof_10.0 cublas_10.0 cudart_10.0 cufft_10.0 curand_10.0 cusolver_10.0 cusparse_10.0 nvgraph_10.0 npp_10.0 nvrtc_10.0"
    Delete "$INSTDIR\cuda_10.0.130_win10_network.exe"
  SectionEnd

  Section "Preprocessing Tool"
    SectionIn RO
    SetOutPath "$INSTDIR\generative_inpainting_master"
    File /r "C:\Users\Alex\Desktop\generative_inpainting_master\"
    SetOutPath "$INSTDIR\Mask_RCNN-tensorflowone_sewer"
    File /r "C:\Users\Alex\Desktop\Mask_RCNN-tensorflowone_sewer\"
    SetOutPath "$INSTDIR"
    File "C:\Users\Alex\Desktop\favicon.ico"
    File "C:\Users\Alex\Desktop\publish\diag2.pyw"
    File "C:\Users\Alex\Desktop\preprocess_rc.py"
    File "C:\Users\Alex\Desktop\geckodriver.exe"
    File "C:\Users\Alex\Desktop\requirements.txt"
    File "C:\Users\Alex\Desktop\environment.yml"
    SetOutPath "C:\temp.gdb"
    File /r "C:\temp.gdb\"
    SetOutPath "C:\Template"
    File /r "C:\Template\"
    SetOutPath "C:\Image_Mgmt_Workflows"
    File /r "C:\Image_Mgmt_Workflows\"
    SetOutPath "C:\yolov5"
    File /r "C:\Users\Alex\Desktop\yolov5\"

    ;User should have the right
    SetOutPath "$PROFILE\Documents\ArcGIS\Projects\MyProject35\"
    File /r "C:\Users\Alex\Documents\ArcGIS\Projects\MyProject35"

    ;pano
    SetOutPath "$INSTDIR"
    File /r "C:\Users\Alex\Desktop\krpano-1.19-pr14\"
    File /r "C:\Users\Alex\Documents\Firefox64\"
    
    ;EnVar::SetHKLM
    EnVar::AddValue "Path" "$INSTDIR"

    ;ExecWait 'move /Y "$INSTDIR\temp.gdb" "C:\"'
    ;ExecWait 'move /Y "$INSTDIR\Template" "C:\"'
    
    SetOutPath "$INSTDIR"
    ExecWait '"C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\conda-env.exe" create -f "$INSTDIR\environment.yml"'
    ExecWait '"C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\python.exe" "C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\Scripts\pip-script.py" install -U -r "$INSTDIR\requirements.txt" --ignore-installed tifffile'

    SetOutPath "$PROGRAMFILES64\ArcGIS\Pro\bin\Python\envs\my-env\Lib\site-packages"
    File "C:\Users\Alex\Desktop\ArcGISPro.pth"
    
    ;ExecWait 'move /Y "$INSTDIR\ArcGISPro.pth" "C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\Lib\site-packages\ArcGISPro.pth"'
    
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\environment.yml"
    Delete "$INSTDIR\ArcGISPro.pth"
    CreateShortCut "$DESKTOP\Preprocessing Tool.lnk" "C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\python.exe" '"$INSTDIR\diag2.pyw"' "$INSTDIR\favicon.ico"

  SetOutPath "$INSTDIR"
  
  ;ADD YOUR OWN FILES HERE...
  
  ;Store installation folder
  ;WriteRegStr HKCU "Software\Preprocessing Utility for Oriented Images" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
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
    !insertmacro MUI_DESCRIPTION_TEXT ${ClientPackage} "The client."
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