all:  astephem.exe persian.exe jd.exe miscell.obj precess.obj obliquit.obj \
         vislimit.obj riseset3.exe ssattest.exe

ssattest.exe:  ssattest.obj date.obj ssats.obj obliquit.obj precess.obj astfuncs.obj miscell.obj
   link ssattest.obj date.obj ssats.obj obliquit.obj precess.obj astfuncs.obj miscell.obj;

astephem.exe:  astephem.obj eart2000.obj date.obj astfuncs.obj
   link astephem.obj eart2000.obj date.obj astfuncs.obj;

riseset3.exe: riseset3.obj lunar2.obj miscell.obj vsopson.obj obliquit.obj date.obj
   link riseset3.obj lunar2.obj miscell.obj vsopson.obj obliquit.obj date.obj;

jd.exe:  jd.obj date.obj
   link jd.obj date.obj;

persian.exe: persian.obj date.obj delta_t.obj
   link persian.obj date.obj delta_t.obj;

precess.exe: precess.obj miscell.obj
   link precess.obj miscell.obj;

.cpp.obj:
   cl /c /Ox /W3 /AL $<

astephem.obj:

astfuncs.obj:

date.obj:

delta_t.obj:

eart2000.obj:

jd.obj:

lunar2.obj:

miscell.obj:

obliquit.obj:

persian.obj:

precess.obj:

riseset3.obj:

ssats.obj:
   cl /c /Od /W3 /AL ssats.cpp

ssattest.obj:

vislimit.obj:

vsopson.obj:

