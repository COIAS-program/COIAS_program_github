// orbitdlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// COrbitDlg dialog

class COrbitDlg : public CDialog
{
// Construction
public:
   COrbitDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
   //{{AFX_DATA(COrbitDlg)
   enum { IDD = IDD_FIND_ORB };
   double   m_step_size;
   CString   m_epoch;
   CString   m_r1;
   CString   m_r2;
   //}}AFX_DATA

   int RunMonteCarlo( void);
   int monte_carlo;
// Implementation
protected:
   virtual void DoDataExchange(CDataExchange* pDX);   // DDX/DDV support
   void InitOrbitSolution();
   void Reset_r1_and_r2( );
   void ImproveOrbitSolution( int full_step, int n_repeats);
   void UpdateElementDisplay( int update_orbit);
   void UpdateResidualDisplay();
   void LoadAnObject( const int obj_idx);
   void LoadAFile( const char *filename);
   int GetPerturberMask();
   CString curr_file_name;
   CString curr_object_name;
   CString constraints;
   time_t curr_file_time;
   double max_residual_for_filtering;
   double orbit[6], orbit_epoch, monte_noise;
   int n_obs, heliocentric_only, element_precision, n_objects;
   int current_context_menu_context;
   int ephemeris_output_options;
   void FAR *obs_data;
   OBJECT_INFO *obj_info;
   virtual BOOL OnCommand( UINT wParam, LONG lParam);
// #ifdef TRY_OMITTING
   CRect OriginalDlgRect;
   void OnGetMinMaxInfo(MINMAXINFO FAR* lpMMI);
// #endif

   // Generated message map functions
   //{{AFX_MSG(COrbitDlg)
   afx_msg void OnClickedFullStep();
   afx_msg void OnClickedHerget();
   afx_msg void OnClickedOpen();
   virtual BOOL OnInitDialog();
   afx_msg void OnDblclkObject();
   afx_msg void OnClickedSave();
   afx_msg void OnSelchangeResiduals();
   afx_msg void OnClickedMakeEphemeris();
   afx_msg void OnClickedSaveResids();
   afx_msg void OnDblclkResiduals();
 afx_msg void OnClickedAbout();
   afx_msg void OnClickedVaisala();
   afx_msg void OnClickedAutoSolve();
   afx_msg void OnChar(UINT nChar, UINT nRepCnt, UINT nFlags);
   afx_msg void OnMonteCarlo();
   afx_msg void OnTimer(UINT nIDEvent);
   afx_msg void OnGauss();
   afx_msg void OnWorst();
   afx_msg void OnDoubleclickedWorst();
   afx_msg void OnFilterObs();
   afx_msg void OnSelcancelListAsteroids();
   afx_msg void OnAsteroids();
   afx_msg void OnSettings();
   afx_msg void OnSelchangeListAsteroids();
   afx_msg void OnSetWeight();
   afx_msg void OnToggleObs();
   afx_msg void OnOrbitalElements();
   afx_msg void OnDestroy();
   afx_msg void OnRButtonUp(UINT nFlags, CPoint point);
   afx_msg void OnSize(UINT nType, int cx, int cy);
   //}}AFX_MSG
   DECLARE_MESSAGE_MAP()
};
