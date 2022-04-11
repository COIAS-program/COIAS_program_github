// orbitdlg.cpp : implementation file
//

#include "stdafx.h"
#include <math.h>
#include <stdio.h>
#include <direct.h>
#include <dos.h>
#include <sys/stat.h>
#include "watdefs.h"
#include "find_orb.h"
#include "mpc_obs.h"
#include "orbitdlg.h"
#include "afuncs.h"
#include "comets.h"
#include "ephem.h"
#include "about.h"
#include "date.h"
#include "generic.h"
#include "settings.h"
#include "weight.h"
#include "monte0.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

extern double solar_pressure[];
extern int n_extra_params;
extern double planet_mass[];
extern int prev_shifted_residual = -1;
extern int perturbers;

#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)
#define PI 3.14159265358979323846
#define AU_IN_LIGHT_YEAR ((365.25 * 86400. * SPEED_OF_LIGHT) / AU_IN_KM)

#define TRY_OMITTING 1

#define SRP1AU 2.3e-7
   /* "Solar radiation pressure at 1 AU",  in kg*AU^3 / (m^2*d^2) */
   /* from a private communication from Steve Chesley             */

#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)

void integrate_orbit( double *orbit, double t0, double t1);
double compute_rms( const OBSERVE FAR *obs, int n_obs, int method);
int adjust_herget_results( OBSERVE FAR *obs, int n_obs, double *orbit);
int find_trial_orbit( double *orbit, OBSERVE FAR *obs, int n_obs,
                 const double r1, const double angle_param);
void improve_parabolic( OBSERVE FAR *obs, int n_obs, double *orbit, double epoch);
int set_locs( const double *orbit, double t0, OBSERVE FAR *obs, int n_obs);
double initial_orbit( OBSERVE FAR *obs, int n_obs, double *orbit);
int get_r1_and_r2( const int n_obs, const OBSERVE FAR *obs,
                             double *r1, double *r2);    /* orb_func.cpp */
int write_residuals_to_file( const char *filename, const char *ast_filename,
          const int n_obs, const OBSERVE FAR *obs_data, const int short_form);
                                                /* ephem0.cpp */
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
void set_environment_ptr( const char *env_ptr, const char *new_value);
double calc_obs_magnitude( const int is_comet, const double obj_sun,
          const double obj_earth, const double earth_sun); /* elem_out.cpp */
double convenient_gauss( const OBSERVE FAR *obs, int n_obs, double *orbit,
                  const double mu, const int desired_soln); /* gauss.cpp */
int obj_desig_to_perturber( const char *packed_desig);
void create_obs_file( const OBSERVE FAR *obs, int n_obs);
int debug_printf( const char *format, ...);                /* runge.cpp */

/////////////////////////////////////////////////////////////////////////////
// COrbitDlg dialog

COrbitDlg::COrbitDlg(CWnd* pParent /*=NULL*/)
   : CDialog(COrbitDlg::IDD, pParent)
{
   extern char default_comet_magnitude_type;

   //{{AFX_DATA_INIT(COrbitDlg)
   m_step_size = 0;
   m_epoch = "";
   m_r1 = "1.";
   m_r2 = "1.";
   //}}AFX_DATA_INIT
   n_obs = monte_carlo = 0;
   heliocentric_only = 0;
   element_precision = 5;
   obs_data = NULL;
   max_residual_for_filtering = 1.;
#ifdef TRY_OMITTING
   OriginalDlgRect.top = OriginalDlgRect.bottom = 0;
#endif
   constraints = "";
   monte_noise = .5;
   n_objects = 0;
   obj_info = NULL;
   ephemeris_output_options = 0;
   current_context_menu_context = 0;
   sscanf( get_environment_ptr( "SETTINGS"), "%c,%d,%d,%d,%lf,%lf",
               &default_comet_magnitude_type,
               &heliocentric_only, &element_precision,
               &ephemeris_output_options,
               &max_residual_for_filtering, &monte_noise);
}

void COrbitDlg::DoDataExchange(CDataExchange* pDX)
{
   CDialog::DoDataExchange(pDX);
   //{{AFX_DATA_MAP(COrbitDlg)
   DDX_Text(pDX, IDC_EPOCH, m_epoch);
   DDV_MaxChars(pDX, m_epoch, 17);
   DDX_Text(pDX, IDC_R1, m_r1);
   DDX_Text(pDX, IDC_R2, m_r2);
   //}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(COrbitDlg, CDialog)
   //{{AFX_MSG_MAP(COrbitDlg)
   ON_BN_CLICKED(IDC_FULL_STEP, OnClickedFullStep)
   ON_BN_CLICKED(IDC_HERGET, OnClickedHerget)
   ON_BN_CLICKED(IDC_OPEN, OnClickedOpen)
   ON_LBN_DBLCLK(IDC_LIST_ASTEROIDS, OnDblclkObject)
   ON_BN_CLICKED(IDC_SAVE, OnClickedSave)
   ON_LBN_SELCHANGE(IDC_RESIDUALS, OnSelchangeResiduals)
   ON_BN_CLICKED(IDC_MAKE_EPHEMERIS, OnClickedMakeEphemeris)
   ON_BN_CLICKED(IDC_SAVE_RESIDS, OnClickedSaveResids)
   ON_LBN_DBLCLK(IDC_RESIDUALS, OnDblclkResiduals)
   ON_BN_CLICKED(IDC_ABOUT, OnClickedAbout)
   ON_BN_CLICKED(IDC_VAISALA, OnClickedVaisala)
   ON_BN_CLICKED(IDC_AUTO_SOLVE, OnClickedAutoSolve)
   ON_WM_CHAR()
   ON_BN_CLICKED(IDC_MONTE_CARLO, OnMonteCarlo)
   ON_WM_TIMER()
   ON_BN_CLICKED(IDC_GAUSS, OnGauss)
   ON_BN_CLICKED(IDC_WORST, OnWorst)
   ON_BN_DOUBLECLICKED(IDC_WORST, OnDoubleclickedWorst)
   ON_BN_CLICKED(IDC_FILTER_OBS, OnFilterObs)
   ON_LBN_SELCANCEL(IDC_LIST_ASTEROIDS, OnSelcancelListAsteroids)
   ON_BN_CLICKED(IDC_ASTEROIDS, OnAsteroids)
   ON_BN_CLICKED(IDC_SETTINGS, OnSettings)
   ON_LBN_SELCHANGE(IDC_LIST_ASTEROIDS, OnSelchangeListAsteroids)
   ON_BN_CLICKED(IDC_SET_WEIGHT, OnSetWeight)
   ON_BN_CLICKED(IDC_TOGGLE_OBS, OnToggleObs)
   ON_BN_CLICKED(IDC_ORBITAL_ELEMENTS, OnOrbitalElements)
   ON_WM_DESTROY()
   ON_WM_RBUTTONUP()
   ON_BN_DOUBLECLICKED(IDC_WORST, OnDoubleclickedWorst)
   ON_WM_SIZE()
   ON_WM_GETMINMAXINFO()
   //}}AFX_MSG_MAP
END_MESSAGE_MAP()

void get_file_from_dialog( int is_open, const char *default_ext,
                           const char *filter, char *buff, const char *path)
{
   char old_path[_MAX_DIR];
#ifndef _WIN32
   unsigned int n_drives;
#endif

   *buff = '\0';
   _getcwd( old_path, _MAX_DIR);
   if( path && *path)
      {
      int i;
      char path2[_MAX_DIR];

      for( i = strlen( path); i && path[i - 1] != '\\'; i--)
         ;
      strcpy( path2, path);
      path2[i] = '\0';
      _chdir( path2);
      }
   CFileDialog dlg( is_open, default_ext, filter);
   if( dlg.DoModal( ) == IDOK)
      strcpy( buff, dlg.GetPathName( ));

   _chdir( old_path);
#ifndef _WIN32
   _dos_setdrive( *old_path - 'A' + 1, &n_drives);
#endif
}

static double extract_epoch( const char *epoch_text)
{
   const double jan_1970 = 2440587.5;
   const double initial_jd =
            jan_1970 + (double)(time( NULL) / 86400L) + .5;
   const double rval = get_time_from_string( initial_jd,
                                           epoch_text, FULL_CTIME_YMD);

   return( rval > 1. ? rval : initial_jd);
}

#ifdef OBSOLETE_CODE
static double extract_epoch( const char *epoch_text)
{
   double day = atof( epoch_text);
   int n_scanned, month, year;

   if( day > 2300000. && day < 2600000.)        /* almost surely a JD */
      return( day);
   n_scanned = sscanf( epoch_text, "%d %d %lf", &year, &month, &day);

   if( n_scanned == 3 && day >= 0. && day <= 50. && month >= 1 && month <= 12
                  && year >= 1300 && year <= 2400)
      return( day + dmy_to_day( 0, month, year, 0) - .5);
   return( 2452000.5);
}
#endif

static void format_distance( char *buff, const double ival)
{
   if( ival < .001)       /* about 150,000 km */
      sprintf( buff, "%dkm", (long)( ival * AU_IN_KM));
   else if( ival < 9999.)
      sprintf( buff, "%.4lf", ival);
   else if( ival < 9999 * AU_IN_LIGHT_YEAR)
      sprintf( buff, "%.4lf LY", ival / AU_IN_LIGHT_YEAR);
   else
      strcpy( buff, "<HUGE>");
}

void COrbitDlg::Reset_r1_and_r2( void)
{
   double r1, r2;
   char buff[80];

   get_r1_and_r2( n_obs, (OBSERVE FAR *)obs_data, &r1, &r2);    /* orb_func.cpp */
   format_distance( buff, r1);
   m_r1 = buff;
   if( m_r2[0] < 'A' || m_r2[0] > 'z')
      {
      format_distance( buff, r2);
      m_r2 = buff;
      }
   UpdateData( FALSE);  /* 'False' indicates 'move data to xtrols' */
}

static double parse_distance_text( const char *buff)
{
   double rval = atof( buff);
   const char end_char = buff[strlen( buff) - 1];

   if( end_char == 'm')
      rval /= AU_IN_KM;
   else if( end_char == 'Y')
      rval *= AU_IN_LIGHT_YEAR;
   return( rval);
}

void COrbitDlg::ImproveOrbitSolution( int full_step, int n_repeats)
{
   int is_vaisala = (full_step & 2);
   int is_linearizing = (full_step & 4);

   full_step &= 1;
   UpdateData( TRUE);     /* Get changes made in edit boxes */
   if( n_obs && obs_data)
      {
      OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;
      double new_epoch;
      int i;
      const char *limited_orbit = NULL;
      extern double j2_multiplier;
      char tbuff[80];

      strcpy( tbuff, (const char *)m_r1);
      for( i = 0; tbuff[i] && tbuff[i] != '='; i++)
         ;
      if( tbuff[i] == '=')
         {
         tbuff[i] = '\0';
         set_environment_ptr( tbuff, (const char *)m_r1 + i + 1);
         }

      if( m_r2[0] == 's')
         n_extra_params = atoi( (const char *)m_r2 + 1);
      else if( m_r2[0] == 'j')
         j2_multiplier = atof( (const char *)m_r2 + 1);
      else if( m_r2[0] == 'k')
         {
         extern int integration_method;

         integration_method = atoi( (const char *)m_r2 + 1);
         }
      else if( m_r2[0] == 't')
         {
         extern double integration_tolerance;

         integration_tolerance = atof( (const char *)m_r2 + 1);
         }
      else if( m_r2[0] == 'r')
         {
         extern double relativistic_factor;

         relativistic_factor = atof( (const char *)m_r2 + 1);
         }
      else if( m_r2[0] >= 'A' && m_r2[0] <= 'z')
         limited_orbit = m_r2;
      SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_WAIT));
      GetPerturberMask( );
      for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
         ;
      new_epoch = obs[i].jd;
      if( full_step)
         {
         new_epoch = extract_epoch( m_epoch);
         if( new_epoch < obs[i].jd)        /* if the start of the "real"    */
            new_epoch = obs[i].jd;         /* arc > curr_epoch,  move ahead */
         for( i = n_obs - 1; i && !obs[i].is_included; i--)
            ;
         if( new_epoch > obs[i].jd)      /* if the end of the "real" arc */
            new_epoch = obs[i].jd;       /* < curr_epoch,  move back     */
         }

      if( orbit_epoch != new_epoch && full_step)
         integrate_orbit( orbit, orbit_epoch, new_epoch);
      orbit_epoch = new_epoch;

      if( !full_step)
         {
         if( is_linearizing)
            adjust_herget_results( obs, n_obs, orbit);
         else if( m_r1[0] != '<' && m_r2[0] != '<')
            {
            double r1 = parse_distance_text( m_r1);
            double r2 = parse_distance_text( m_r2);
            double d_r1, d_r2;

            if( limited_orbit)
               {
               for( i = n_obs - 1; i && !obs[i].is_included; i--)
                  ;
               r2 = obs[i].r;
               }
            if( is_vaisala)
               {
               double angle_param;

               if( sscanf( m_r1, "%lf,%lf", &r1, &angle_param) == 2)
                  {
                  if( !find_trial_orbit( orbit, obs, n_obs, r1, angle_param))
                     {
                     r1 = obs->r;
                     r2 = obs[n_obs - 1].r;
                     }
                  }
               else
                  {
                  herget_method( obs, n_obs, -r1, r2, orbit, &d_r1, &d_r2,
                                       (const char *)constraints);
                  r1 = d_r1;
                  r2 = d_r2;
                  }
               }
            else
               {
               herget_method( obs, n_obs, r1, r2, orbit, &d_r1, &d_r2,
                                            (const char *)constraints);
               herget_method( obs, n_obs, r1 + d_r1, r2 + d_r2, orbit,
                                          NULL, NULL, NULL);
               }
            }
         }
      else
         {
         if( !strcmp( (const char *)constraints, "e=1"))
            improve_parabolic( obs, n_obs, orbit, orbit_epoch);
         else
            {
            while( n_repeats--)
               full_improvement( obs, n_obs, orbit, orbit_epoch,
                                       (const char *)constraints);
            while( (GetAsyncKeyState( VK_SHIFT) & 0x8001) == 0x8001)
               full_improvement( obs, n_obs, orbit, orbit_epoch,
                                       (const char *)constraints);
            }
         }

      Reset_r1_and_r2( );
      if( !monte_carlo || !*get_environment_ptr( "MONTE_UPDATE"))
         {
         UpdateElementDisplay( 1);
         UpdateResidualDisplay( );
         }
      SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_ARROW));
      }
   else
      {
      char buff[80];

      get_findorb_text( buff, 1);         /* "No orbit to improve!" */
      MessageBox( buff, "FindOrb", MB_OK);
      }
}

