; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=COrbitDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "find_orb.h"
VbxHeaderFile=find_orb.h
VbxImplementationFile=find_orb.cpp

ClassCount=7
Class1=CFind_orbApp
Class2=COrbitDlg

ResourceCount=13
Resource1=IDD_MAKE_EPHEMERIS
Class3=CEphem
Resource2=IDD_GENERIC_ENTRY
Class4=CAbout
Resource3=IDD_FIND_ORB
Class5=CGenericEntry
Resource4=IDD_ABOUT (English (U.S.))
Resource5=IDD_FIND_ORB (English (U.S.))
Resource6=IDD_SETTINGS
Resource7=IDD_GENERIC_ENTRY (English (U.S.))
Resource8=IDD_ABOUT
Class6=CMonteCarlo
Resource9=IDD_MONTE_CARLO
Resource10=IDR_POPUP1
Class7=CSettings
Resource11=IDD_MONTE_CARLO (English (U.S.))
Resource12=IDR_POPUP_SAVE_CLIP
Resource13=IDD_MAKE_EPHEMERIS (English (U.S.))

[CLS:CFind_orbApp]
Type=0
HeaderFile=find_orb.h
ImplementationFile=find_orb.cpp
Filter=N
LastObject=CFind_orbApp
BaseClass=CWinApp
VirtualFilter=AC

[CLS:COrbitDlg]
Type=0
HeaderFile=orbitdlg.h
ImplementationFile=orbitdlg.cpp
Filter=W
LastObject=COrbitDlg
BaseClass=CDialog
VirtualFilter=dWC

[CLS:CEphem]
Type=0
HeaderFile=ephem.h
ImplementationFile=ephem.cpp
Filter=D
LastObject=IDC_COPY
BaseClass=CDialog
VirtualFilter=dWC

[CLS:CAbout]
Type=0
HeaderFile=about.h
ImplementationFile=about.cpp
Filter=D
LastObject=CAbout

[DLG:IDD_ABOUT]
Type=1
Class=CAbout
ControlCount=8
Control1=IDOK,button,1342242817
Control2=IDC_STATIC1,static,1342308353
Control3=IDC_STATIC2,static,1342308353
Control4=IDC_STATIC3,static,1342308353
Control5=IDC_STATIC6,static,1342177283
Control6=IDC_STATIC4,static,1342308353
Control7=IDC_STATIC5,static,1342308353
Control8=IDC_STATIC7,static,1342308353

[DLG:IDD_MAKE_EPHEMERIS]
Type=1
Class=CEphem
ControlCount=18
Control1=IDC_EPHEM_DAY,edit,1350631552
Control2=IDC_EPHEM_MONTH,edit,1350631552
Control3=IDC_EPHEM_YEAR,edit,1350631552
Control4=IDC_EPHEM_NUM_STEPS,edit,1350631552
Control5=IDC_EPHEM_STEP,edit,1350631552
Control6=IDC_LAT,edit,1350631552
Control7=IDC_LON,edit,1350631552
Control8=IDC_GO,button,1342242816
Control9=IDC_SAVE,button,1342242816
Control10=IDOK,button,1342242817
Control11=IDC_STATIC1,static,1342308364
Control12=IDC_STATIC2,static,1342308364
Control13=IDC_STATIC3,static,1342308364
Control14=IDC_STATIC4,static,1342308364
Control15=IDC_STATIC5,static,1342308364
Control16=IDC_LIST1,listbox,1352728577
Control17=IDC_STATIC6,static,1342308364
Control18=IDC_STATIC7,static,1342308364

