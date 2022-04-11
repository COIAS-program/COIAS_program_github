// ephem.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CEphem dialog

class CEphem : public CDialog
{
// Construction
public:
   CEphem(COrbitDlg* pParent = NULL);   // standard constructor
   double orbit[6], epoch;
   double jd, ht_in_meters, abs_mag;
   int is_comet;
   const char *obj_name;

// Dialog Data
   //{{AFX_DATA(CEphem)
   enum { IDD = IDD_MAKE_EPHEMERIS };
   CString   m_day;
   int      m_number_steps;
   CString   m_lat;
   CString   m_lon;
   CString   m_ephem_step;
   BOOL   m_alt_az;
   BOOL   m_motion;
   //}}AFX_DATA


// Implementation
protected:
   int ephemeris_and_pseudo_mpec_made;
   CFont list_box_font;
   virtual void DoDataExchange(CDataExchange* pDX);   // DDX/DDV support
   void CreateB32Ephemeris( const char *filename);
   void set_jd_from_xtrols( char *err_msg);
   CRect OriginalDlgRect;
   void OnGetMinMaxInfo(MINMAXINFO FAR* lpMMI);

   // Generated message map functions
   //{{AFX_MSG(CEphem)
   afx_msg void OnClickedSave();
   afx_msg void OnClickedGo();
   virtual BOOL OnInitDialog();
   afx_msg void OnPseudoMpec();
   afx_msg void OnSize(UINT nType, int cx, int cy);
   afx_msg void OnCopy();
   //}}AFX_MSG
   DECLARE_MESSAGE_MAP()
};