/////////////////////////////////////////////////////////////////////////////
// COrbitDlg message handlers

void COrbitDlg::OnClickedFullStep()
{
   // TODO: Add your control notification handler code here

   ImproveOrbitSolution( 1, 1);
   if( *get_environment_ptr( "LINEAR_FULL"))
      ImproveOrbitSolution( 4, 1);     /* ...then linearize */
}

void COrbitDlg::OnClickedHerget()
{
   // TODO: Add your control notification handler code here

   ImproveOrbitSolution( 0, 1);
   if( *get_environment_ptr( "LINEAR_HERGET"))
      ImproveOrbitSolution( 4, 1);     /* ...then linearize */
}

void COrbitDlg::InitOrbitSolution()
{
   int i;
   CButton *pButton;

   m_r1 = "1";
   m_r2 = "1";
   UpdateData( FALSE);     /* 'False' indicates 'move data to edit boxes' */
   for( i = 0; i < 11; i++)
      {
      int is_on = ((perturbers >> (i + 1)) & 1);

      if( i == 10)            /* asteroids are a special case */
         is_on = (perturbers >> 20) & 7;
      pButton = (CButton *)GetDlgItem( i + IDC_PLANET1);
      pButton->SetCheck( is_on);           /* turn off all the perturbers */
      }
}

int COrbitDlg::GetPerturberMask()
{
   int i, rval = 0;

   for( i = IDC_PLANET1; i <= IDC_PLANET10; i++)
      if( ((CButton *)GetDlgItem( i))->GetCheck( ))
         rval |= (2 << (i - IDC_PLANET1));
   if( ((CButton *)GetDlgItem( IDC_ASTEROIDS))->GetCheck( ))
      rval |= (7 << 20);
   perturbers = rval;
   return( rval);
}

void COrbitDlg::LoadAFile( const char *filename)
{
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_LIST_ASTEROIDS);

   if( obj_info)
      free( obj_info);
   obj_info = find_objects_in_file( filename, &n_objects, NULL);
   if( obj_info && n_objects && pListBox)
      {
      int i;
      struct stat s;

      if( !stat( filename, &s))
         curr_file_time = s.st_mtime;
      pListBox->ResetContent( );
      curr_file_name = filename;
      curr_object_name = "";

      for( i = 0; i < n_objects; i++)
         pListBox->AddString( (const char FAR *)obj_info[i].obj_name);
      pListBox->SetSel( 1, TRUE);
      if( n_objects == 1)
         LoadAnObject( 0);
      }
   else
      {
      char buff[100];

      get_findorb_text( buff, obj_info ? 10 : 11);
              /* "No observations loaded from that file!"
                 : "File not found!"    */
      MessageBox( buff, "FindOrb", MB_OK);
      }
}

void COrbitDlg::OnClickedOpen()
{
   // TODO: Add your control notification handler code here
   char filename[_MAX_DIR];
   static char path[_MAX_DIR];

   get_file_from_dialog( TRUE, "", "*.*", filename, path);
   if( *filename)
      {
      LoadAFile( filename);
      strcpy( path, filename);
      }
}

int reset_dialog_language( CDialog *dlg, const char *dlg_name)
{
   FILE *ifile;
   extern char findorb_language;       /* defaults to 'e' for English */
   char buff[100], filename[20];
   int i, in_dialog = 0;

   strcpy( filename, "efindorb.dat");
   *filename = findorb_language;
   ifile = fopen( filename, "rb");

   if( !ifile)
      return( -1);

   while( fgets( buff, 100, ifile))
      if( *buff != '#')
         {
         for( i = 0; buff[i] >= ' ' || buff[i] < 0; i++)
            ;
         buff[i] = '\0';
         if( *buff == '!')
            memmove( buff, buff + 1, strlen( buff));
         else
            OemToAnsi( buff, buff);
         if( *buff == '@' && !strcmp( buff + 1, dlg_name))
            in_dialog = 1;
         if( *buff == '@' && !strcmp( buff + 1, "end"))
            in_dialog = 0;
         if( in_dialog && *buff)
            if( *buff == 'w')
               dlg->SetWindowText( buff + 6);
            else
               dlg->SetDlgItemText( atoi( buff), buff + 6);
                        /* Kludge to allow re-use of 'version' string */
                        /* between 'about' and 'main' dialogues:      */
         if( !strcmp( dlg_name, "main") && atoi( buff) == 179)
            dlg->SetDlgItemText(IDC_STATION_INFO, buff + 6);
         }
   fclose( ifile);
   return( 0);
}

BOOL COrbitDlg::OnInitDialog()
{
   CDialog::OnInitDialog();

   // TODO: Add extra initialization here
   FILE *startup;
   const char FAR *cmd_line = AfxGetApp( )->m_lpCmdLine;
   const char FAR *cmd_language = NULL;
   int i;
   extern char findorb_language;       /* defaults to 'e' for English */

#ifdef TRY_OMITTING
   GetWindowRect( &OriginalDlgRect);
   ScreenToClient( &OriginalDlgRect);
#endif
   for( i = 0; cmd_line[i] && !cmd_language; i++)
      if( cmd_line[i] == '-' && cmd_line[i + 1] == 'l')
         cmd_language = cmd_line + i;
   if( cmd_language)
      findorb_language = cmd_language[2];
   else if( startup = fopen( "startup.mar", "rb"))
      {
      char buff[140];

      while( fgets( buff, 140, startup))
         if( !memcmp( buff, "51 language", 11))
            findorb_language = buff[12];
      fclose( startup);
      }
   reset_dialog_language( this, "main");
   perturbers = 0;
   m_step_size = 3.;
   srand( (unsigned)time( NULL));         /* for Monte Carlo code */
   load_up_weight_records( "weight.txt");
   InitOrbitSolution( );
   SetTimer( 1, 500, NULL);
   if( *cmd_line != '-' && *cmd_line)
      LoadAFile( cmd_line);

   return TRUE;  // return TRUE  unless you set the focus to a control
}

extern const char *elements_filename;

void COrbitDlg::UpdateElementDisplay( int update_orbit)
{
   int i, index, obs_format, n_selected, *selections;
   char *obuff = (char *)calloc( 10, 80);
   OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);
// int residual_stops[14] = {  0,  10,  20, 53, 60,  80,  90, 102,
//                           130, 145, 155, 180, 210, 270 };
/*                            YY   MM   DD. X  mpc   HH   MM   SS.SSS   */
   int residual_stops[14] = {  0,  10,  20, 58, 65,  85,  95, 107,
                             140, 155, 165, 195, 225, 285 };
