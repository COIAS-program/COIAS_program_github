// ephem.cpp : implementation file
//

#include "stdafx.h"
#include <math.h>
#include <time.h>
#ifdef _MSC_VER            /* Microsoft Visual C/C++ lacks a 'stdint.h'; */
#include "stdintvc.h"      /* 'stdintvc.h' is a replacement version      */
#else
#include <stdint.h>
#endif
#include "find_orb.h"
#include "mpc_obs.h"
#include "orbitdlg.h"
#include "ephem.h"
#include "watdefs.h"
#include "lunar.h"
#include "afuncs.h"
#include "date.h"
#include "comets.h"

#ifdef _DEBUG
#undef THIS_FILE
static char BASED_CODE THIS_FILE[] = __FILE__;
#endif

#define J2000 2451545.0
#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)
#define EARTH_MAJOR_AXIS_IN_AU (EARTH_MAJOR_AXIS / (1000. * AU_IN_KM))
#define PI 3.141592653589793238462643383279502884197169399375105

int make_pseudo_mpec( const char *mpec_filename, const char *obj_name);
                                              /* ephem0.cpp */
void equatorial_to_ecliptic( double FAR *vect);
void integrate_orbit( double *orbit, double t0, double t1);
int reset_dialog_language( CDialog *dlg, const char *dlg_name);
int earth_lunar_posn( const double jd, double FAR *earth_loc, double FAR *lunar_loc);
int planet_posn( const int planet_no, const double jd, double *vect_2000);
int lat_alt_to_parallax( const double lat, const double ht_in_meters,
                double *rho_cos_phi, double *rho_sin_phi);   /* ephem0.cpp */
void ecliptic_to_equatorial( double FAR *vect);            /* mpc_obs.cpp */
int debug_printf( const char *format, ...);                /* runge.cpp */
char *fgets_trimmed( char *buff, size_t max_bytes, FILE *ifile);

/////////////////////////////////////////////////////////////////////////////
// CEphem dialog

CEphem::CEphem(COrbitDlg* pParent /*=NULL*/)
   : CDialog(CEphem::IDD, pParent)
{
   //{{AFX_DATA_INIT(CEphem)
   m_day = "";
   m_number_steps = 0;
   m_lat = "";
   m_lon = "";
   m_ephem_step = _T("");
   //}}AFX_DATA_INIT
   OriginalDlgRect.top = OriginalDlgRect.bottom = 0;
   ephemeris_and_pseudo_mpec_made = 0;
}