[DLG:IDD_FIND_ORB]
Type=1
Class=COrbitDlg
ControlCount=50
Control1=IDC_OPEN,button,1342242816
Control2=IDC_LIST_ASTEROIDS,listbox,1352728579
Control3=IDC_R1,edit,1350631552
Control4=IDC_R2,edit,1350631552
Control5=IDC_EPOCH,edit,1350631552
Control6=IDC_STEP_SIZE,edit,1350631552
Control7=IDC_COMETARY,button,1342242819
Control8=IDC_PLANET1,button,1342242819
Control9=IDC_PLANET2,button,1342242819
Control10=IDC_PLANET3,button,1342242819
Control11=IDC_PLANET10,button,1342242819
Control12=IDC_PLANET4,button,1342242819
Control13=IDC_PLANET5,button,1342242819
Control14=IDC_PLANET6,button,1342242819
Control15=IDC_PLANET7,button,1342242819
Control16=IDC_PLANET8,button,1342242819
Control17=IDC_PLANET9,button,1342242819
Control18=IDC_HERGET,button,1342242816
Control19=IDC_FULL_STEP,button,1342242816
Control20=IDC_VAISALA,button,1342242816
Control21=IDC_AUTO_SOLVE,button,1342242816
Control22=IDC_SAVE_RESIDS,button,1342242816
Control23=IDOK,button,1342242817
Control24=IDC_RESIDUALS,listbox,1352728705
Control25=IDC_STATIC1,static,1342308364
Control26=IDC_STATIC2,static,1342308364
Control27=IDC_STATIC3,static,1342308364
Control28=IDC_STATIC4,static,1342308364
Control29=IDC_STATIC5,static,1342308364
Control30=IDC_STATIC6,static,1342308364
Control31=IDC_STATIC7,button,1342177287
Control32=IDC_ORBIT1,static,1342308364
Control33=IDC_ORBIT2,static,1342308364
Control34=IDC_ORBIT3,static,1342308364
Control35=IDC_ORBIT4,static,1342308364
Control36=IDC_ORBIT5,static,1342308364
Control37=IDC_ORBIT6,static,1342308364
Control38=IDC_ORBIT7,static,1342308364
Control39=IDC_ORBIT8,static,1342308364
Control40=IDC_ORBIT9,static,1342308364
Control41=IDC_STATIC8,static,1342308364
Control42=IDC_STATION_INFO,static,1342308352
Control43=IDC_STATIC9,button,1342177287
Control44=IDC_ABOUT,button,1342242816
Control45=IDC_SAVE,button,1342242816
Control46=IDC_MAKE_EPHEMERIS,button,1342242816
Control47=IDC_MONTE_CARLO,button,1342242816
Control48=IDC_GAUSS,button,1342242816
Control49=IDC_WORST,button,1342242816
Control50=IDC_FILTER_OBS,button,1342242816

[CLS:CGenericEntry]
Type=0
HeaderFile=Generic.h
ImplementationFile=Generic.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CGenericEntry

[DLG:IDD_GENERIC_ENTRY]
Type=1
Class=CGenericEntry
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_EDIT1,edit,1350631552
Control4=IDC_STATIC1,static,1342308353

[DLG:IDD_ABOUT (English (U.S.))]
Type=1
Class=CAbout
ControlCount=8
Control1=IDOK,button,1342242817
Control2=IDC_STATIC1,static,1342308353
Control3=IDC_STATIC2,static,1342308353
Control4=IDC_STATIC3,static,1342308353
Control5=IDC_STATIC6,static,1342177283
Control6=IDC_VERSION_INFO,static,1342308353
Control7=IDC_STATIC5,static,1342308353
Control8=IDC_STATIC7,static,1342308353

[DLG:IDD_MAKE_EPHEMERIS (English (U.S.))]
Type=1
Class=CEphem
ControlCount=18
Control1=IDC_EPHEM_DAY,edit,1350631552
Control2=IDC_EPHEM_NUM_STEPS,edit,1350631552
Control3=IDC_EPHEM_STEP,edit,1350631552
Control4=IDC_LAT,edit,1350631552
Control5=IDC_LON,edit,1350631552
Control6=IDC_GO,button,1342242816
Control7=IDC_SAVE,button,1342242816
Control8=IDOK,button,1342242817
Control9=IDC_STATIC1,static,1342308354
Control10=IDC_STATIC4,static,1342308354
Control11=IDC_STATIC5,static,1342308354
Control12=IDC_LIST1,listbox,1352728577
Control13=IDC_STATIC6,static,1342308354
Control14=IDC_STATIC7,static,1342308354
Control15=IDC_MPEC,button,1342242816
Control16=IDC_MOTION,button,1342242819
Control17=IDC_ALT_AZ,button,1342242819
Control18=IDC_COPY,button,1342242816

[DLG:IDD_FIND_ORB (English (U.S.))]
Type=1
Class=COrbitDlg
ControlCount=42
Control1=IDC_OPEN,button,1342242816
Control2=IDC_LIST_ASTEROIDS,listbox,1352728577
Control3=IDC_R1,edit,1350631552
Control4=IDC_R2,edit,1350631552
Control5=IDC_EPOCH,edit,1350631552
Control6=IDC_ASTEROIDS,button,1342242819
Control7=IDC_PLANET1,button,1342242819
Control8=IDC_PLANET2,button,1342242819
Control9=IDC_PLANET3,button,1342242819
Control10=IDC_PLANET10,button,1342242819
Control11=IDC_PLANET4,button,1342242819
Control12=IDC_PLANET5,button,1342242819
Control13=IDC_PLANET6,button,1342242819
Control14=IDC_PLANET7,button,1342242819
Control15=IDC_PLANET8,button,1342242819
Control16=IDC_PLANET9,button,1342242819
Control17=IDC_HERGET,button,1342242816
Control18=IDC_FULL_STEP,button,1342242816
Control19=IDC_VAISALA,button,1342242816
Control20=IDC_AUTO_SOLVE,button,1342242816
Control21=IDC_SAVE_RESIDS,button,1342242816
Control22=IDOK,button,1342242817
Control23=IDC_RESIDUALS,listbox,1352730753
Control24=IDC_STATIC1,static,1342308364
Control25=IDC_STATIC2,static,1342308364
Control26=IDC_STATIC3,static,1342308364
Control27=IDC_STATIC4,static,1342308364
Control28=IDC_ORBITAL_ELEMENTS,button,1342193671
Control29=IDC_ORBIT1,static,1342308364
Control30=IDC_STATIC8,static,1342308364
Control31=IDC_STATION_INFO,static,1342308364
Control32=IDC_STATIC9,button,1342177287
Control33=IDC_ABOUT,button,1342242816
Control34=IDC_SAVE,button,1342242816
Control35=IDC_MAKE_EPHEMERIS,button,1342242816
Control36=IDC_MONTE_CARLO,button,1342242816
Control37=IDC_GAUSS,button,1342242816
Control38=IDC_WORST,button,1342242816
Control39=IDC_FILTER_OBS,button,1342242816
Control40=IDC_SETTINGS,button,1342242816
Control41=IDC_TOGGLE_OBS,button,1342242816
Control42=IDC_SET_WEIGHT,button,1342242816