/*                           ddd   mm  ss   dx   dy                     */

   if( n_obs >= 2 && update_orbit)
      {
      double epoch_in_edit_box;
      FILE *ifile;
      char *orbit_buff = (char *)malloc( 2000), *tptr = orbit_buff;

      UpdateData( TRUE);     /* Get changes made in edit boxes */
      epoch_in_edit_box = extract_epoch( m_epoch);
      write_out_elements_to_file( orbit, orbit_epoch, epoch_in_edit_box,
                     (OBSERVE FAR *)obs, n_obs,
                     constraints, element_precision, monte_carlo,
                     heliocentric_only);
      ifile = fopen( elements_filename, "rb");
      fgets( tptr, 200, ifile);   /* skip first line,  then... */
      i = 0;
      while( i < 9 && fgets( tptr, 200, ifile))
         if( *tptr != '#')
            {
            tptr += strlen( tptr);
            i++;
            }
      *tptr = '\0';

      SetDlgItemText( IDC_ORBIT1, orbit_buff);

      fclose( ifile);
      if( monte_carlo)
         {
         extern int monte_carlo_object_count;
         char buff[10];

         sprintf( buff, "%d", monte_carlo_object_count);
         SetDlgItemText( IDC_MONTE_CARLO, buff);
         }
      }

   index = pListBox->GetTopIndex( );
   n_selected = pListBox->GetSelCount( );
   selections = (int *)calloc( n_selected, sizeof( int));
   pListBox->GetSelItems( n_selected, selections);
   pListBox->ResetContent( );
   pListBox->SetTabStops( 14, (LPINT)residual_stops);
   obs_format = atoi( get_environment_ptr( "RESID_FORMAT")) + 1;

   for( i = 0; i < n_obs; i++)
      {
      if( !obs_format)
         {
         recreate_observation_line( obuff, obs + i);
         memmove( obuff, obuff + 12, strlen( obuff + 11));
         }
      else
         format_observation( obs + i, obuff, obs_format);
      pListBox->AddString( (const char FAR *)obuff);
      }

   for( i = 0; i < n_selected; i++)
      pListBox->SetSel( selections[i], TRUE);
   free( selections);
   if( index >= 0 && index < n_obs)
      pListBox->SetTopIndex( index);
   free( obuff);
}

static void put_epoch_text( char *buff, const double jd)
{
   long year;
   int month, i;
   const double day = decimal_day_to_dmy( jd, &year, &month, 0);

   sprintf( buff, "%d %d %.5lf", year, month, day);
   for( i = strlen( buff); buff[i - 1] == '0'; i--)
      ;                    /* trim trailing zeroes */
   if( buff[i - 1] == '.')
      i--;
   buff[i] = '\0';
}

void COrbitDlg::LoadAnObject( const int obj_idx)
{
   OBSERVE FAR *obs;
   char buff[90];
   int i, got_vectors, need_real_r1_and_r2 = 0;
   long file_offset;
   FILE *ifile = fopen( curr_file_name, "rb");

   curr_object_name = obj_info[obj_idx].obj_name;
   SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_WAIT));
            /* Start a bit ahead of the actual data,  just in case */
            /* there's a #Weight: or similar command in there: */
   file_offset = obj_info[obj_idx].file_offset - 40L;
   if( file_offset < 0L)
      file_offset = 0L;
   fseek( ifile, file_offset, SEEK_SET);
   n_obs = obj_info[obj_idx].n_obs;
   obs = load_observations( ifile, obj_info[obj_idx].packed_desig, n_obs);
   fclose( ifile);
   obj_desig_to_perturber( obj_info[obj_idx].packed_desig);
   m_step_size = 3.;
   n_extra_params = 0;
   for( i = 0; i < 3; i++)
      solar_pressure[i] = 0.;
   got_vectors = fetch_previous_solution( obs, n_obs, orbit, &orbit_epoch,
                     &perturbers);
   if( got_vectors)
      {
      put_epoch_text( buff, orbit_epoch);
      set_locs( orbit, orbit_epoch, obs, n_obs);
      m_epoch = buff;
      need_real_r1_and_r2 = 1;
      }
   SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_ARROW));
   if( !n_obs)
      return;
   if( obs_data)
      FFREE( obs_data);
   SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_WAIT));
   obs_data = obs;
   if( !got_vectors)
      {
      for( i = n_obs - 1; i && !obs[i].is_included; i--)
         ;
      put_epoch_text( buff, floor( obs[i].jd) + .5);
      m_epoch = buff;
//    perturbers = 0;
      }

   ((CListBox *)GetDlgItem( IDC_RESIDUALS))->ResetContent( );
   InitOrbitSolution( );
   if( !got_vectors)
      {
      GetPerturberMask( );
      orbit_epoch = initial_orbit( obs, n_obs, orbit);
      need_real_r1_and_r2 = 1;
      }

   if( need_real_r1_and_r2)
      Reset_r1_and_r2( );

   UpdateElementDisplay( 1);
   UpdateResidualDisplay( );
   SetCursor( AfxGetApp( )->LoadStandardCursor( IDC_ARROW));
}

void COrbitDlg::OnDblclkObject()
{
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_LIST_ASTEROIDS);
   int selected = pListBox->GetCurSel( );
   struct stat s;

                  /* If the file was modified,  we should reload everything: */
   if( !stat( curr_file_name, &s))
      if( curr_file_time != s.st_mtime)
         {
         char obj_name[80];
         int i;

         strcpy( obj_name, obj_info[selected].obj_name);
         debug_printf( "Modification time changed: reloading file\n");
         LoadAFile( curr_file_name);
         selected = 0;
         for( i = 0; i < n_objects; i++)
            if( !strcmp( obj_name, obj_info[i].obj_name))
               selected = i;
         }
   LoadAnObject( selected);
}

void COrbitDlg::OnClickedSave()
{
   // TODO: Add your control notification handler code here
   char filename[_MAX_DIR];

   get_file_from_dialog( FALSE, "", "*.*", filename, NULL);

   if( *filename)
      {
      double orbit2[6];
      double epoch_in_edit_box;
      FILE *ofile;

      UpdateData( TRUE);     /* Get changes made in edit boxes */
      epoch_in_edit_box = extract_epoch( m_epoch);
      memcpy( orbit2, orbit, 6 * sizeof( double));
      integrate_orbit( orbit2, orbit_epoch, epoch_in_edit_box);
      if( ofile = fopen( filename, "w"))
         {
         char buff[100];
         FILE *ifile = fopen( elements_filename, "rb");

         if( ifile)
            {
            while( fgets( buff, sizeof( buff), ifile))
               fputs( buff, ofile);
            fclose( ifile);
            }
         fclose( ofile);
         }
      else
         MessageBox( filename, "Not opened", MB_OK);
      store_solution( (const OBSERVE FAR *)obs_data, n_obs, orbit2,
                      epoch_in_edit_box, perturbers);
      }
}