void CEphem::DoDataExchange(CDataExchange* pDX)
{
   CDialog::DoDataExchange(pDX);
   //{{AFX_DATA_MAP(CEphem)
   DDX_Text(pDX, IDC_EPHEM_DAY, m_day);
   DDX_Text(pDX, IDC_EPHEM_NUM_STEPS, m_number_steps);
   DDX_Text(pDX, IDC_LAT, m_lat);
   DDX_Text(pDX, IDC_LON, m_lon);
   DDX_Text(pDX, IDC_EPHEM_STEP, m_ephem_step);
   DDX_Check(pDX, IDC_ALT_AZ, m_alt_az);
   DDX_Check(pDX, IDC_MOTION, m_motion);
   //}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CEphem, CDialog)
   //{{AFX_MSG_MAP(CEphem)
   ON_BN_CLICKED(IDC_SAVE, OnClickedSave)
   ON_BN_CLICKED(IDC_GO, OnClickedGo)
   ON_BN_CLICKED(IDC_MPEC, OnPseudoMpec)
   ON_WM_SIZE()
   ON_WM_GETMINMAXINFO()
   ON_WM_CHAR()
   ON_BN_CLICKED(IDC_COPY, OnCopy)
   //}}AFX_MSG_MAP
END_MESSAGE_MAP()

void get_file_from_dialog( int is_open, const char *default_ext,
                           const char *filter, char *buff, const char *path);

/////////////////////////////////////////////////////////////////////////////
// CEphem message handlers

extern const char *ephemeris_filename;         /* "ephemeri.txt" */

void CEphem::OnClickedSave()
{
   // TODO: Add your control notification handler code here
   char filename[_MAX_DIR];

   get_file_from_dialog( FALSE, "", "*.*", filename, NULL);
   if( *filename)
      if( *m_lat == 'b')
         CreateB32Ephemeris( filename);
      else
         {
         unlink( filename);
         rename( ephemeris_filename, filename);
         }
}

void CEphem::set_jd_from_xtrols( char *err_msg)
{
   static const double jan_1970 = 2440587.5;
   static const double curr_time = jan_1970 + time( NULL) / 86400.;

   if( err_msg)
      *err_msg = '\0';
   UpdateData( TRUE);     /* Get changes made in edit boxes */
   jd = get_time_from_string( curr_time, m_day, FULL_CTIME_YMD);
}

const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */

static int add_ephemeris_details( FILE *ofile, const double start_jd,
                                               const double end_jd)
{
   time_t t0;
   char tbuff[128];
   FILE *ifile;
   extern const char *elements_filename;

   t0 = time( NULL);
   fprintf( ofile, "\nCreated %s", ctime( &t0));

   full_ctime( tbuff, start_jd, 0);
   fprintf( ofile, "Ephemeris start: %s\n", tbuff);

   full_ctime( tbuff, end_jd, 0);
   fprintf( ofile, "Ephemeris end:   %s\n", tbuff);

   ifile = fopen( elements_filename, "rb");
   while( fgets( tbuff, sizeof( tbuff), ifile))
      fwrite( tbuff, strlen( tbuff), 1, ofile);
   fclose( ifile);
   return( 0);
}

/* See 'interpol.cpp' for details on this.  Implementation is "clever",  and
therefore requires a fair bit of explanation. */

static double interpolate( const double *y, const double x, const int n_pts)
{
   double t = 1., c = 1., rval;
   int i;

   for( i = 0; i < n_pts; i++)
      {
      c *= x - (double)i;
      if( i)
         t *= -(double)i;
      }
   if( !c)        /* we're on an abscissa */
      rval = y[(int)( x + .5)];
   else
      {
      rval = y[0] / (t * x);
      for( i = 1; i < n_pts; i++)
         {
         t *= (double)i / (double)( i - n_pts);
         rval += y[i] / (t * (x - (double)i));
         }
      rval *= c;
      }
   return( rval);
}

#define MAX_N_PTS 30

static int best_interpolation_order( const double *ovals,
                  const int array_size, double *max_err)
{
   int i, axis, j, n_pts, rval = 0;

   *max_err = 1e+20;
   for( n_pts = 3; n_pts < MAX_N_PTS; n_pts++)
      {
      double worst = 0.;

      for( i = 0; (i + n_pts) * 2 < array_size; i++)
         for( axis = 0; axis < 3; axis++)
            {
            double tarray[MAX_N_PTS];
            double err, y;

            for( j = 0; j < n_pts; j++)
               tarray[j] = ovals[(i + j) * 6 + axis];

            if( n_pts & 1)    /* for odd number of points... */
               err = interpolate( tarray, (double)n_pts / 2., n_pts);
            else              /* for even number of points... */
               err = interpolate( tarray, (double)(n_pts - 1.) / 2., n_pts);
            y = err;
            err -= ovals[i * 6 + ((n_pts - 1) / 2) * 6 + 3 + axis];
            err = fabs( err);
            if( worst < err)
               worst = err;
//          if( i < 10)
//             debug_printf( "i = %d, n_pts = %d, axis = %d: %.8lg %.8lg\n",
//                      i, n_pts, axis, y, err);
            }
      debug_printf( "order %d: worst: %.3g\n", n_pts, worst);
      if( worst < *max_err)
         {
         *max_err = worst;
         rval = n_pts;
         }
      }
   return( rval);
}

/* In the following,  we compute twice as many data points as we eventually
use,  going at half steps.  That lets us check the "intermediate" (odd)
points against the even ones,  to see how much error is involved;  the
order with the lowest error is then output.  We also can see which ordinate
has the highest absolute value,  and scale the long integers to fit. */

int create_b32_ephemeris( const char *filename,
               const double epoch, const double *orbit,
               const int n_steps, const double ephem_step,
               const double jd_start)
{
   double orbi[6], curr_jd, max_ordinate = 0., resolution;
   double *output_array = (double *)calloc( n_steps * 2,
                                 3 * sizeof( double));
   double prev_ephem_t = epoch, max_err;
   int i, j, jpl_id = 0, planet_center = 0;
   FILE *ofile;
   char tbuff[128];
   static const char *hdr_fmt = "%d %03d %10.1lf %.2lf %ld %d %lg %d %d ";

                     /* hunt for the JPL ID: */
   for( i = 0; filename[i] && !jpl_id; i++)
      {
      jpl_id = atoi( filename + i);
      planet_center = (int)( filename[i] - '0');
      }
   memcpy( orbi, orbit, 6 * sizeof( double));
   curr_jd = jd_start;
   for( i = 0; i < n_steps * 2; i++)
      {
      double r = 0., solar_r = 0., obs_posn[3];
      double *topo = output_array + i * 3;

//    ephemeris_t = curr_jd + td_minus_ut( curr_jd) / 86400.;
      integrate_orbit( orbi, prev_ephem_t, curr_jd);
      prev_ephem_t = curr_jd;
      if( planet_center == 3)
         earth_lunar_posn( curr_jd, obs_posn, NULL);
      else
         planet_posn( planet_center, curr_jd, obs_posn);
      for( j = 0; j < 3; j++)
         topo[j] = orbi[j] - obs_posn[j];

                  /* rotate topo (planeto?) from ecliptic to equatorial */
      ecliptic_to_equatorial( topo);                           /* mpc_obs.cpp */
      for( j = 0; j < 3; j++)
         if( max_ordinate < fabs( topo[j]))
            max_ordinate = fabs( topo[j]);
      curr_jd += ephem_step / 2.;
      }

   resolution = max_ordinate / 2.e+9;
   ofile = fopen( filename, "wb");
   memset( tbuff, 0, 128);
   sprintf( tbuff, hdr_fmt, 128, jpl_id,
            jd_start, ephem_step, n_steps,
            best_interpolation_order( output_array, 2 * n_steps, &max_err),
            resolution, 32, 0);

   fwrite( tbuff, 128, 1, ofile);
   for( i = 0; i < n_steps; i++)
      for( j = 0; j < 3; j++)
         {
         const int32_t tval = (int32_t)( output_array[i * 6 + j] / resolution);
         fwrite( &tval, 1, sizeof( int32_t), ofile);
         }
   free( output_array);
   add_ephemeris_details( ofile, jd_start, curr_jd);
   fclose( ofile);
#ifdef _WIN32
   sprintf( tbuff, "max err: %.3g\nEnd: ", max_err);
   full_ctime( tbuff + strlen( tbuff), curr_jd, 0);
   MessageBox( NULL, tbuff, "Ephemeris", MB_OK);
#endif
   return( 0);
}

void CEphem::CreateB32Ephemeris( const char *filename)
{
   int rval;

   set_jd_from_xtrols( NULL);
   rval = create_b32_ephemeris( filename, epoch, orbit, m_number_steps,
               atof( m_ephem_step), jd);
}

static const char *mpec_filename = "mpec.htm";

void CEphem::OnClickedGo()
{
   char buff[200], *err_msg = NULL;
   // TODO: Add your control notification handler code here
   set_jd_from_xtrols( buff);

   const double step_size = get_step_size( m_ephem_step, NULL, NULL);

   if( *buff)
      err_msg = buff;
   else if( !step_size)
      {
      get_findorb_text( buff, 7);   /* "No step size specified!" */
      err_msg = buff;
      }
   else if( !m_number_steps)
      {
      get_findorb_text( buff, 6);
      err_msg = buff;   /* "Ephemeris must contain at least one entry!" */
      }

   if( !err_msg)
      {
      double rho_sin_phi, rho_cos_phi, lon = 0.;
      char note_text[80];
      int options = (m_alt_az ? OPTION_ALT_AZ_OUTPUT : 0)
                  | (m_motion ? OPTION_MOTION_OUTPUT : 0);
      int planet_no = get_observer_data( m_lat, buff, &lon,
                                   &rho_cos_phi, &rho_sin_phi);

      *note_text = '\0';
      if( planet_no < 0)
         {
         planet_no = 3;
         if( *m_lat == 'v' || *m_lat == 'V')
            {
            lon = 0.;
            rho_sin_phi = rho_cos_phi = 0.;
            options = OPTION_STATE_VECTOR_OUTPUT;
            if( *m_lat == 'V')      /* ...with velocity included */
               options |= OPTION_VELOCITY_OUTPUT;
            }
         else
            {
            double lat;

            if( *m_lat == 'n' || *m_lat == 'N')
               lat = atof( (const char *)m_lat + 1);
            else if( *m_lat == 's' || *m_lat == 'S')
               lat = -atof( (const char *)m_lat + 1);
            else
               {
               get_findorb_text( buff, 12);
               err_msg = buff;    /* Latitude must start with an 'N' or 'S'! */
               }

            if( !err_msg)
               if( *m_lon == 'e' || *m_lon == 'E')
                  lon = atof( (const char *)m_lon + 1);
               else if( *m_lon == 'w' || *m_lon == 'W')
                  lon = -atof( (const char *)m_lon + 1);
               else
                  {
                  get_findorb_text( buff, 13);
                  err_msg = buff; /* Longitude must start with an 'E' or 'W'! */
                  }
            lat *= PI / 180.;
            lon *= PI / 180.;
            lat_alt_to_parallax( lat, 0., &rho_cos_phi, &rho_sin_phi);
            sprintf( note_text, "For %s, %s", (const char *)m_lon,
                                              (const char *)m_lat);
            }
         }
      else
         strcpy( note_text, buff + 30);      /* copy in observer loc */
      if( !err_msg)
         {
         ephemeris_in_a_file( ephemeris_filename, orbit, planet_no, epoch, jd,
                     m_ephem_step, abs_mag, lon, rho_cos_phi, rho_sin_phi,
                     m_number_steps, is_comet, note_text, options);

         CListBox* pListBox = (CListBox*)GetDlgItem( IDC_LIST1);
         FILE *ifile = fopen( ephemeris_filename, "r");

         pListBox->ResetContent( );
         while( fgets_trimmed( buff, sizeof( buff), ifile))
            if( *buff != '#' && *buff)
               pListBox->AddString( (const char FAR *)buff);
         fclose( ifile);
         make_pseudo_mpec( mpec_filename, obj_name);      /* ephem0.cpp */
         ephemeris_and_pseudo_mpec_made = 1;
         if( options & OPTION_STATE_VECTOR_OUTPUT)
            {
            FILE *ofile = fopen( ephemeris_filename, "a");

            add_ephemeris_details( ofile, jd,
                          jd + step_size * (double)m_number_steps);
            fclose( ofile);
            }
         }
      }
   if( err_msg)
      MessageBox( err_msg, "Ephemeris", MB_OK);
}

BOOL CEphem::OnInitDialog()
{
   CDialog::OnInitDialog();

   // TODO: Add extra initialization here
   reset_dialog_language( this, "ephem");
   GetWindowRect( &OriginalDlgRect);
   ScreenToClient( &OriginalDlgRect);

   LOGFONT lf;                             // Used to create the CFont.
   const char *font_str = get_environment_ptr( "EPHEM_FONT");
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_LIST1);

   memset(&lf, 0, sizeof(LOGFONT));        // Clear out structure.
   if( *font_str)
      {
      int bytes, fields[8];

      sscanf( font_str, "%ld %ld %ld %ld %ld %d %d %d %d %d %d %d %d %n",
            &lf.lfHeight, &lf.lfWidth,
            &lf.lfEscapement, &lf.lfOrientation, &lf.lfWeight,
            fields, fields + 1, fields + 2, fields + 3, fields + 4,
            fields + 5, fields + 6, fields + 7, &bytes);
      strcpy( lf.lfFaceName, font_str + bytes);
      lf.lfItalic          = (BYTE)fields[0];
      lf.lfUnderline       = (BYTE)fields[1];
      lf.lfStrikeOut       = (BYTE)fields[2];
      lf.lfCharSet         = (BYTE)fields[3];
      lf.lfOutPrecision    = (BYTE)fields[4];
      lf.lfClipPrecision   = (BYTE)fields[5];
      lf.lfQuality         = (BYTE)fields[6];
      lf.lfPitchAndFamily  = (BYTE)fields[7];
      debug_printf( "Face name '%s'\n", lf.lfFaceName);
      }
   else
      {
      lf.lfHeight = -12;                      // Request a 12-pixel-high font
      strcpy(lf.lfFaceName, "Courier New");       // Request font
   // lf.lfFaceName[0] = '\0';
      lf.lfPitchAndFamily = FIXED_PITCH | FF_MODERN;
      lf.lfWeight = FW_NORMAL;
      lf.lfCharSet = DEFAULT_CHARSET;
      }
   list_box_font.CreateFontIndirect(&lf);    // Create the font.
   pListBox->SetFont( &list_box_font);     // set the font
   pListBox->SetItemHeight( 0, 1 - lf.lfHeight);
   return TRUE;  // return TRUE  unless you set the focus to a control
}

