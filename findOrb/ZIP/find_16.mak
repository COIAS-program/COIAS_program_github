# Microsoft Visual C++ generated build script - Do not modify

PROJ = FIND_ORB
DEBUG = 1
PROGTYPE = 0
CALLER =
ARGS =
DLLS =
D_RCDEFINES = /d_DEBUG
R_RCDEFINES = /dNDEBUG
ORIGIN = MSVC
ORIGIN_VER = 1.00
PROJPATH = C:\FIND_ORB\
USEMFC = 1
CC = cl
CPP = cl
CXX = cl
CCREATEPCHFLAG =
CPPCREATEPCHFLAG = /YcSTDAFX.H
CUSEPCHFLAG =
CPPUSEPCHFLAG = /YuSTDAFX.H
FIRSTC =
FIRSTCPP = STDAFX.CPP
RC = rc
CFLAGS_D_WEXE = /nologo /G2 /W3 /Zi /AM /Od /D "_DEBUG" /FR /GA /Fd"FIND_ORB.PDB"
CFLAGS_R_WEXE = /nologo /Gs /G2 /W4 /AM /O1 /D "NDEBUG" /FR /GA /DJSAT_OBS
LFLAGS_D_WEXE = /NOLOGO /NOD /PACKC:61440 /STACK:10240 /ALIGN:16 /ONERROR:NOEXE /CO
LFLAGS_R_WEXE = /NOLOGO /NOD /PACKC:61440 /STACK:10240 /ALIGN:16 /ONERROR:NOEXE
LIBS_D_WEXE = mafxcwd oldnames libw mlibcew commdlg olesvr olecli shell \lunar\winlunar
LIBS_R_WEXE = mafxcw oldnames libw mlibcew commdlg shell \lunar\winlunar
RCFLAGS = /nologo /z /k
RESFLAGS = /nologo /t /k
RUNFLAGS =
DEFFILE = FIND_ORB.DEF
OBJS_EXT =
LIBS_EXT =
!if "$(DEBUG)" == "1"
CFLAGS = $(CFLAGS_D_WEXE)
LFLAGS = $(LFLAGS_D_WEXE)
LIBS = $(LIBS_D_WEXE)
MAPFILE = find_orb.map
RCDEFINES = $(D_RCDEFINES)
!else
CFLAGS = $(CFLAGS_R_WEXE)
LFLAGS = $(LFLAGS_R_WEXE)
LIBS = $(LIBS_R_WEXE)
MAPFILE = find_orb.map
RCDEFINES = $(R_RCDEFINES)
!endif
!if [if exist MSVC.BND del MSVC.BND]
!endif
SBRS = STDAFX.SBR \
      FIND_ORB.SBR


FIND_ORB_RCDEP = c:\find_orb\res\find_orb.ico \
   c:\find_orb\res\find_orb.rc2


STDAFX_DEP = c:\find_orb\stdafx.h


FIND_ORB_DEP = c:\find_orb\stdafx.h \
   c:\find_orb\find_orb.h \
   c:\find_orb\orbitdlg.h \

all:   $(PROJ).EXE $(PROJ).BSC

FIND_ORB.RES:   FIND_ORB.RC $(FIND_ORB_RCDEP)
   $(RC) $(RCFLAGS) $(RCDEFINES) -r FIND_ORB.RC  >> d:err
   type d:err

STDAFX.OBJ:   STDAFX.CPP $(STDAFX_DEP)
   $(CPP) $(CFLAGS) $(CPPCREATEPCHFLAG) /c STDAFX.CPP >> d:err
   type d:err

FIND_ORB.OBJ:   FIND_ORB.CPP $(FIND_ORB_DEP)
   $(CPP) $(CFLAGS) $(CPPUSEPCHFLAG) /c FIND_ORB.CPP >> d:err
   type d:err

orbitdlg.OBJ:  orbitdlg.CPP orbitdlg.h
   $(CPP) $(CFLAGS) $(CPPUSEPCHFLAG) /c -I\myincl orbitdlg.CPP >> d:err
   type d:err

orb_func.OBJ:  orb_func.CPP
   $(CPP) $(CFLAGS) /c -I\myincl orb_func.CPP >> d:err
   type d:err

ephem.OBJ:  ephem.CPP
   $(CPP) $(CFLAGS) /c -I\myincl ephem.CPP >> d:err
   type d:err

ephem0.OBJ:  ephem0.CPP
   $(CPP) $(CFLAGS) /c -I\myincl ephem0.CPP >> d:err
   type d:err

about.OBJ:  about.CPP
   $(CPP) $(CFLAGS) /c -I\myincl about.CPP >> d:err
   type d:err

classel.OBJ:  classel.CPP
   $(CPP) $(CFLAGS) /c -I\myincl classel.CPP >> d:err
   type d:err

mpc_obs.OBJ:   mpc_obs.CPP
   $(CPP) $(CFLAGS) /c -I\myincl mpc_obs.CPP >> d:err
   type d:err

runge.OBJ  :   runge.CPP
   $(CPP) $(CFLAGS) /c -I\myincl runge.CPP >> d:err
   type d:err

lsquare.OBJ  :   \image\lsquare.CPP
   $(CPP) $(CFLAGS) /c -I\myincl \image\lsquare.CPP >> d:err
   type d:err

$(PROJ).EXE::   FIND_ORB.RES

$(PROJ).EXE::   STDAFX.OBJ FIND_ORB.OBJ orbitdlg.OBJ mpc_obs.obj about.obj \
                ephem.obj ephem0.obj lsquare.obj runge.obj orb_func.obj \
                $(OBJS_EXT) $(DEFFILE)
   echo >NUL @<<$(PROJ).CRF
STDAFX.OBJ +
about.OBJ +
ephem.OBJ +
ephem0.OBJ +
find_orb.obj +
mpc_obs.OBJ +
orbitdlg.OBJ +
orb_func.OBJ +
runge.OBJ +
lsquare.OBJ +
$(OBJS_EXT)
$(PROJ).EXE
$(MAPFILE)
c:\msvc\lib\+
c:\msvc\mfc\lib\+
$(LIBS)
$(DEFFILE);
<<
   link $(LFLAGS) @$(PROJ).CRF
   $(RC) $(RESFLAGS) FIND_ORB.RES $@
   @copy $(PROJ).CRF MSVC.BND

$(PROJ).EXE::   FIND_ORB.RES
   if not exist MSVC.BND    $(RC) $(RESFLAGS) FIND_ORB.RES $@

run: $(PROJ).EXE
   $(PROJ) $(RUNFLAGS)


$(PROJ).BSC: $(SBRS)
   bscmake @<<
/o$@ $(SBRS)
<<