void COrbitDlg::UpdateResidualDisplay()
{
   CListBox *pResidualBox = (CListBox *)GetDlgItem( IDC_RESIDUALS);
   const int n_selected = pResidualBox->GetSelCount( );
   char buff[440];
   OBSERVE FAR *obs = (OBSERVE FAR *)obs_data, *optr;

   // TODO: Add your control notification handler code here
   if( n_selected == 1)
      {
      int selected, i;

      pResidualBox->GetSelItems( 1, &selected);
      optr = obs + selected;
      *buff = '\0';
      for( i = 0; i < 5; i++)
         {
         generate_observation_text( obs, n_obs, selected, i,
                                           buff + strlen( buff));
         strcat( buff, "\n");
         }
      recreate_observation_line( buff + strlen( buff), optr);
      if( (GetAsyncKeyState( VK_SHIFT) & 0x8001) == 0x8001)
         if( prev_shifted_residual == -1)
            prev_shifted_residual = selected;
         else
            {
            int temp, n1 = prev_shifted_residual, n2 = selected, i;

            if( n2 < n1)
               {
               temp = n1;
               n1 = n2;
               n2 = temp;
               }
            for( i = n1; i <= n2; i++)
               obs[i].is_included ^= 1;
            UpdateElementDisplay( 0);

            prev_shifted_residual = -1;
            }
      }
   else
      {
      if( !n_selected)
         strcpy( buff, "(No observation selected)");
      else
         {
         int *selected = (int *)calloc( n_selected, sizeof( int));
         int i;
         double mean_xresid = 0., mean_yresid = 0.;
         double mean_xresid2 = 0., mean_yresid2 = 0.;
//       double mean_mag_resid = 0., mean_mag_resid2 = 0.;

         sprintf( buff, "%d observations selected of %d\n", n_selected, n_obs);
         pResidualBox->GetSelItems( n_selected, selected);
         for( i = 0; i < n_selected; i++)
            {
            MOTION_DETAILS m;

            optr = obs + selected[i];
            compute_observation_motion_details( optr, &m);
            mean_xresid += m.xresid;
            mean_yresid += m.yresid;
            mean_xresid2 += m.xresid * m.xresid;
            mean_yresid2 += m.yresid * m.yresid;
            }
         mean_xresid /= (double)n_selected;
         mean_yresid /= (double)n_selected;
         mean_xresid2 /= (double)n_selected;
         mean_yresid2 /= (double)n_selected;
         sprintf( buff + strlen( buff), "Mean RA residual %.2lf +/- %.2lf; dec %.2lf +/- %.2lf",
                mean_xresid, sqrt( mean_xresid2 - mean_xresid * mean_xresid),
                mean_yresid, sqrt( mean_yresid2 - mean_yresid * mean_yresid));
         if( n_selected == 2)
            {
            double dist, posn_ang, delta_time;

            calc_dist_and_posn_ang( &obs[selected[0]].ra,
                                    &obs[selected[1]].ra, &dist, &posn_ang);
            dist *= 180. / PI;      /* cvt radians to degrees */
            delta_time = obs[selected[1]].jd - obs[selected[0]].jd;

            sprintf( buff + strlen( buff), "\nObservations are %.1lf\" = %.2lf' = %.3lf degrees apart",
                  dist * 3600., dist * 60., dist);
            if( fabs( delta_time) < 1.)
               sprintf( buff + strlen( buff), "\nTime diff: %.1lf sec = %.2lf min = %.3lf hrs",
                        delta_time * 86400., delta_time * 1440., delta_time * 24.);
            else
               sprintf( buff + strlen( buff), "\nTime diff: %.1lf hrs = %.2lf days",
                        delta_time * 24., delta_time);
            dist /= delta_time;     /* get motion in degrees/day */
            dist *= 60. / 24.;      /* then convert to '/hr */
                              /* Dunno how the PA got flipped,  but it did: */
            posn_ang = 2. * PI - posn_ang;
            sprintf( buff + strlen( buff), "\nMotion: %.1lf'/hr in RA, %.1lf'/hr in dec",
                     dist * sin( posn_ang), dist * cos( posn_ang));
            sprintf( buff + strlen( buff), " (total %.1lf'/hr at PA %.1lf)",
                     dist, posn_ang * 180. / PI);
            }
         strcat( buff, "\n");
         make_date_range_text( buff + strlen( buff),
                                      obs[selected[0]].jd,
                                      obs[selected[n_selected - 1]].jd);
         free( selected);
         }
      }
   SetDlgItemText( IDC_STATION_INFO, buff);
   GetDlgItem( IDC_STATION_INFO)->Invalidate();
}

void COrbitDlg::OnSelchangeResiduals()
{
   // TODO: Add your control notification handler code here
   UpdateResidualDisplay( );
}

void COrbitDlg::OnClickedMakeEphemeris()
{
   // TODO: Add your control notification handler code here
   if( obs_data && n_obs)
      {
      CEphem dlg;
      int lines_read = 0;
      char tstr[90], object_name[80];
      const char *envptr;
      FILE *ifile = fopen( "startup.mar", "rb");
      extern const char *residual_filename;

                                 /* For purposes of making a pseudo-MPEC: */
      write_residuals_to_file( residual_filename, curr_file_name, n_obs,
                        (OBSERVE FAR *)obs_data, RESIDUAL_FORMAT_SHORT);
      create_obs_file( (OBSERVE FAR *)obs_data, n_obs);
      dlg.epoch = orbit_epoch;
      dlg.m_number_steps = 10;
      dlg.m_ephem_step = "1";
      dlg.m_alt_az = ((ephemeris_output_options & 8) ? TRUE : FALSE);
      dlg.m_motion = ((ephemeris_output_options & 4) ? TRUE : FALSE);
      get_object_name( object_name, ((OBSERVE FAR *)obs_data)->packed_id);
      dlg.obj_name = object_name;
      envptr = get_environment_ptr( "EPHEM_START");
      if( envptr && *envptr)
         strcpy( tstr, envptr);
      else
         full_ctime( tstr, dlg.epoch, FULL_CTIME_YMD | FULL_CTIME_DATE_ONLY);
      dlg.m_day = tstr;
      envptr = get_environment_ptr( "EPHEM_STEPS");
      if( envptr && *envptr)
         {
         sscanf( envptr, "%d %s", &dlg.m_number_steps, tstr);
         dlg.m_ephem_step = tstr;
         }
      dlg.m_lon = dlg.m_lat = "";

      dlg.abs_mag = calc_absolute_magnitude( (OBSERVE FAR *)obs_data,
                                           n_obs);
      dlg.is_comet = ((const OBSERVE FAR *)obs_data)->is_comet;
      if( ifile)
         {
         while( fgets( tstr, 90, ifile))
            {
            if( !memcmp( tstr, "11 lat/lon", 10))
               {
               double lat, lon;

               sscanf( tstr + 12, "%lf%lf", &lon, &lat);
               sprintf( tstr, "%c %.4lf", (lon < 0. ? 'W' : 'E'),
                           fabs( lon));
               dlg.m_lon = tstr;
               sprintf( tstr, "%c %.4lf", (lat < 0. ? 'S' : 'N'),
                           fabs( lat));
               dlg.m_lat = tstr;
               }
            lines_read++;
            }
         fclose( ifile);
         }

      envptr = get_environment_ptr( "EPHEM_LAT");
      if( envptr && *envptr)
         dlg.m_lat = envptr;
      envptr = get_environment_ptr( "EPHEM_LON");
      if( envptr && *envptr)
         dlg.m_lon = envptr;

      memcpy( dlg.orbit, orbit, 6 * sizeof( double));
      GetPerturberMask( );
      if( dlg.DoModal( ) == IDOK)
         {
         sprintf( tstr, "%d %s",
                        dlg.m_number_steps, (const char *)dlg.m_ephem_step);
         set_environment_ptr( "EPHEM_STEPS", tstr);
         set_environment_ptr( "EPHEM_START", dlg.m_day);
         set_environment_ptr( "EPHEM_LON", dlg.m_lon);
         set_environment_ptr( "EPHEM_LAT", dlg.m_lat);
         ephemeris_output_options = (dlg.m_alt_az ? 8 : 0);
         if( dlg.m_motion)
            ephemeris_output_options |= 4;
         }

#ifdef OBSOLETE_CODE
      if( lines_read < 5)   /* STARTUP.MAR not found,  so make one: */
         {
         FILE *ofile = fopen( "startup.mar", "wb");
         const char *lat = (const char *)dlg.m_lat;
         const char *lon = (const char *)dlg.m_lon;

         fprintf( ofile, "11 lat/lon  %c%.5lf %c%.5lf\n",
               (*lon == 'w' || *lon =='W') ? '-' : ' ', atof( lon + 1),
               (*lat == 's' || *lat =='S') ? '-' : ' ', atof( lat + 1));
         fclose( ofile);
         }
#endif
      }
   else
      {
      char buff[80];

      get_findorb_text( buff, 3);  /* "No orbit to make an ephemeris!" */
      MessageBox( buff, "FindOrb", MB_OK);
      }
}