void CEphem::OnPseudoMpec()
{
   // TODO: Add your control notification handler code here

   if( !ephemeris_and_pseudo_mpec_made)
      MessageBox( "You must make an ephemeris before\nmaking a pseudo-MPEC.", "Find_Orb", MB_OK);
   else
      {
      char filename[_MAX_DIR];

      get_file_from_dialog( FALSE, "", "*.*", filename, NULL);
      if( *filename)
         {
         unlink( filename);
         rename( mpec_filename, filename);
         }
      }
}

int copy_file_to_clipboard( const char *filename);    /* ephem0.cpp */
int clipboard_to_file( const char *filename);         /* ephem0.cpp */

void CEphem::OnCopy()
{
   // TODO: Add your control notification handler code here
   if( !ephemeris_and_pseudo_mpec_made)
      MessageBox( "You must make an ephemeris before\ncopying to the clipboard.", "Find_Orb", MB_OK);
   else
      {
      const int rval = copy_file_to_clipboard( ephemeris_filename);

      if( rval)
         {
         char buff[80];

         sprintf( buff, "rval %d", rval);
         MessageBox( buff, "find_orb", MB_OK);
         }
      }
}

void CEphem::OnSize(UINT nType, int cx, int cy)
{
   CDialog::OnSize(nType, cx, cy);

   // TODO: Add your message handler code here
   CListBox* pListBox = (CListBox*)GetDlgItem( IDC_LIST1);

   if( pListBox)
      {
      CRect rect;

      pListBox->GetWindowRect( &rect);
      ScreenToClient( &rect);
      pListBox->SetWindowPos( this, 0, 0,
                  cx,
                  cy - rect.top,
                  SWP_NOMOVE | SWP_NOZORDER);
      }

   // TODO: Add your message handler code here
}

/* Solution found from http://www.codeguru.com/forum/showthread.php?t=318933 */

void CEphem::OnGetMinMaxInfo(MINMAXINFO FAR* lpMMI)
{
  // set the minimum tracking width
  // and the minimum tracking height of the window
  if( OriginalDlgRect.Height( ))
     {
     lpMMI->ptMinTrackSize.x = OriginalDlgRect.Width( );
//   lpMMI->ptMaxTrackSize.x = OriginalDlgRect.Width( );
     lpMMI->ptMinTrackSize.y = OriginalDlgRect.Height( );
     }
}
