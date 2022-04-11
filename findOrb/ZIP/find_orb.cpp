// find_orb.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "mpc_obs.h"
#include "find_orb.h"
#include "orbitdlg.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CFind_orbApp

BEGIN_MESSAGE_MAP(CFind_orbApp, CWinApp)
   //{{AFX_MSG_MAP(CFind_orbApp)
   //}}AFX_MSG_MAP
   // Standard file based document commands
   ON_COMMAND(ID_FILE_NEW, CWinApp::OnFileNew)
   ON_COMMAND(ID_FILE_OPEN, CWinApp::OnFileOpen)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CFind_orbApp construction

CFind_orbApp::CFind_orbApp()
{
   // TODO: add construction code here,
   // Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CFind_orbApp object

CFind_orbApp NEAR theApp;

/////////////////////////////////////////////////////////////////////////////
// CFind_orbApp initialization

int debug_level = 0;

BOOL CFind_orbApp::InitInstance()
{
   // Standard initialization
   // If you are not using these features and wish to reduce the size
   //  of your final executable, you should remove from the following
   //  the specific initialization routines you do not need.

   SetDialogBkColor();        // set dialog background color to gray
   LoadStdProfileSettings();  // Load standard INI file options (including MRU)

   // Register the application's document templates.  Document templates
   //  serve as the connection between documents, frame windows and views.
/*
   AddDocTemplate(new CSingleDocTemplate(IDR_MAINFRAME,
         RUNTIME_CLASS(CFind_orbDoc),
         RUNTIME_CLASS(CMainFrame),     // main SDI frame window
         RUNTIME_CLASS(CFind_orbView)));


   // create a new (empty) document
   OnFileNew();
*/


   if (m_lpCmdLine[0] != '\0')
   {
      // TODO: add command line processing here
   }

   COrbitDlg dlg;

   dlg.m_r1 = dlg.m_r2 = "1";
   dlg.m_step_size = 3.;
   dlg.DoModal( );

   return TRUE;
}