void COrbitDlg::OnClickedSaveResids()
{
   // TODO: Add your control notification handler code here
   char filename[_MAX_DIR];

   if( !n_obs)
      {
      get_findorb_text( filename, 2);     /* "No residuals to save!" */
      MessageBox( filename, "Save residuals", MB_OK);
      return;
      }
   get_file_from_dialog( FALSE, "", "*.*", filename, NULL);
   if( *filename)
      {
      int residual_format;

      if( stricmp( filename + strlen( filename) - 4, ".res"))
         residual_format = RESIDUAL_FORMAT_FULL_NO_TABS;
      else
         residual_format = RESIDUAL_FORMAT_SHORT;
      write_residuals_to_file( filename, curr_file_name,
                    n_obs, (OBSERVE FAR *)obs_data, residual_format);
      }
}

void COrbitDlg::OnDblclkResiduals()
{
   // TODO: Add your control notification handler code here
   OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);
   int selected = pListBox->GetCurSel( );

   obs[selected].is_included ^= 1;
   UpdateElementDisplay( 0);
}

void COrbitDlg::OnClickedAbout()
{
   // TODO: Add your control notification handler code here
   CAbout dlg;

   dlg.DoModal( );
}

void COrbitDlg::OnClickedVaisala()
{
   // TODO: Add your control notification handler code here

   ImproveOrbitSolution( 2, 1);     /* initial Vaisala... */
   ImproveOrbitSolution( 4, 1);     /* ...then linearize */
}

#define EARTH_CLOSE_APPROACH .01

void COrbitDlg::OnClickedAutoSolve()
{
   // TODO: Add your control notification handler code here
   if( !n_obs || !obs_data)
      {
      char buff[80];

      get_findorb_text( buff, 1);         /* "No orbit to improve!" */
      MessageBox( buff, "FindOrb", MB_OK);
      }
   else
      {
      int pass, bug_out = 0, perturbers_used = 0;

      for( pass = 0; !bug_out && pass < 2; pass++)
         {
         double rms[20];
         int i, iter, done = 0;
         OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;

         rms[0] = compute_rms( obs, n_obs, 1);
         for( iter = 1; !bug_out && iter < 20 && !done; iter++)
            {
            ImproveOrbitSolution( pass, 1);
            rms[iter] = compute_rms( (OBSERVE FAR *)obs_data, n_obs, 1);
            if( iter > 1 && rms[iter] < 10.)
               if( rms[iter] > rms[iter - 2] * .9) /* not getting much improvement */
                  done = 1;
            if( rms[iter] > 100000.)         /* wups!  explosion occurred */
               bug_out = 1;
            }
         if( pass)       /* may need to repeat */
            {
            int n1, n2, perturbers_to_use = 0;
            double curr_arc;

            for( i = 0; i < n_obs; i++)
               if( obs[i].is_included && obs[i].r < EARTH_CLOSE_APPROACH)
                  perturbers_to_use = 4 | (1 << 10);    /* earth & moon */
            for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
               ;
            n1 = i;
            for( i = n_obs - 1; i && !obs[i].is_included; i--)
               ;
            n2 = i;

            curr_arc = obs[n2].jd - obs[n1].jd;
            if( curr_arc > 60.)
               perturbers_to_use |= (1 << 4);       /* Jupiter */
            if( curr_arc > 250.)
               perturbers_to_use = 255;            /* Mercury...Neptune */
            if( perturbers_to_use == perturbers_used)
               if( n1 > 0 || n2 < n_obs - 1)   /* gotta extend the arc */
                  {
                  int m1, m2;

                  for( i = n1; i >= 0 && obs[n2].jd - obs[i].jd < 4. * curr_arc; i--)
                     obs[i].is_included = 1;
                  m1 = i + 1;
                  for( i = n2; i < n_obs && obs[i].jd - obs[n1].jd < 4. * curr_arc; i++)
                     obs[i].is_included = 1;
                  m2 = i - 1;
                  if( m1 == n1 && m2 == n2)     /* gotta expand arc by at least */
                     {                          /* one observation: */
                     if( !m1)
                        m2++;
                     else if( m2 == n_obs - 1)
                        m1--;
                     else
                        {
                        if( obs[m1].jd - obs[m1 - 1].jd >
                                                obs[m2 + 1].jd - obs[m2].jd)
                           m2++;
                        else
                           m1--;
                        }
                     obs[m1].is_included = obs[m2].is_included = 1;
                     }
                           /* reconsider the arc: */
                  curr_arc = obs[m2].jd - obs[m1].jd;
                  if( curr_arc > 60.)
                     perturbers_to_use |= (1 << 4);       /* Jupiter */
                  if( curr_arc > 250.)
                     perturbers_to_use = 255;          /* Mercury...Neptune */
                  pass = 0;         /* ensure another iteration */
                  }

            if( perturbers_to_use != perturbers_used)
               {
               for( i = 0; i < 9; i++)
                  if( (perturbers_to_use >> i) & 1)
                     ((CButton *)GetDlgItem( IDC_PLANET1 + i))->SetCheck( 1);
               pass = 0;         /* ensure another iteration */
               perturbers_used = perturbers_to_use;
               }
            }
         }
      }
}