[DLG:IDD_GENERIC_ENTRY (English (U.S.))]
Type=1
Class=CGenericEntry
ControlCount=4
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_EDIT1,edit,1350631552
Control4=IDC_STATIC1,static,1342308353

[DLG:IDD_MONTE_CARLO]
Type=1
Class=CMonteCarlo
ControlCount=13
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_GAUSS_TEXT,static,1342308354
Control4=IDC_GAUSSIAN,edit,1350631552
Control5=IDC_STATISTICAL,button,1342242819
Control6=IDC_MIN_RANGE_TEXT,static,1342308354
Control7=IDC_MAX_RANGE_TEXT,static,1342308354
Control8=IDC_MIN_RANGE,edit,1350631552
Control9=IDC_MAX_RANGE,edit,1350631552
Control10=IDC_ECC_TEXT,static,1342308354
Control11=IDC_INCL_TEXT,static,1342308354
Control12=IDC_MAX_ECC,edit,1350631552
Control13=IDC_MAX_INCL,edit,1350631552

[CLS:CMonteCarlo]
Type=0
HeaderFile=Monte.h
ImplementationFile=Monte.cpp
BaseClass=CDialog
Filter=D
LastObject=CMonteCarlo
VirtualFilter=dWC

[DLG:IDD_MONTE_CARLO (English (U.S.))]
Type=1
Class=CMonteCarlo
ControlCount=13
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_GAUSS_TEXT,static,1342308354
Control4=IDC_GAUSSIAN,edit,1350631552
Control5=IDC_STATISTICAL,button,1342242819
Control6=IDC_MIN_RANGE_TEXT,static,1342308354
Control7=IDC_MAX_RANGE_TEXT,static,1342308354
Control8=IDC_MIN_RANGE,edit,1350631552
Control9=IDC_MAX_RANGE,edit,1350631552
Control10=IDC_ECC_TEXT,static,1342308354
Control11=IDC_INCL_TEXT,static,1342308354
Control12=IDC_MAX_ECC,edit,1350631552
Control13=IDC_MAX_INCL,edit,1350631552

[DLG:IDD_SETTINGS]
Type=1
Class=CSettings
ControlCount=17
Control1=IDOK,button,1342242817
Control2=IDCANCEL,button,1342242816
Control3=IDC_STATIC1,static,1342308354
Control4=IDC_CONSTRAINTS,edit,1350631552
Control5=IDC_STATIC2,static,1342308354
Control6=IDC_REFERENCE,edit,1350631552
Control7=IDC_STATIC3,static,1342308354
Control8=IDC_MONTE_NOISE,edit,1350631552
Control9=IDC_STATIC4,static,1342308354
Control10=IDC_MAX_RESIDUAL,edit,1350631552
Control11=IDC_STATIC5,static,1342308354
Control12=IDC_ELEMENT_PRECISION,edit,1350631552
Control13=IDC_HELIOCENTRIC,button,1342242819
Control14=IDC_SRP,button,1342242819
Control15=IDC_STATIC,button,1342177287
Control16=IDC_RADIO1,button,1342308361
Control17=IDC_RADIO2,button,1342177289

[CLS:CSettings]
Type=0
HeaderFile=Settings.h
ImplementationFile=Settings.cpp
BaseClass=CDialog
Filter=D
VirtualFilter=dWC
LastObject=CSettings

[MNU:IDR_POPUP_SAVE_CLIP]
Type=1
Class=COrbitDlg
Command1=IDM_SAVE_TO_FILE
Command2=IDM_COPY_TO_CLIPBOARD
CommandCount=2

[MNU:IDR_POPUP1]
Type=1
Class=COrbitDlg
CommandCount=0

