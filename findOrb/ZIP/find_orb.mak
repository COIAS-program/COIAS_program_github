# Microsoft Developer Studio Generated NMAKE File, Based on Find_orb.dsp
!IF "$(CFG)" == ""
CFG=Find_orb - Win32 Debug
!MESSAGE No configuration specified. Defaulting to Find_orb - Win32 Debug.
!ENDIF 

!IF "$(CFG)" != "Find_orb - Win32 Release" && "$(CFG)" !=\
 "Find_orb - Win32 Debug"
!MESSAGE Invalid configuration "$(CFG)" specified.
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "Find_orb.mak" CFG="Find_orb - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "Find_orb - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "Find_orb - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE 
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

!IF  "$(CFG)" == "Find_orb - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

!IF "$(RECURSE)" == "0" 

ALL : "$(OUTDIR)\Find_orb.exe" "$(OUTDIR)\Find_orb.bsc"

!ELSE 

ALL : "$(OUTDIR)\Find_orb.exe" "$(OUTDIR)\Find_orb.bsc"

!ENDIF 

CLEAN :
	-@erase "$(INTDIR)\About.obj"
	-@erase "$(INTDIR)\About.sbr"
	-@erase "$(INTDIR)\collide.obj"
	-@erase "$(INTDIR)\collide.sbr"
	-@erase "$(INTDIR)\Conv_ele.obj"
	-@erase "$(INTDIR)\Conv_ele.sbr"
	-@erase "$(INTDIR)\elem2tle.obj"
	-@erase "$(INTDIR)\elem2tle.sbr"
	-@erase "$(INTDIR)\elem_out.obj"
	-@erase "$(INTDIR)\elem_out.sbr"
	-@erase "$(INTDIR)\Ephem.obj"
	-@erase "$(INTDIR)\Ephem.sbr"
	-@erase "$(INTDIR)\Ephem0.obj"
	-@erase "$(INTDIR)\Ephem0.sbr"
	-@erase "$(INTDIR)\Find_orb.obj"
	-@erase "$(INTDIR)\Find_orb.pch"
	-@erase "$(INTDIR)\Find_orb.res"
	-@erase "$(INTDIR)\Find_orb.sbr"
	-@erase "$(INTDIR)\Gauss.obj"
	-@erase "$(INTDIR)\Gauss.sbr"
	-@erase "$(INTDIR)\Generic.obj"
	-@erase "$(INTDIR)\Generic.sbr"
	-@erase "$(INTDIR)\Get_pert.obj"
	-@erase "$(INTDIR)\Get_pert.sbr"
	-@erase "$(INTDIR)\Jpleph.obj"
	-@erase "$(INTDIR)\Jpleph.sbr"
	-@erase "$(INTDIR)\Lsquare.obj"
	-@erase "$(INTDIR)\Lsquare.sbr"
	-@erase "$(INTDIR)\moid4.obj"
	-@erase "$(INTDIR)\moid4.sbr"
	-@erase "$(INTDIR)\Monte.obj"
	-@erase "$(INTDIR)\Monte.sbr"
	-@erase "$(INTDIR)\monte0.obj"
	-@erase "$(INTDIR)\monte0.sbr"
	-@erase "$(INTDIR)\Mpc_obs.obj"
	-@erase "$(INTDIR)\Mpc_obs.sbr"
	-@erase "$(INTDIR)\orb_fun2.obj"
	-@erase "$(INTDIR)\orb_fun2.sbr"
	-@erase "$(INTDIR)\Orb_func.obj"
	-@erase "$(INTDIR)\Orb_func.sbr"
	-@erase "$(INTDIR)\Orbitdlg.obj"
	-@erase "$(INTDIR)\Orbitdlg.sbr"
	-@erase "$(INTDIR)\pl_cache.obj"
	-@erase "$(INTDIR)\pl_cache.sbr"
	-@erase "$(INTDIR)\Roots.obj"
	-@erase "$(INTDIR)\Roots.sbr"
	-@erase "$(INTDIR)\Runge.obj"
	-@erase "$(INTDIR)\Runge.sbr"
	-@erase "$(INTDIR)\Settings.obj"
	-@erase "$(INTDIR)\Settings.sbr"
	-@erase "$(INTDIR)\sm_vsop.obj"
	-@erase "$(INTDIR)\sm_vsop.sbr"
	-@erase "$(INTDIR)\Sr.obj"
	-@erase "$(INTDIR)\Sr.sbr"
	-@erase "$(INTDIR)\Stdafx.obj"
	-@erase "$(INTDIR)\Stdafx.sbr"
	-@erase "$(INTDIR)\tle_out.obj"
	-@erase "$(INTDIR)\tle_out.sbr"
	-@erase "$(INTDIR)\vc50.idb"
	-@erase "$(INTDIR)\weight.obj"
	-@erase "$(INTDIR)\weight.sbr"
	-@erase "$(OUTDIR)\Find_orb.bsc"
	-@erase "$(OUTDIR)\Find_orb.exe"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fp"$(INTDIR)\Find_orb.pch" /Yu"STDAFX.H" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD\
 /c 