void COrbitDlg::OnChar(UINT nChar, UINT nRepCnt, UINT nFlags)
{
   // TODO: Add your message handler code here and/or call default
   char text[90];

   sprintf( text, "Got %02lx (%c)\n", nChar, nChar);
   MessageBox( text, "FindOrb", MB_OK);
   CDialog::OnChar(nChar, nRepCnt, nFlags);
}

void COrbitDlg::OnMonteCarlo()
{
   // TODO: Add your control notification handler code here

   monte_carlo ^= 1;
   if( !monte_carlo)
      SetDlgItemText( IDC_MONTE_CARLO, "Monte Carlo");
}

int COrbitDlg::RunMonteCarlo( void)
{
   if( n_obs && obs_data)
      {
      OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;
      double *stored_ra_decs;

      stored_ra_decs = add_gaussian_noise_to_obs( n_obs, obs, monte_noise);
      ImproveOrbitSolution( 1, 2);
      remove_gaussian_noise_from_obs( n_obs, obs, stored_ra_decs);
      }

   return( 0);
}

void COrbitDlg::OnTimer(UINT nIDEvent)
{
   // TODO: Add your message handler code here and/or call default
   extern char *runtime_message;

   CDialog::OnTimer(nIDEvent);
   if( monte_carlo)
      RunMonteCarlo( );
   if( runtime_message)
      SetDlgItemText( IDC_STATION_INFO, runtime_message);
}

void COrbitDlg::OnGauss()
{
   OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;
   static int soln_number = 0;
   double new_epoch;

   // TODO: Add your control notification handler code here
   constraints = "";
   new_epoch = convenient_gauss( obs, n_obs, orbit, 1., soln_number++);
   if( !new_epoch)
      {
      char buff[80];

      get_findorb_text( buff, 4);      /* "Method of Gauss failed!" */
      MessageBox( buff, "FindOrb", MB_OK);
      }
   else
      {
      orbit_epoch = new_epoch;
      set_locs( orbit, orbit_epoch, obs, n_obs);
      Reset_r1_and_r2( );
      UpdateElementDisplay( 1);
      }
}

int find_worst_observation( const OBSERVE FAR *obs, const int n_obs);

void COrbitDlg::OnWorst()
{
   // TODO: Add your control notification handler code here

   const int worst = find_worst_observation( (OBSERVE FAR *)obs_data, n_obs);

   if( worst >= 0)
      {
      CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);

//    pListBox->SetCurSel( worst);     Valid for single-selection box only
      pListBox->SelItemRange( FALSE, 0, pListBox->GetCount( ) - 1);
      pListBox->SetSel( worst, TRUE);
      UpdateResidualDisplay( );
      }
}

void COrbitDlg::OnDoubleclickedWorst()
{
   // TODO: Add your control notification handler code here

   MessageBox( "Double clicked", "FindOrb", MB_OK);
}


void COrbitDlg::OnFilterObs()
{
   // TODO: Add your control notification handler code here

   int rval = filter_obs( (OBSERVE FAR *)obs_data, n_obs,
                              max_residual_for_filtering);

   if( rval != FILTERING_CHANGES_MADE)
      {
      char buff[80];

      get_findorb_text( buff, 5);      /* "No changes made!" */
      MessageBox( buff, "FindOrb", MB_OK);
      }
   else
      ImproveOrbitSolution( 1, 1);
}

void COrbitDlg::OnSelcancelListAsteroids()
{
   // TODO: Add your control notification handler code here

}

void COrbitDlg::OnAsteroids()
{
   // TODO: Add your control notification handler code here

}

         /* Added for David Dixon:  code to include a constant acceleration
            TPA (AU/day^2) if object is beyond radius RTPA,  to investigate
            the possible Pioneer anomaly effect. */
extern double RTPA = 0., TPA = 0.;

void COrbitDlg::OnSettings()
{
   // TODO: Add your control notification handler code here
   CSettings dlg;
   extern char default_comet_magnitude_type;
   char tstr[30];

   dlg.m_heliocentric = heliocentric_only;
   dlg.m_element_precision = element_precision;
   dlg.m_constraints = constraints;
   sprintf( tstr, "%.2lf", max_residual_for_filtering);
   dlg.m_max_residual = tstr;
   dlg.m_monte_noise = monte_noise;
   dlg.m_reference = get_environment_ptr( "REFERENCE");
   dlg.m_srp = (n_extra_params != 0);
   dlg.m_comet_mags_total = (default_comet_magnitude_type == 'T');
   if( dlg.DoModal( ) == IDOK)
      {
      element_precision = dlg.m_element_precision;
      heliocentric_only = dlg.m_heliocentric;
      max_residual_for_filtering = atof( dlg.m_max_residual);
      monte_noise = dlg.m_monte_noise;
      constraints = dlg.m_constraints;
      if( dlg.m_srp && !n_extra_params)
         solar_pressure[0] = solar_pressure[1] = solar_pressure[2] = 0.;
      n_extra_params = dlg.m_srp;
      set_environment_ptr( "REFERENCE", (const char *)dlg.m_reference);
      default_comet_magnitude_type =
                  (dlg.m_comet_mags_total ? 'T' : 'N');
      UpdateElementDisplay( 1);

      const char *pioneer_text = strstr( constraints, "PIO=");

      if( pioneer_text)
         sscanf( pioneer_text + 4, "%lf,%lf", &RTPA, &TPA);
      else
         RTPA = TPA = 0.;
      }
}

void COrbitDlg::OnSelchangeListAsteroids()
{
   // TODO: Add your control notification handler code here
   const int selected = ((CListBox*)GetDlgItem( IDC_LIST_ASTEROIDS))->GetCurSel( );

   if( selected >= 0 && selected < n_objects)
      {
      char buff[440];
      OBJECT_INFO *ids = obj_info + selected;

      sprintf( buff, "Object %d of %d: %s\n", selected, n_objects,
                              ids->obj_name);
      sprintf( buff + strlen( buff), "%d observations; ", ids->n_obs);
      make_date_range_text( buff + strlen( buff),
                                      (double)ids->jd_start / 1440.,
                                      (double)ids->jd_end / 1440.);

      SetDlgItemText( IDC_STATION_INFO, buff);
      GetDlgItem( IDC_STATION_INFO)->Invalidate();
      }
}

void COrbitDlg::OnSetWeight()
{
   // TODO: Add your control notification handler code here
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);
   int n_selected;

   n_selected = pListBox->GetSelCount( );
   if( !n_selected)
      MessageBox( \
"No observations selected!  Select one or more\n\
observations,  click on this button,  and\n\
you'll be prompted to enter a weight for them.\n", "FindOrb", MB_OK);
   else
      {
      CGenericEntry dlg;

      dlg.m_caption = "Enter observation weight:";
      dlg.m_text = "1";
      if( dlg.DoModal( ) == IDOK)
         {
         int *selections, i;
         OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;

         selections = (int *)calloc( n_selected, sizeof( int));
         pListBox->GetSelItems( n_selected, selections);
         for( i = 0; i < n_selected; i++)
            obs[selections[i]].weight = atof( dlg.m_text);
         free( selections);
         UpdateElementDisplay( 0);
         UpdateResidualDisplay( );
         }
      }
}

