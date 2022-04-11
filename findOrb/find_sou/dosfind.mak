OBJS=dos_find.obj collide.obj conv_ele.obj elem2tle.obj \
  elem_out.obj ephem0.obj gauss.obj get_pert.obj \
  jpleph.obj lsquare.obj moid4.obj monte0.obj mpc_obs.obj \
  orb_func.obj orb_fun2.obj pl_cache.obj roots.obj runge.obj \
  sm_vsop.obj sr.obj tle_out.obj weight.obj

dos_find.exe: $(OBJS)
     link $(OBJS) lunar.lib pdcurses.lib user32.lib

CFLAGS=/c /Ot /W3 /nologo

.cpp.obj:
   cl $(CFLAGS) $<

