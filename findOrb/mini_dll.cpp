// libentry.cpp : Defines the entry point for the DLL application.
//
/* Usually,  the following lines come from a separate file,  STDAFX.H.
   However,  for the 'mini-DLL',  STDAFX is used only in this file,
   and maintaining a separate include file seems superfluous.       */

/*        ------ STDAFX.H BEGINS HERE ------ */
// stdafx.h : include file for standard system include files,
//  or project specific include files that are used frequently, but
//      are changed infrequently
//

#if !defined(AFX_STDAFX_H__298970FE_2CDF_11D5_A298_000102CA0D3E__INCLUDED_)
#define AFX_STDAFX_H__298970FE_2CDF_11D5_A298_000102CA0D3E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000


// Insert your headers here
#define WIN32_LEAN_AND_MEAN      // Exclude rarely-used stuff from Windows headers

#include <windows.h>

// TODO: reference additional headers your program requires here

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_STDAFX_H__298970FE_2CDF_11D5_A298_000102CA0D3E__INCLUDED_)
/*        ------ STDAFX.H ENDS HERE ------ */

BOOL APIENTRY DllMain( HANDLE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                )
{
    return TRUE;
}

