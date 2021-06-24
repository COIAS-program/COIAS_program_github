#ifdef __WATCOMC__
#ifdef __386__
#define BITS_32
#endif
#endif

#ifdef __GNUC__
#define BITS_32
#endif

#ifdef _WIN32
#define BITS_32
#endif

#ifdef BITS_32

#ifndef FAR
#define FAR
#endif

#ifndef _HUGE
#define _HUGE
#endif

#ifndef NEAR
#define NEAR
#endif

#ifndef PASCAL
#define PASCAL
#endif

#define FMEMCPY      memcpy
#define FMEMCMP      memcmp
#define FMEMICMP     memicmp
#define FMEMMOVE     memmove
#define FMEMSET      memset
#define FSTRCPY      strcpy
#define FSTRSTR      strstr
#define FSTRCAT      strcat
#define FSTRNCPY     strncpy
#define FSTRICMP     stricmp
#define FSTRCMP      strcmp
#define FSTRLEN      strlen
#define FMALLOC      malloc
#define FCALLOC      calloc
#define FFREE        free
#define FREALLOC     realloc
#define STRUPR       strupr

#ifdef __WATCOMC__
#define _ftime        ftime
#define _timeb        timeb
#define _videoconfig videoconfig
#define _timezone    timezone
#define _tzset       tzset
#define _swab        swab
// int _stricmp( char *s1, char *s2);
// int _memicmp( char *s1, char *s2, int n);
#endif
#endif

#ifndef BITS_32

#define _FAR       __far
#define _HUGE      huge

#ifndef FAR
#define FAR        far
#endif

#ifndef NEAR
#define NEAR       near
#endif

#ifndef PASCAL
#define PASCAL     pascal
#endif

#define FMEMCPY    _fmemcpy
#define FMEMCMP    _fmemcmp
#define FMEMICMP   _fmemicmp
#define FMEMMOVE   _fmemmove
#define FMEMSET    _fmemset
#define FSTRCPY    _fstrcpy
#define FSTRSTR    _fstrstr
#define FSTRCAT    _fstrcat
#define FSTRNCPY   _fstrncpy
#define FSTRLEN    _fstrlen
#define FSTRICMP   _fstricmp
#define FSTRCMP    _fstrcmp
#define FMALLOC    _fmalloc
#define FCALLOC    _fcalloc
#define FFREE      _ffree
#define FREALLOC   _frealloc
#define STRUPR     _strupr
#endif

#ifdef _WIN32
#define DLL_FUNC __stdcall
#else
#define DLL_FUNC
#endif
#define DLLPTR