void COrbitDlg::OnToggleObs()
{
   // TODO: Add your control notification handler code here
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);
   int n_selected;

   n_selected = pListBox->GetSelCount( );
   if( !n_selected)
      MessageBox( \
"No observations selected!  Select one or more\n\
observations,  click on this button,  and\n\
they will be toggled.\n", "FindOrb", MB_OK);
   else
      {
      int *selections, n_included = 0, i;
      OBSERVE FAR *obs = (OBSERVE FAR *)obs_data;

      selections = (int *)calloc( n_selected, sizeof( int));
      pListBox->GetSelItems( n_selected, selections);
      for( i = 0; i < n_selected; i++)
         if( obs[selections[i]].is_included)
            n_included++;
      for( i = 0; i < n_selected; i++)
         obs[selections[i]].is_included = (n_included <= n_selected / 2);
      free( selections);
      UpdateElementDisplay( 0);
      UpdateResidualDisplay( );
      }
}

void COrbitDlg::OnOrbitalElements()
{
   // TODO: Add your control notification handler code here

   MessageBox( "Orbital elements clicked", "FindOrb", MB_OK);
}

void COrbitDlg::OnDestroy()
{
   char buff[80];
   extern char default_comet_magnitude_type;

   free_weight_recs( );
   sprintf( buff, "%c,%d,%d,%d,%.2lf,%.2lf",
               default_comet_magnitude_type,
               heliocentric_only, element_precision,
               ephemeris_output_options,
               max_residual_for_filtering, monte_noise);
   set_environment_ptr( "SETTINGS", buff),
   CDialog::OnDestroy();

   // TODO: Add your message handler code here

}

/* A right-click over the observation/station info,  or over the orbital
elements,  leads to a small popup wherein one can choose to save the data
in those areas to a file or copy said text to the clipboard: */

void COrbitDlg::OnRButtonUp(UINT nFlags, CPoint point)
{
   // TODO: Add your message handler code here and/or call default

   CWnd *child = this->ChildWindowFromPoint( point);

   current_context_menu_context = 0;
   if( child == GetDlgItem( IDC_STATION_INFO))
      current_context_menu_context = IDC_STATION_INFO;
   if( child == GetDlgItem( IDC_ORBITAL_ELEMENTS))
      current_context_menu_context = IDC_ORBIT1;

   if( current_context_menu_context)
      {
      CMenu mnuPopup, *mnuPopupMenu;
      CPoint tpoint = point;

      mnuPopup.LoadMenu( IDR_POPUP1);
                    // Get a pointer to the first item of the menu
      mnuPopupMenu = mnuPopup.GetSubMenu(0);
      ClientToScreen( &tpoint);
      mnuPopupMenu->TrackPopupMenu(TPM_LEFTALIGN | TPM_RIGHTBUTTON,
                              tpoint.x, tpoint.y, this);
      }
#ifdef FIND_OUT_WHAT_RIGHT_CLICKS
   else
      {
      char buff[80];

      sprintf( buff, "Right-click %p\n", child);
      MessageBox( buff, "Find_Orb", MB_OK);
      }
#endif
   CDialog::OnLButtonUp(nFlags, point);
}

int copy_buffer_to_clipboard( const char *contents, const long length);
int clipboard_to_file( const char *filename);         /* mpc_obs.cpp */

BOOL COrbitDlg::OnCommand( UINT wParam, LONG lParam)
{
   CWnd::OnCommand( wParam, lParam);

   if( wParam == IDM_READ_CLIPBOARD)
      {
      const char *filename = "obs_temp.txt";

      if( !clipboard_to_file( filename))
         LoadAFile( filename);
      }
   else if( wParam == IDM_SAVE_TO_FILE &&
                  current_context_menu_context == IDC_ORBIT1)
      OnClickedSave( );
   else if( current_context_menu_context)
      if( wParam == IDM_SAVE_TO_FILE || wParam == IDM_COPY_TO_CLIPBOARD)
         {
         CString str;

         this->GetDlgItemText( current_context_menu_context, str);
         if( wParam == IDM_COPY_TO_CLIPBOARD)
            {
            int rval = copy_buffer_to_clipboard( (const char *)str,
                                    strlen( (const char *)str));

            if( rval)
               {
               char tbuff[80];

               sprintf( tbuff, "Clipboard rval %d\n", rval);
               AfxMessageBox( tbuff);
               }
            }
         else
            {
            char filename[_MAX_DIR];

            get_file_from_dialog( FALSE, "", "*.*", filename, NULL);

            if( *filename)
               {
               FILE *ofile = fopen( filename, "w");

               fwrite( str, 1, strlen( str), ofile);
               fclose( ofile);
               }
            }
         }
   current_context_menu_context = 0;
   return TRUE;
}

int debug_printf( const char *format, ...);                /* runge.cpp */

/* GetWindowRect gives a rectangle in screeen coords relative to the
upper left corner of the screen.
   SetWindowPos moves and/or resizes.  The position is in client coords;
width & height are in pixels.
   MoveWindow:  For a top-level window, the position and dimensions are
relative to the upper-left corner of the screen. For a child window,
they are relative to the upper-left corner of the parent window's client
area.  */

void COrbitDlg::OnSize(UINT nType, int cx, int cy)
{
   CDialog::OnSize(nType, cx, cy);
#ifdef TRY_OMITTING
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_RESIDUALS);
   CWnd *station_info = GetDlgItem( IDC_STATION_INFO);

   // TODO: Add your message handler code here
   if( pListBox && station_info)
      {
      CRect rect;


      station_info->GetWindowRect( &rect);
      ScreenToClient( &rect);
      cy -= rect.Height( );
      station_info->SetWindowPos( NULL, rect.left, cy,
                                  0, 0, SWP_NOSIZE | SWP_NOZORDER);

      pListBox->GetWindowRect( &rect);
      ScreenToClient( &rect);
      pListBox->SetWindowPos( this, 0, 0,
                  rect.Width( ),             /* don't change width */
                  cy - rect.top,
                  SWP_NOMOVE | SWP_NOZORDER);
      }
#endif
   // TODO: Add your message handler code here

}

/* Solution found from http://www.codeguru.com/forum/showthread.php?t=318933 */
/* Modified using http://www.flounder.com/getminmaxinfo.htm ,  which has
   lots of useful info on resizing windows & keeping controls to match */

#ifdef TRY_OMITTING
void COrbitDlg::OnGetMinMaxInfo(MINMAXINFO FAR* lpMMI)
{
  // set the minimum tracking width
  // and the minimum tracking height of the window
  if( OriginalDlgRect.Height( ))
     {
     lpMMI->ptMinTrackSize.x = OriginalDlgRect.Width( );
     lpMMI->ptMaxTrackSize.x = OriginalDlgRect.Width( );
     lpMMI->ptMinTrackSize.y = OriginalDlgRect.Height( );
     }
}
#endif
