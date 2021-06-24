# Make file for DOS_FIND with the Watcom C/C++ compiler.

dos_find.exe:     dos_find.obj bmouse.obj collide.obj &
    conv_ele.obj elem2tle.obj elem_out.obj ephem0.obj &
    gauss.obj get_pert.obj jpleph.obj lsquare.obj moid4.obj monte0.obj &
    mpc_obs.obj mycurses.obj orb_func.obj orb_fun2.obj pl_cache.obj &
    roots.obj runge.obj sm_vsop.obj sr.obj tle_out.obj weight.obj
   wlink option stub=pmodew option quiet option map=dos_find.map @watfind.lnk

CFLAGS=/Ox /W3 /4r /s /j /zq /DUSE_MYCURSES

.cpp.obj:
   wcc386 $(CFLAGS) $<
