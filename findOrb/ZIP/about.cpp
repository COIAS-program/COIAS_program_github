// about.cpp : implementation file
//

#include "stdafx.h"
#include "find_orb.h"
#include "about.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

int reset_dialog_language( CDialog *dlg, const char *dlg_name);

/////////////////////////////////////////////////////////////////////////////
// CAbout dialog

CAbout::CAbout(CWnd* pParent /*=NULL*/)
   : CDialog(CAbout::IDD, pParent)
{
   //{{AFX_DATA_INIT(CAbout)
      // NOTE: the ClassWizard will add member initialization here
   //}}AFX_DATA_INIT
}

void CAbout::DoDataExchange(CDataExchange* pDX)
{
   CDialog::DoDataExchange(pDX);
   //{{AFX_DATA_MAP(CAbout)
      // NOTE: the ClassWizard will add DDX and DDV calls here
   //}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAbout, CDialog)
   //{{AFX_MSG_MAP(CAbout)
   //}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAbout message handlers

BOOL CAbout::OnInitDialog()
{
   CDialog::OnInitDialog();
   // TODO: Add extra initialization here
   reset_dialog_language( this, "about");

   return TRUE;  // return TRUE  unless you set the focus to a control
}