CPP_OBJS=.\Release/
CPP_SBRS=.\Release/

.c{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

MTL=midl.exe
MTL_PROJ=/nologo /D "NDEBUG" /mktyplib203 /o NUL /win32 
RSC=rc.exe
RSC_PROJ=/l 0x409 /fo"$(INTDIR)\Find_orb.res" /d "NDEBUG" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\Find_orb.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\About.sbr" \
	"$(INTDIR)\collide.sbr" \
	"$(INTDIR)\Conv_ele.sbr" \
	"$(INTDIR)\elem2tle.sbr" \
	"$(INTDIR)\elem_out.sbr" \
	"$(INTDIR)\Ephem.sbr" \
	"$(INTDIR)\Ephem0.sbr" \
	"$(INTDIR)\Find_orb.sbr" \
	"$(INTDIR)\Gauss.sbr" \
	"$(INTDIR)\Generic.sbr" \
	"$(INTDIR)\Get_pert.sbr" \
	"$(INTDIR)\Jpleph.sbr" \
	"$(INTDIR)\Lsquare.sbr" \
	"$(INTDIR)\moid4.sbr" \
	"$(INTDIR)\Monte.sbr" \
	"$(INTDIR)\monte0.sbr" \
	"$(INTDIR)\Mpc_obs.sbr" \
	"$(INTDIR)\orb_fun2.sbr" \
	"$(INTDIR)\Orb_func.sbr" \
	"$(INTDIR)\Orbitdlg.sbr" \
	"$(INTDIR)\pl_cache.sbr" \
	"$(INTDIR)\Roots.sbr" \
	"$(INTDIR)\Runge.sbr" \
	"$(INTDIR)\Settings.sbr" \
	"$(INTDIR)\sm_vsop.sbr" \
	"$(INTDIR)\Sr.sbr" \
	"$(INTDIR)\Stdafx.sbr" \
	"$(INTDIR)\tle_out.sbr" \
	"$(INTDIR)\weight.sbr"

"$(OUTDIR)\Find_orb.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=oldnames.lib \lunar\posttest\lunar.lib /nologo /stack:0x8800\
 /subsystem:windows /incremental:no /pdb:"$(OUTDIR)\Find_orb.pdb" /machine:IX86\
 /def:".\Find_orb.def" /out:"$(OUTDIR)\Find_orb.exe" 
DEF_FILE= \
	".\Find_orb.def"
LINK32_OBJS= \
	"$(INTDIR)\About.obj" \
	"$(INTDIR)\collide.obj" \
	"$(INTDIR)\Conv_ele.obj" \
	"$(INTDIR)\elem2tle.obj" \
	"$(INTDIR)\elem_out.obj" \
	"$(INTDIR)\Ephem.obj" \
	"$(INTDIR)\Ephem0.obj" \
	"$(INTDIR)\Find_orb.obj" \
	"$(INTDIR)\Find_orb.res" \
	"$(INTDIR)\Gauss.obj" \
	"$(INTDIR)\Generic.obj" \
	"$(INTDIR)\Get_pert.obj" \
	"$(INTDIR)\Jpleph.obj" \
	"$(INTDIR)\Lsquare.obj" \
	"$(INTDIR)\moid4.obj" \
	"$(INTDIR)\Monte.obj" \
	"$(INTDIR)\monte0.obj" \
	"$(INTDIR)\Mpc_obs.obj" \
	"$(INTDIR)\orb_fun2.obj" \
	"$(INTDIR)\Orb_func.obj" \
	"$(INTDIR)\Orbitdlg.obj" \
	"$(INTDIR)\pl_cache.obj" \
	"$(INTDIR)\Roots.obj" \
	"$(INTDIR)\Runge.obj" \
	"$(INTDIR)\Settings.obj" \
	"$(INTDIR)\sm_vsop.obj" \
	"$(INTDIR)\Sr.obj" \
	"$(INTDIR)\Stdafx.obj" \
	"$(INTDIR)\tle_out.obj" \
	"$(INTDIR)\weight.obj"

"$(OUTDIR)\Find_orb.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

SOURCE=$(InputPath)
DS_POSTBUILD_DEP=$(INTDIR)\postbld.dep

ALL : $(DS_POSTBUILD_DEP)

# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

$(DS_POSTBUILD_DEP) : "$(OUTDIR)\Find_orb.exe" "$(OUTDIR)\Find_orb.bsc"
   copy release\find_orb.exe find_o32.exe
	echo Helper for Post-build step > "$(DS_POSTBUILD_DEP)"

!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

!IF "$(RECURSE)" == "0" 

ALL : "$(OUTDIR)\Find_orb.exe" "$(OUTDIR)\Find_orb.bsc"

!ELSE 

ALL : "$(OUTDIR)\Find_orb.exe" "$(OUTDIR)\Find_orb.bsc"

!ENDIF 

CLEAN :
	-@erase "$(INTDIR)\About.obj"
	-@erase "$(INTDIR)\About.sbr"
	-@erase "$(INTDIR)\collide.obj"
	-@erase "$(INTDIR)\collide.sbr"
	-@erase "$(INTDIR)\Conv_ele.obj"
	-@erase "$(INTDIR)\Conv_ele.sbr"
	-@erase "$(INTDIR)\elem2tle.obj"
	-@erase "$(INTDIR)\elem2tle.sbr"
	-@erase "$(INTDIR)\elem_out.obj"
	-@erase "$(INTDIR)\elem_out.sbr"
	-@erase "$(INTDIR)\Ephem.obj"
	-@erase "$(INTDIR)\Ephem.sbr"
	-@erase "$(INTDIR)\Ephem0.obj"
	-@erase "$(INTDIR)\Ephem0.sbr"
	-@erase "$(INTDIR)\Find_orb.obj"
	-@erase "$(INTDIR)\Find_orb.pch"
	-@erase "$(INTDIR)\Find_orb.res"
	-@erase "$(INTDIR)\Find_orb.sbr"
	-@erase "$(INTDIR)\Gauss.obj"
	-@erase "$(INTDIR)\Gauss.sbr"
	-@erase "$(INTDIR)\Generic.obj"
	-@erase "$(INTDIR)\Generic.sbr"
	-@erase "$(INTDIR)\Get_pert.obj"
	-@erase "$(INTDIR)\Get_pert.sbr"
	-@erase "$(INTDIR)\Jpleph.obj"
	-@erase "$(INTDIR)\Jpleph.sbr"
	-@erase "$(INTDIR)\Lsquare.obj"
	-@erase "$(INTDIR)\Lsquare.sbr"
	-@erase "$(INTDIR)\moid4.obj"
	-@erase "$(INTDIR)\moid4.sbr"
	-@erase "$(INTDIR)\Monte.obj"
	-@erase "$(INTDIR)\Monte.sbr"
	-@erase "$(INTDIR)\monte0.obj"
	-@erase "$(INTDIR)\monte0.sbr"
	-@erase "$(INTDIR)\Mpc_obs.obj"
	-@erase "$(INTDIR)\Mpc_obs.sbr"
	-@erase "$(INTDIR)\orb_fun2.obj"
	-@erase "$(INTDIR)\orb_fun2.sbr"
	-@erase "$(INTDIR)\Orb_func.obj"
	-@erase "$(INTDIR)\Orb_func.sbr"
	-@erase "$(INTDIR)\Orbitdlg.obj"
	-@erase "$(INTDIR)\Orbitdlg.sbr"
	-@erase "$(INTDIR)\pl_cache.obj"
	-@erase "$(INTDIR)\pl_cache.sbr"
	-@erase "$(INTDIR)\Roots.obj"
	-@erase "$(INTDIR)\Roots.sbr"
	-@erase "$(INTDIR)\Runge.obj"
	-@erase "$(INTDIR)\Runge.sbr"
	-@erase "$(INTDIR)\Settings.obj"
	-@erase "$(INTDIR)\Settings.sbr"
	-@erase "$(INTDIR)\sm_vsop.obj"
	-@erase "$(INTDIR)\sm_vsop.sbr"
	-@erase "$(INTDIR)\Sr.obj"
	-@erase "$(INTDIR)\Sr.sbr"
	-@erase "$(INTDIR)\Stdafx.obj"
	-@erase "$(INTDIR)\Stdafx.sbr"
	-@erase "$(INTDIR)\tle_out.obj"
	-@erase "$(INTDIR)\tle_out.sbr"
	-@erase "$(INTDIR)\vc50.idb"
	-@erase "$(INTDIR)\vc50.pdb"
	-@erase "$(INTDIR)\weight.obj"
	-@erase "$(INTDIR)\weight.sbr"
	-@erase "$(OUTDIR)\Find_orb.bsc"
	-@erase "$(OUTDIR)\Find_orb.exe"
	-@erase "$(OUTDIR)\Find_orb.map"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D "_AFXDLL"\
 /FR"$(INTDIR)\\" /Fp"$(INTDIR)\Find_orb.pch" /Yu"STDAFX.H" /Fo"$(INTDIR)\\"\
 /Fd"$(INTDIR)\\" /FD /c 
CPP_OBJS=.\Debug/
CPP_SBRS=.\Debug/

.c{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(CPP_OBJS)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(CPP_SBRS)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

MTL=midl.exe
MTL_PROJ=/nologo /D "_DEBUG" /mktyplib203 /o NUL /win32 
RSC=rc.exe
RSC_PROJ=/l 0x419 /fo"$(INTDIR)\Find_orb.res" /d "_DEBUG" /d "_AFXDLL" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\Find_orb.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\About.sbr" \
	"$(INTDIR)\collide.sbr" \
	"$(INTDIR)\Conv_ele.sbr" \
	"$(INTDIR)\elem2tle.sbr" \
	"$(INTDIR)\elem_out.sbr" \
	"$(INTDIR)\Ephem.sbr" \
	"$(INTDIR)\Ephem0.sbr" \
	"$(INTDIR)\Find_orb.sbr" \
	"$(INTDIR)\Gauss.sbr" \
	"$(INTDIR)\Generic.sbr" \
	"$(INTDIR)\Get_pert.sbr" \
	"$(INTDIR)\Jpleph.sbr" \
	"$(INTDIR)\Lsquare.sbr" \
	"$(INTDIR)\moid4.sbr" \
	"$(INTDIR)\Monte.sbr" \
	"$(INTDIR)\monte0.sbr" \
	"$(INTDIR)\Mpc_obs.sbr" \
	"$(INTDIR)\orb_fun2.sbr" \
	"$(INTDIR)\Orb_func.sbr" \
	"$(INTDIR)\Orbitdlg.sbr" \
	"$(INTDIR)\pl_cache.sbr" \
	"$(INTDIR)\Roots.sbr" \
	"$(INTDIR)\Runge.sbr" \
	"$(INTDIR)\Settings.sbr" \
	"$(INTDIR)\sm_vsop.sbr" \
	"$(INTDIR)\Sr.sbr" \
	"$(INTDIR)\Stdafx.sbr" \
	"$(INTDIR)\tle_out.sbr" \
	"$(INTDIR)\weight.sbr"

"$(OUTDIR)\Find_orb.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=oldnames.lib \lunar\posttest\lunar.lib /nologo /stack:0x8800\
 /subsystem:windows /profile /map:"$(INTDIR)\Find_orb.map" /debug /machine:IX86\
 /def:".\Find_orb.def" /out:"$(OUTDIR)\Find_orb.exe" 
DEF_FILE= \
	".\Find_orb.def"
LINK32_OBJS= \
	"$(INTDIR)\About.obj" \
	"$(INTDIR)\collide.obj" \
	"$(INTDIR)\Conv_ele.obj" \
	"$(INTDIR)\elem2tle.obj" \
	"$(INTDIR)\elem_out.obj" \
	"$(INTDIR)\Ephem.obj" \
	"$(INTDIR)\Ephem0.obj" \
	"$(INTDIR)\Find_orb.obj" \
	"$(INTDIR)\Find_orb.res" \
	"$(INTDIR)\Gauss.obj" \
	"$(INTDIR)\Generic.obj" \
	"$(INTDIR)\Get_pert.obj" \
	"$(INTDIR)\Jpleph.obj" \
	"$(INTDIR)\Lsquare.obj" \
	"$(INTDIR)\moid4.obj" \
	"$(INTDIR)\Monte.obj" \
	"$(INTDIR)\monte0.obj" \
	"$(INTDIR)\Mpc_obs.obj" \
	"$(INTDIR)\orb_fun2.obj" \
	"$(INTDIR)\Orb_func.obj" \
	"$(INTDIR)\Orbitdlg.obj" \
	"$(INTDIR)\pl_cache.obj" \
	"$(INTDIR)\Roots.obj" \
	"$(INTDIR)\Runge.obj" \
	"$(INTDIR)\Settings.obj" \
	"$(INTDIR)\sm_vsop.obj" \
	"$(INTDIR)\Sr.obj" \
	"$(INTDIR)\Stdafx.obj" \
	"$(INTDIR)\tle_out.obj" \
	"$(INTDIR)\weight.obj"

"$(OUTDIR)\Find_orb.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ENDIF 


!IF "$(CFG)" == "Find_orb - Win32 Release" || "$(CFG)" ==\
 "Find_orb - Win32 Debug"
SOURCE=.\About.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ABOUT=\
	".\about.h"\
	".\find_orb.h"\
	".\stdafx.h"\
	
CPP_SWITCHES=/nologo /Zp8 /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG"\
 /FR"$(INTDIR)\\" /Fp"$(INTDIR)\Find_orb.pch" /Yu"STDAFX.H" /Fo"$(INTDIR)\\"\
 /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\About.obj"	"$(INTDIR)\About.sbr" : $(SOURCE) $(DEP_CPP_ABOUT)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ABOUT=\
	".\about.h"\
	".\find_orb.h"\
	".\stdafx.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\Find_orb.pch" /Yu"STDAFX.H"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\About.obj"	"$(INTDIR)\About.sbr" : $(SOURCE) $(DEP_CPP_ABOUT)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\collide.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_COLLI=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\collide.obj"	"$(INTDIR)\collide.sbr" : $(SOURCE) $(DEP_CPP_COLLI)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_COLLI=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\collide.obj"	"$(INTDIR)\collide.sbr" : $(SOURCE) $(DEP_CPP_COLLI)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Conv_ele.cpp
DEP_CPP_CONV_=\
	"..\myincl\afuncs.h"\
	"..\myincl\watdefs.h"\
	

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Conv_ele.obj"	"$(INTDIR)\Conv_ele.sbr" : $(SOURCE) $(DEP_CPP_CONV_)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Conv_ele.obj"	"$(INTDIR)\Conv_ele.sbr" : $(SOURCE) $(DEP_CPP_CONV_)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\elem2tle.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ELEM2=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\norad.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\elem2tle.obj"	"$(INTDIR)\elem2tle.sbr" : $(SOURCE) $(DEP_CPP_ELEM2)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ELEM2=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\norad.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\elem2tle.obj"	"$(INTDIR)\elem2tle.sbr" : $(SOURCE) $(DEP_CPP_ELEM2)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\elem_out.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ELEM_=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\showelem.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\elem_out.obj"	"$(INTDIR)\elem_out.sbr" : $(SOURCE) $(DEP_CPP_ELEM_)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ELEM_=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\showelem.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\elem_out.obj"	"$(INTDIR)\elem_out.sbr" : $(SOURCE) $(DEP_CPP_ELEM_)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Ephem.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_EPHEM=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\ephem.h"\
	".\find_orb.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\stdafx.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Ephem.obj"	"$(INTDIR)\Ephem.sbr" : $(SOURCE) $(DEP_CPP_EPHEM)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_EPHEM=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\ephem.h"\
	".\find_orb.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\stdafx.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\Find_orb.pch" /Yu"STDAFX.H"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Ephem.obj"	"$(INTDIR)\Ephem.sbr" : $(SOURCE) $(DEP_CPP_EPHEM)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Ephem0.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_EPHEM0=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Ephem0.obj"	"$(INTDIR)\Ephem0.sbr" : $(SOURCE) $(DEP_CPP_EPHEM0)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_EPHEM0=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /O2 /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Ephem0.obj"	"$(INTDIR)\Ephem0.sbr" : $(SOURCE) $(DEP_CPP_EPHEM0)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Find_orb.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_FIND_=\
	".\find_orb.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Find_orb.obj"	"$(INTDIR)\Find_orb.sbr" : $(SOURCE) $(DEP_CPP_FIND_)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_FIND_=\
	".\find_orb.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Find_orb.obj"	"$(INTDIR)\Find_orb.sbr" : $(SOURCE) $(DEP_CPP_FIND_)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ENDIF 

SOURCE=.\Find_orb.rc
DEP_RSC_FIND_O=\
	".\RES\FIND_ORB.ICO"\
	".\res\find_orb.rc2"\
	

"$(INTDIR)\Find_orb.res" : $(SOURCE) $(DEP_RSC_FIND_O) "$(INTDIR)"
	$(RSC) $(RSC_PROJ) $(SOURCE)


SOURCE=.\Gauss.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_GAUSS=\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Gauss.obj"	"$(INTDIR)\Gauss.sbr" : $(SOURCE) $(DEP_CPP_GAUSS)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_GAUSS=\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Gauss.obj"	"$(INTDIR)\Gauss.sbr" : $(SOURCE) $(DEP_CPP_GAUSS)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Generic.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_GENER=\
	".\find_orb.h"\
	".\Generic.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Generic.obj"	"$(INTDIR)\Generic.sbr" : $(SOURCE) $(DEP_CPP_GENER)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_GENER=\
	".\find_orb.h"\
	".\Generic.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Generic.obj"	"$(INTDIR)\Generic.sbr" : $(SOURCE) $(DEP_CPP_GENER)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ENDIF 

SOURCE=.\Get_pert.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_GET_P=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Get_pert.obj"	"$(INTDIR)\Get_pert.sbr" : $(SOURCE) $(DEP_CPP_GET_P)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_GET_P=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Get_pert.obj"	"$(INTDIR)\Get_pert.sbr" : $(SOURCE) $(DEP_CPP_GET_P)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=..\jpl\pl\Jpleph.cpp
DEP_CPP_JPLEP=\
	"..\jpl\pl\jpl_int.h"\
	"..\myincl\jpleph.h"\
	{$(INCLUDE)}"stdintvc.h"\
	

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Jpleph.obj"	"$(INTDIR)\Jpleph.sbr" : $(SOURCE) $(DEP_CPP_JPLEP)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Jpleph.obj"	"$(INTDIR)\Jpleph.sbr" : $(SOURCE) $(DEP_CPP_JPLEP)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=..\Image\Lsquare.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_LSQUA=\
	"..\myincl\lsquare.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Lsquare.obj"	"$(INTDIR)\Lsquare.sbr" : $(SOURCE) $(DEP_CPP_LSQUA)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_LSQUA=\
	"..\myincl\checkmem.h"\
	"..\myincl\lsquare.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Lsquare.obj"	"$(INTDIR)\Lsquare.sbr" : $(SOURCE) $(DEP_CPP_LSQUA)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\moid4.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_MOID4=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\moid4.obj"	"$(INTDIR)\moid4.sbr" : $(SOURCE) $(DEP_CPP_MOID4)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_MOID4=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\moid4.obj"	"$(INTDIR)\moid4.sbr" : $(SOURCE) $(DEP_CPP_MOID4)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Monte.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_MONTE=\
	".\find_orb.h"\
	".\Monte.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Monte.obj"	"$(INTDIR)\Monte.sbr" : $(SOURCE) $(DEP_CPP_MONTE)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_MONTE=\
	".\find_orb.h"\
	".\Monte.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Monte.obj"	"$(INTDIR)\Monte.sbr" : $(SOURCE) $(DEP_CPP_MONTE)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ENDIF 

SOURCE=.\monte0.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_MONTE0=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	".\monte0.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\monte0.obj"	"$(INTDIR)\monte0.sbr" : $(SOURCE) $(DEP_CPP_MONTE0)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_MONTE0=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	".\monte0.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\monte0.obj"	"$(INTDIR)\monte0.sbr" : $(SOURCE) $(DEP_CPP_MONTE0)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Mpc_obs.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_MPC_O=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	".\weight.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Mpc_obs.obj"	"$(INTDIR)\Mpc_obs.sbr" : $(SOURCE) $(DEP_CPP_MPC_O)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_MPC_O=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	".\weight.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Mpc_obs.obj"	"$(INTDIR)\Mpc_obs.sbr" : $(SOURCE) $(DEP_CPP_MPC_O)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\orb_fun2.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ORB_F=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\orb_fun2.obj"	"$(INTDIR)\orb_fun2.sbr" : $(SOURCE) $(DEP_CPP_ORB_F)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ORB_F=\
	"..\myincl\comets.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\orb_fun2.obj"	"$(INTDIR)\orb_fun2.sbr" : $(SOURCE) $(DEP_CPP_ORB_F)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Orb_func.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ORB_FU=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lsquare.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Orb_func.obj"	"$(INTDIR)\Orb_func.sbr" : $(SOURCE) $(DEP_CPP_ORB_FU)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ORB_FU=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\lsquare.h"\
	"..\myincl\mycurses.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
NODEP_CPP_ORB_FU=\
	".\curses.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Orb_func.obj"	"$(INTDIR)\Orb_func.sbr" : $(SOURCE) $(DEP_CPP_ORB_FU)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Orbitdlg.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_ORBIT=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\watdefs.h"\
	".\about.h"\
	".\ephem.h"\
	".\find_orb.h"\
	".\Generic.h"\
	".\monte0.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\Settings.h"\
	".\stdafx.h"\
	".\weight.h"\
	{$(INCLUDE)}"stdintvc.h"\
	

"$(INTDIR)\Orbitdlg.obj"	"$(INTDIR)\Orbitdlg.sbr" : $(SOURCE) $(DEP_CPP_ORBIT)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_ORBIT=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\date.h"\
	"..\myincl\watdefs.h"\
	".\about.h"\
	".\ephem.h"\
	".\find_orb.h"\
	".\Generic.h"\
	".\monte0.h"\
	".\mpc_obs.h"\
	".\orbitdlg.h"\
	".\Settings.h"\
	".\stdafx.h"\
	".\weight.h"\
	{$(INCLUDE)}"stdintvc.h"\
	{$(INCLUDE)}"sys\stat.h"\
	{$(INCLUDE)}"sys\types.h"\
	

"$(INTDIR)\Orbitdlg.obj"	"$(INTDIR)\Orbitdlg.sbr" : $(SOURCE) $(DEP_CPP_ORBIT)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ENDIF 

SOURCE=.\pl_cache.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_PL_CA=\
	"..\myincl\afuncs.h"\
	"..\myincl\jpleph.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\pl_cache.obj"	"$(INTDIR)\pl_cache.sbr" : $(SOURCE) $(DEP_CPP_PL_CA)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_PL_CA=\
	"..\myincl\afuncs.h"\
	"..\myincl\jpleph.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\pl_cache.obj"	"$(INTDIR)\pl_cache.sbr" : $(SOURCE) $(DEP_CPP_PL_CA)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Roots.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Roots.obj"	"$(INTDIR)\Roots.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Roots.obj"	"$(INTDIR)\Roots.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Runge.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_RUNGE=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Runge.obj"	"$(INTDIR)\Runge.sbr" : $(SOURCE) $(DEP_CPP_RUNGE)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_RUNGE=\
	"..\myincl\afuncs.h"\
	"..\myincl\comets.h"\
	"..\myincl\lunar.h"\
	"..\myincl\watdefs.h"\
	".\mpc_obs.h"\
	{$(INCLUDE)}"stdintvc.h"\
	
CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Runge.obj"	"$(INTDIR)\Runge.sbr" : $(SOURCE) $(DEP_CPP_RUNGE)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Settings.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

DEP_CPP_SETTI=\
	".\find_orb.h"\
	".\Settings.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Settings.obj"	"$(INTDIR)\Settings.sbr" : $(SOURCE) $(DEP_CPP_SETTI)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

DEP_CPP_SETTI=\
	".\find_orb.h"\
	".\Settings.h"\
	".\stdafx.h"\
	

"$(INTDIR)\Settings.obj"	"$(INTDIR)\Settings.sbr" : $(SOURCE) $(DEP_CPP_SETTI)\
 "$(INTDIR)" "$(INTDIR)\Find_orb.pch"


!ENDIF 

SOURCE=.\sm_vsop.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\sm_vsop.obj"	"$(INTDIR)\sm_vsop.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\sm_vsop.obj"	"$(INTDIR)\sm_vsop.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Sr.cpp

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Sr.obj"	"$(INTDIR)\Sr.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Sr.obj"	"$(INTDIR)\Sr.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\Stdafx.cpp
DEP_CPP_STDAF=\
	".\stdafx.h"\
	

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fp"$(INTDIR)\Find_orb.pch" /Yc"STDAFX.H" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD\
 /c 

"$(INTDIR)\Stdafx.obj"	"$(INTDIR)\Stdafx.sbr"	"$(INTDIR)\Find_orb.pch" : \
$(SOURCE) $(DEP_CPP_STDAF) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\Find_orb.pch" /Yc"STDAFX.H"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\Stdafx.obj"	"$(INTDIR)\Stdafx.sbr"	"$(INTDIR)\Find_orb.pch" : \
$(SOURCE) $(DEP_CPP_STDAF) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=..\sattest\neoklis\tle_out.cpp
DEP_CPP_TLE_O=\
	"..\sattest\neoklis\norad.h"\
	

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\tle_out.obj"	"$(INTDIR)\tle_out.sbr" : $(SOURCE) $(DEP_CPP_TLE_O)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\tle_out.obj"	"$(INTDIR)\tle_out.sbr" : $(SOURCE) $(DEP_CPP_TLE_O)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

SOURCE=.\weight.cpp
DEP_CPP_WEIGH=\
	"..\myincl\date.h"\
	"..\myincl\watdefs.h"\
	".\weight.h"\
	

!IF  "$(CFG)" == "Find_orb - Win32 Release"

CPP_SWITCHES=/nologo /MT /W3 /GX /O1 /I "\myincl" /D "NDEBUG" /FR"$(INTDIR)\\"\
 /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\weight.obj"	"$(INTDIR)\weight.sbr" : $(SOURCE) $(DEP_CPP_WEIGH)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "Find_orb - Win32 Debug"

CPP_SWITCHES=/nologo /MDd /W3 /Gm /GX /Zi /Od /I "\myincl" /D "_DEBUG" /D\
 "_AFXDLL" /FR"$(INTDIR)\\" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\weight.obj"	"$(INTDIR)\weight.sbr" : $(SOURCE) $(DEP_CPP_WEIGH)\
 "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 


!ENDIF 

