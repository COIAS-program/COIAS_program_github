#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#ifdef _WIN32
#include <windows.h>
#endif
#include "watdefs.h"
#include "comets.h"
#include "lunar.h"
#include "afuncs.h"
#include "mpc_obs.h"
#include "weight.h"
#include "date.h"

#define PI 3.141592653589793238462643383279502884197
#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)
#define EARTH_MAJOR_AXIS_IN_AU (EARTH_MAJOR_AXIS / (1000. * AU_IN_KM))
#define EARTH_MINOR_AXIS_IN_AU (EARTH_MINOR_AXIS / (1000. * AU_IN_KM))
#define EARTH_MOON_BARYCENTER_FACTOR (82.300679)
#define J2000 2451545.

//K.S. 2021/6/14///////////////////
extern char *mypath;
///////////////////////////////////

int lat_alt_to_parallax( const double lat, const double ht_in_meters,
                double *rho_cos_phi, double *rho_sin_phi);   /* ephem0.cpp */
int parallax_to_lat_alt( const double rho_cos_phi, const double rho_sin_phi,
               double *lat, double *ht_in_meters);           /* ephem0.cpp */
void set_obs_vect( OBSERVE FAR *obs);        /* mpc_obs.h */
int planet_posn( const int planet_no, const double jd, double *vect_2000);
void ecliptic_to_equatorial( double FAR *vect);            /* mpc_obs.cpp */
void equatorial_to_ecliptic( double FAR *vect);            /* mpc_obs.cpp */
static inline void compute_relative_velocity_vectors( const OBSERVE FAR *obs,
                                   double *vel);
int generate_observation_text( const OBSERVE FAR *obs, const int n_obs,
                      const int obs_idx, const int primary_data, char *buff);
void remove_trailing_cr_lf( char *buff);            /* ephem0.cpp */
void format_dist_in_buff( char *buff, const double dist_in_au); /* ephem0.c */
int compute_observer_loc( const double jde, const int planet_no,
               const double rho_cos_phi,                    /* mpc_obs.cpp */
               const double rho_sin_phi, const double lon, double FAR *offset);
int compute_observer_vel( const double jde, const int planet_no,
               const double rho_cos_phi,                    /* mpc_obs.cpp */
               const double rho_sin_phi, const double lon, double FAR *offset);

/* MPC reports store RA and dec in base 60,  Babylonian style. */

static double read_base_60( const char *ibuff)
{
   char buff[13];
   double rval;

   memcpy( buff, ibuff, 12);
   buff[12] = '\0';
   if( buff[2] == '.')        /* decimal degrees or hours */
      rval = atof( buff);
   else
      {
      rval = atof( buff) + atof( buff + 3) / 60.;
      if( buff[5] == ' ')                 /* i.e., seconds are given */
         rval += atof( buff + 6) / 3600.;
      }
   return( rval);
}

int generic_message_box( const char *message, const char *box_type)
{
   int rval = 0;
#ifdef WIN32
   int box_flags = MB_YESNO;

   if( !strcmp( box_type, "o"))
      box_flags = MB_OK;
   rval = MessageBox( NULL, message, "Find_Orb", box_flags);
#endif
   return( rval);
}


int debug_printf( const char *format, ...);                /* runge.cpp */
extern int debug_level;

/* A return value of zero indicates success (the MPC station data line was */
/* properly formed).  Anything else indicates an error.                    */

static int extract_mpc_station_data( const char *buff, double *lon_in_radians,
                            double *rho_cos_phi, double *rho_sin_phi)
{
   int rval = -1;       /* assume no valid data */

                    /* A valid station code line must have,  for starters, */
                    /* a three-character code followed by a space,  and at */
                    /* least 22 bytes:                                     */
   if( !isalnum( buff[0]) || !isalnum( buff[1]) || !isalnum( buff[2])
            || buff[3] != ' ' || strlen( buff) < 22)
      return( rval);
   if( lon_in_radians && rho_cos_phi && rho_sin_phi)
      {
      *lon_in_radians = *rho_cos_phi = *rho_sin_phi = 0.;
      if( buff[7] == '.' && buff[14] == '.' && buff[23] == '.')
         {              /* for-real MPC data,  with parallax constants: */
         *lon_in_radians = atof( buff + 4) * PI / 180.;
         *rho_cos_phi = atof( buff + 13) * EARTH_MAJOR_AXIS_IN_AU;
         *rho_sin_phi = atof( buff + 21) * EARTH_MAJOR_AXIS_IN_AU;
         rval = 0;
         }
      else if( !memcmp( buff + 3, "                           ", 27)
               && buff[30] > ' ') /* stations 245, 247, 249, 250: all blanks */
         rval = 0;
      else        /* latitude & altitude,  not parallaxes: */
         {
         double lat_in_radians, alt_in_meters;

         if( sscanf( buff + 4, "%lf%lf%lf", lon_in_radians, &lat_in_radians,
                                        &alt_in_meters) == 3)
            {
            *lon_in_radians *= PI / 180.;
            lat_in_radians *= PI / 180.;
            lat_alt_to_parallax( lat_in_radians, alt_in_meters,
                        rho_cos_phi, rho_sin_phi);   /* ephem0.cpp */
            rval = 0;
            }
         }
      if( *lon_in_radians < 0.)           /* keep longitude in -180 to +180 */
         *lon_in_radians += 2. * PI;      /* degree range:                  */
      if( *lon_in_radians > PI)
         *lon_in_radians -= 2. * PI;
      }
   return( rval);
}

/* On pass=0,  we just parse the file,  counting valid lines & their size */
/* On pass=1,  we actually copy those lines to the 'rval' array of strings */

static char **load_mpc_stations( int *n_stations)
{
   char **rval = NULL, *codes = NULL;
   int pass, loop;

   //K.S. 2021/2/15/////////////////////////////////////////////
   const char *rovers_filename_org = "rovers.txt";
   char rovers_filename[256];
   sprintf(rovers_filename,"%s/%s",mypath,rovers_filename_org);

   const char *ObsCodesHtml_filename_org = "ObsCodes.html";
   char ObsCodesHtml_filename[256];
   sprintf(ObsCodesHtml_filename,"%s/%s",mypath,ObsCodesHtml_filename_org);

   const char *ObsCodesHtm_filename_org = "ObsCodes.htm";
   char ObsCodesHtm_filename[256];
   sprintf(ObsCodesHtm_filename,"%s/%s",mypath,ObsCodesHtm_filename_org);
   /////////////////////////////////////////////////////////////

   for( pass = 0; pass < 2; pass++)
      {
      int buff_loc = 0;

      *n_stations = 0;
      for( loop = 0; loop < 2; loop++)
         {
         FILE *ifile;

         if( loop){
	   //K.S. 2021/2/15//////////////////////////
	   ifile = fopen( rovers_filename, "rb");
	   if(ifile==NULL){
	     fprintf(stderr,"cannot open rovers.txt file! \n");
	     exit(1);
	   }
	 }
         else
            {
	      //K.S. 2021/2/15//////////////////////////
	      ifile = fopen( ObsCodesHtml_filename, "rb");
	      if( !ifile){
		//K.S. 2021/2/15//////////////////////////
		ifile = fopen( ObsCodesHtm_filename, "rb");
		if(ifile==NULL){
		  fprintf(stderr,"cannot open ObsCodes.html and htm files! \n");
		  exit(1);
		}
	      }
            }
         if( ifile)
            {
            char buff[100];
            double lon_in_radians, rho_cos_phi, rho_sin_phi;

            while( fgets( buff, 100, ifile))
               if( !extract_mpc_station_data( buff, &lon_in_radians,
                                         &rho_cos_phi, &rho_sin_phi))
                  {
                  if( rval)
                     {
                     rval[*n_stations] = codes + buff_loc;
                     strcpy( rval[*n_stations], buff);
                     }
                  buff_loc += strlen( buff) + 1;
                  (*n_stations)++;
                  }
            fclose( ifile);
            }
         }
      if( !pass)     /* At end of first pass,  make the buffer: */
         {
         rval = (char **)calloc( (*n_stations + 1) * sizeof( char *)
                                       + buff_loc, 1);
         codes = (char *)( rval + *n_stations + 1);
         }
      }
   return( rval);
}

/* The following function paws through the STATIONS.TXT file (or the
   ObsCodes.html or .htm file),  looking for the observer code in
   question.  When it finds it,  it just copies the entire line into
   buff.  If lon_in_radians and the rho_xxx_phi values are non-NULL,
   they're extracted from the buffer.

   There are a few "supplemental" observers,  mostly satellite observers
   who don't have MPC codes.  These could be handled as roving observers
   (code 247),  but this can be a hassle;  it's better if they have their
   own codes.  These codes are put into 'rovers.txt',  and have designations
   that are the initials of the observer;  that way,  they don't look
   too much like "real,  official" MPC designations.  At present,  there
   are a few codes there for artificial satellite observers.

   Return value:

      -2:  stations.txt,  obscodes.htm,  obscodes.html not found (need
               any one of these)
       Other:  index of planet of MPC station (3=earth,  most common
            case;  0=sun, 1=mercury,  etc.)
*/

int get_observer_data( const char FAR *mpc_code, char *buff,
              double *lon_in_radians, double *rho_cos_phi, double *rho_sin_phi)

{
   static char *curr_station = NULL;
   static char **station_data = NULL;
   static int n_stations = 0;
   int i, rval = -1;

   if( !n_stations)
      station_data = load_mpc_stations( &n_stations);
   if( lon_in_radians)
      *lon_in_radians = *rho_cos_phi = *rho_sin_phi = 0.;

   if( !curr_station || memcmp( curr_station, mpc_code, 3))
      {
      curr_station = NULL;
      for( i = 0; i < n_stations && !curr_station; i++)
         if( !memcmp( station_data[i], mpc_code, 3))
            curr_station = station_data[i];
      }
   if( !curr_station)
      {
      debug_printf( "Couldn't find MPC station '%s'\n", mpc_code);
      if( buff)
         {
         strcpy( buff, "!!!   0.0000 0.000000 0.000000Unknown Station Code");
         memcpy( buff, mpc_code, 3);
         }
      }
   else
      {
      rval = 3;
      if( buff)
         strcpy( buff, curr_station);
      extract_mpc_station_data( curr_station, lon_in_radians,
                                        rho_cos_phi, rho_sin_phi);
      if( curr_station[30] == '@') /* this is an extraterrestrial station! */
         {                    /* See 'rovers.txt' for examples */
         rval = atoi( curr_station + 31);
         if( buff)
            memmove( buff + 30, buff + 33, strlen( buff + 33) + 1);
         }
      }
   return( rval);
}

/* As the function name suggests,  gets the lat/lon of an MPC station.
   Return value is the planet index (3=earth, 0=sun, 1=mercury,  etc.)
   or a negative value if the station doesn't exist,  or if there's no
   latitude/longitude (planet-centric case,  or spacecraft).         */

int get_observer_data_latlon( const char FAR *mpc_code, char *buff,
              double *lon_in_radians, double *lat_in_radians,
              double *alt_in_meters)
{
   double rho_cos_phi, rho_sin_phi, alt = 0.;
   int rval;

   *lon_in_radians = *lat_in_radians = 0.;
   rval = get_observer_data( mpc_code, buff, lon_in_radians,
                                   &rho_cos_phi, &rho_sin_phi);
   if( rval >= 0 && (rho_cos_phi || rho_sin_phi))
      {       /* Cvt parallax data from AU back into earth-axis units: */
      rho_cos_phi /= EARTH_MAJOR_AXIS_IN_AU;
      rho_sin_phi /= EARTH_MAJOR_AXIS_IN_AU;
      parallax_to_lat_alt( rho_cos_phi, rho_sin_phi, lat_in_radians, &alt);
      }
   else
      rval = -2;
   if( alt_in_meters)
      *alt_in_meters = alt;
   return( rval);
}

double vector3_length( const double *vect);                 /* ephem0.cpp */

/* Used in part for sanity checks ("is the observed RA/dec above the
   horizon?  Is the sun _below_ the horizon at that time?")  Either
   alt/az can be NULL if you're only after one alt/az.

   Return value = 0 if successful,  nonzero otherwise.  (For the function
   to work,  the MPC station must be topocentric.  So you won't get alt/az
   values for a geocentric/planetocentric location,  nor from spacecraft.)

*/

int get_obs_alt_azzes( const OBSERVE FAR *obs, DPT *sun_alt_az,
                                               DPT *object_alt_az)
{
   DPT latlon;
   int rval = (get_observer_data_latlon( obs->mpc_code, NULL,
                                    &latlon.x, &latlon.y, NULL) != 3);

   if( !rval)
      {
      int i;
      DPT ra_dec;
      const double utc = obs->jd - td_minus_utc( obs->jd) / 86400.;

      for( i = 0; i < 2; i++)
         {
         DPT *alt_az = (i ? object_alt_az : sun_alt_az);

         if( alt_az)
            {
            if( !i)      /* compute solar alt/az */
               {
               double equat[3];

               memcpy( equat, obs->obs_posn, 3 * sizeof( double));
               ecliptic_to_equatorial( equat);
               ra_dec.x = atan2( equat[1], -equat[0]);
               ra_dec.y = -asin( equat[2] / vector3_length( equat));
               }
            else
               {
               ra_dec.x = -obs->ra;
               ra_dec.y = obs->dec;
               }
            full_ra_dec_to_alt_az( &ra_dec, alt_az, NULL, &latlon, utc, NULL);
            }
         }
      }
   return( rval);
}

static int get_normal_packed_desig( char *obuff, const char *ibuff)
{
   int rval = 0;

   if( *ibuff >= 'G' && *ibuff <= 'K' && isdigit( ibuff[1])
            && isdigit( ibuff[2]) && isupper( ibuff[3])
            && isdigit( ibuff[5]) && isalnum( ibuff[6]))
      {
      int output_no;

      if( isdigit( ibuff[4]))
         output_no = ibuff[4] - '0';
      else if( isupper( ibuff[4]))
         output_no = ibuff[4] - 'A' + 10;
      else if( islower( ibuff[4]))
         output_no = ibuff[4] - 'a' + 36;
      else
         {
         output_no = -1;
         rval = -2;
         }

      *obuff++ = ((*ibuff >= 'K') ? '2' : '1');          /* millennium */
      *obuff++ = (char)( '0' + ((*ibuff - 'A') % 10));   /* century   */
      *obuff++ = ibuff[1];                               /* decade   */
      *obuff++ = ibuff[2];                               /* year    */
      *obuff++ = ' ';
      *obuff++ = ibuff[3];       /* half-month designator */
      if( isupper( ibuff[6]))    /* asteroid second letter */
         *obuff++ = ibuff[6];
      output_no = output_no * 10 + ibuff[5] - '0';
      if( !output_no)
         *obuff = '\0';
      else
         sprintf( obuff, "%d", output_no);
      if( islower( ibuff[6]))    /* comet fragment letter */
         sprintf( obuff + strlen( obuff), "%c", ibuff[6]);
      }
   else
      rval = -1;
   return( rval);
}

void *load_file_into_memory( const char *filename, size_t *size)
{
   FILE *ifile = fopen( filename, "rb");
   char *rval = NULL;
   size_t filesize = 0;

   if( ifile)
      {
      fseek( ifile, 0L, SEEK_END);
      filesize = ftell( ifile);
      fseek( ifile, 0L, SEEK_SET);
      rval = (char *)malloc( filesize + 1);
      if( !rval)
         debug_printf( "%d bytes not allocated for '%s'\n",
                                    filesize, filename);
      if( fread( rval, 1, filesize, ifile) != filesize)
         {
         debug_printf( "'%s' not loaded: %d bytes\n", filename, filesize);
         filesize = 0;
         free( rval);
         rval = NULL;
         }
      else
         rval[filesize] = '\0';
      fclose( ifile);
      }
   if( size)
      *size = filesize;
   return( rval);
}

/* "Mutant hex" is frequently used by MPC.  It uses the usual hex digits
   0123456789ABCDEF for numbers 0 to 15,  followed by G...Z for 16...35
   and a...z for 36...61.  */

static int mutant_hex_char_to_int( const char c)
{
   int rval;

   if( c >= '0' && c <= '9')
      rval = (int)c - '0';
   else if( c >= 'A' && c <= 'Z')
      rval = (int)c - 'A' + 10;
   else if( c >= 'a' && c <= 'z')
      rval = (int)c - 'a' + 36;
   else
      rval = -1;
   return( rval);
}

/* In an MPC astrometric report line,  the name can be stored in assorted
   highly scrambled and non-intuitive ways.  Those ways _are_ documented
   on the MPC Web site,  which is probably the best place to look to
   understand why the following bizarre code does what it does.   Return
   value is zero if it's an asteroid designation,  1 if it's a comet,
   -1 if it wasn't puzzled out.        */

int get_object_name( char *obuff, const char *packed_desig)
{
   int rval = -1;
   size_t i;
   static char *extra_names = NULL;
   static size_t extra_name_len;

   if( !extra_names)          /* see 'odd_name.txt' for comments on this */
      extra_names = (char *)load_file_into_memory( "odd_name.txt",
                                            &extra_name_len);

   for( i = 0; i < extra_name_len; i++)
      if( !i || extra_names[i - 1] == 10)
         if( !memcmp( packed_desig, extra_names + i, 12))
            {
            int j;

            i += 13;
            for( j = i; extra_names[j] >= ' '; j++)
               obuff[j - i] = extra_names[j];
            obuff[j - i] = '\0';
            return( 0);
            }

   if( packed_desig[4] == 'S')   /* Possible natural satellite */
      if( strchr( "MVEJSUNP", *packed_desig) && isdigit( packed_desig[1])
                  && isdigit( packed_desig[2]) && isdigit( packed_desig[3]) &&
                  !memcmp( packed_desig + 5, "       ", 7))
         {
         const char *planet_names[8] = { "Venus", "Earth", "Mars", "Jupiter",
                  "Saturn", "Uranus", "Neptune", "Pluto" };
         const char *roman_digits[10] = { "", "I", "II", "III", "IV",
                     "V", "VI", "VII", "VIII", "IX" };
         const char *roman_tens[10] = { "", "X", "XX", "XXX", "XL",
                     "L", "LX", "LXX", "LXXX", "XL" };
         const char *roman_hundreds[10] = { "", "C", "CC", "CCC", "CD",
                     "D", "DC", "DCC", "DCCC", "CD" };
         const int obj_number = atoi( packed_desig + 1);

         for( i = 0; i < 8; i++)
            if( planet_names[i][0] == *packed_desig)
               {
               strcpy( obuff, planet_names[i]);
               strcat( obuff, " ");
               }
         if( obj_number / 100)
            strcat( obuff, roman_hundreds[obj_number / 100]);
         if( (obj_number / 10) % 10)
            strcat( obuff, roman_tens[(obj_number / 10) % 10]);
         if( obj_number % 10)
            strcat( obuff, roman_digits[obj_number % 10]);
         rval = 0;
         }
      else if( strchr( "MVEJSUNP", packed_desig[8]) && isdigit( packed_desig[6])
               && isdigit( packed_desig[7]) && isdigit( packed_desig[9])
               && isdigit( packed_desig[10]) && packed_desig[11] == '0'
               && !memcmp( packed_desig + 1, "   ", 3) && packed_desig[5] >= 'H'
               && packed_desig[5] <= 'Z')
         {
         sprintf( obuff, "S/%d%c%c", 20 + packed_desig[5] - 'K',
                                  packed_desig[6], packed_desig[7]);
         obuff[6] = ' ';
         obuff[7] = packed_desig[8];       /* planet identifier */
         obuff[8] = ' ';
         if( packed_desig[9] > '0')     /* double-digit ID (unlikely, */
            {                           /* but it _can_ happen)       */
            obuff[9] = packed_desig[9];
            obuff[10] = packed_desig[10];
            obuff[11] = '\0';
            }
         else                 /* more usual single-digit case: */
            {
            obuff[9] = packed_desig[10];
            obuff[10] = '\0';
            }
         rval = 0;
         }

   if( isalnum( packed_desig[0]) && isdigit( packed_desig[1]) &&  /* possible numbered */
       isdigit( packed_desig[2]) && isdigit( packed_desig[3]) &&  /* asteroid or comet */
                      !memcmp( packed_desig + 5, "       ", 5))
      if( isdigit( packed_desig[4]))
         {                                /* it's a numbered asteroid */
         int number = mutant_hex_char_to_int( *packed_desig);

         number = number * 10000L + atol( packed_desig + 1);
         sprintf( obuff, "(%d)", number);
         rval = 0;
         }
      else if( strchr( "PCDXA", packed_desig[4]))   /* it's a numbered comet */
         {
         const char extra_suffix_char = packed_desig[10];
         const char suffix_char = packed_desig[11];

         *obuff++ = packed_desig[4];
         *obuff++ = '/';
         while( *packed_desig == '0')         /* skip leading zeroes */
            packed_desig++;
         while( *packed_desig >= '0' && *packed_desig <= '9')   /* read digits... */
            *obuff++ = *packed_desig++;
                  /* possibly _two_ suffix letters... so far,  only the  */
                  /* components of 73P/Schwassmann-Wachmann 3 have this: */
         if( extra_suffix_char >= 'a' && extra_suffix_char <= 'z')
            *obuff++ = extra_suffix_char;
         if( suffix_char >= 'a' && suffix_char <= 'z')
            *obuff++ = suffix_char;
         *obuff++ = '\0';
         rval = 1;
         }

   if( rval == -1 && !memcmp( packed_desig, "    ", 4)
            && strchr( " PCDXA", packed_desig[4]))
      {
      if( packed_desig[4] != ' ')
         {
         *obuff++ = packed_desig[4];
         *obuff++ = '/';
         }
      if( !get_normal_packed_desig( obuff, packed_desig + 5))
         rval = (packed_desig[4] != ' ');
      }

#ifdef POSSIBLY_USEFUL_LATER
               /* Look for CSS/SSS/Mt. Lemmon/LAB desigs.  These should be  */
               /* a hex digit,  plus a half-month character,  plus five hex */
               /* more hex digits,  all uppercase.  The first of these is   */
               /* 0-3 for an object found at CSS,  4-7 for SSS, 8-B for Mt. */
               /* Lemmon,  C-F for LAB (which apparently is rare).          */
   if( rval == -1 && !memcmp( packed_desig, "     ", 5))
      {
      int is_valid = 1;

      if( packed_desig[6] < 'A' || packed_desig[6] > 'Z')
         is_valid = 0;           /* not a valid half-month designation */
      for( i = 5; i < 12 && is_valid; i++)
         if( i != 6)       /* skip the half-month designation */
            if( !isdigit( packed_desig[i]))
               if( packed_desig[i] < 'A' || packed_desig[i] > 'F')
                  is_valid = 0;
      if( is_valid)
         {
         const char *suffixes[4] = { " (CSS)", " (SSS)", " (MtL)", " (LAB)" };
         const int stn = mutant_hex_char_to_int( packed_desig[7]) / 4;

         memcpy( obuff, packed_desig + 5, 7);
         strcpy( obuff + 7, suffixes[stn]);
         rval = 0;
         }
      }
#endif

   if( rval == -1)    /* store the name "as is",  assuming no encoding */
      {               /* (except skip leading spaces) */
      for( i = 0; i < 12 && packed_desig[i] == ' '; i++)
         ;
      memcpy( obuff, packed_desig + i, 12 - i);
      obuff[12 - i] = '\0';
      remove_trailing_cr_lf( obuff);      /* ephem0.cpp */
      }
   return( rval);
}

static const double sin_obliq_2000 = .397777156;
static const double cos_obliq_2000 = .917482062;

void equatorial_to_ecliptic( double FAR *vect)
{
   double temp;

   temp    = vect[2] * cos_obliq_2000 - vect[1] * sin_obliq_2000;
   vect[1] = vect[1] * cos_obliq_2000 + vect[2] * sin_obliq_2000;
   vect[2] = temp;
}

void ecliptic_to_equatorial( double FAR *vect)
{
   double temp;

   temp    = vect[2] * cos_obliq_2000 + vect[1] * sin_obliq_2000;
   vect[1] = vect[1] * cos_obliq_2000 - vect[2] * sin_obliq_2000;
   vect[2] = temp;
}

void set_obs_vect( OBSERVE FAR *obs)
{
   obs->vect[0] = cos( obs->ra) * cos( obs->dec);
   obs->vect[1] = sin( obs->ra) * cos( obs->dec);
   obs->vect[2] = sin( obs->dec);
   equatorial_to_ecliptic( obs->vect);
}

/* Given a planet number (Sun=0, Mercury=1, ... Pluto=9) and a JD,
   the following code computes that planet's J2000 equatorial coordinates
   using the PS1996 theory (or,  for the moon,  ELP82). */

const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
void set_environment_ptr( const char *env_ptr, const char *new_value);

int earth_lunar_posn( const double jd, double FAR *earth_loc, double FAR *lunar_loc)
{
   double t_earth[3], t_lunar[3];
   int i;

   planet_posn( 3, jd, t_earth);
   planet_posn( 10, jd, t_lunar);
                     /* earth_loc is the E-M barycenter,  and lunar_loc */
                     /* is geocentric.  Modify earth_loc to be the earth */
                     /* geocenter loc,  and lunar_loc to be heliocentric: */
   for( i = 0; i < 3; i++)
      {
      t_earth[i] -= t_lunar[i] / EARTH_MOON_BARYCENTER_FACTOR;
      t_lunar[i] += t_earth[i];
      if( earth_loc)
         earth_loc[i] = t_earth[i];
      if( lunar_loc)
         lunar_loc[i] = t_lunar[i];
      }
   return( 0);
}




/* Input time is a JD in UT.  Output offset is in equatorial J2000,  in AU. */

int compute_topocentric_offset( const double ut, const double rho_cos_phi,
               const double rho_sin_phi, const double lon, double *offset)
{
   double precess_matrix[9];
   int i;

   calc_planet_orientation( 3, 0, ut, precess_matrix);
   spin_matrix( precess_matrix, precess_matrix + 3, lon);
   for( i = 0; i < 3; i++)
      offset[i] = (rho_cos_phi * precess_matrix[i]
                 + rho_sin_phi * precess_matrix[i + 6]);
   return( 0);
}

int compute_observer_loc( const double jde, const int planet_no,
               const double rho_cos_phi,
               const double rho_sin_phi, const double lon, double FAR *offset)
{
   if( planet_no != 3 && planet_no != 10)
      planet_posn( planet_no, jde, offset);
   else
      {
      double earth_loc[3], lunar_loc[3];

      earth_lunar_posn( jde, earth_loc, lunar_loc);

      if( planet_no == 10)
         FMEMCPY( offset, lunar_loc, 3 * sizeof( double));
      else
         {
         FMEMCPY( offset, earth_loc, 3 * sizeof( double));
         if( rho_sin_phi || rho_cos_phi)
            {
            const double ut = jde - td_minus_ut( jde) / 86400.;
            double geo_offset[3];
            int i;

            compute_topocentric_offset( ut, rho_cos_phi, rho_sin_phi,
                                               lon, geo_offset);
            equatorial_to_ecliptic( geo_offset);
            for( i = 0; i < 3; i++)
               offset[i] += geo_offset[i];
            }
         }
      }
   return( 0);
}

int compute_observer_vel( const double jde, const int planet_no,
               const double rho_cos_phi,
               const double rho_sin_phi, const double lon, double FAR *vel)
{
   double loc1[3], loc2[3];
   const double delta_t = 10. / 86400.;         /* ten seconds */
   int i;

   compute_observer_loc( jde + delta_t, planet_no,
                                     rho_cos_phi, rho_sin_phi, lon, loc2);
   compute_observer_loc( jde - delta_t, planet_no,
                                     rho_cos_phi, rho_sin_phi, lon, loc1);
   for( i = 0; i < 3; i++)
      vel[i] = (loc2[i] - loc1[i]) / (2. * delta_t);
   return( 0);
}

/* get_precision() looks at an RA or dec from an MPC report and returns  */
/* its precision.  The return value has the following meaning:           */
/*    dd mm ss.sss       3                                               */
/*    dd mm ss.ss        2                                               */
/*    dd mm ss.s         1                                               */
/*    dd mm ss           0                                               */
/*    dd mm             -1                                               */
/*    dd mm.m           -2                                               */
/*    dd mm.mm          -3                                               */
/*    dd mm.mmm         -4                                               */
/*    dd.               100                                              */
/*    dd.d              101                                              */
/*    dd.dd             102                                              */
/*    dd.ddd            103                                              */
/*    dd.dddd           104                                              */
/*    Undetermined      -99                                              */
/* Please note that (at least thus far) I've never seen a -3 or -4 case, */
/* and the decimal cases seem to be very uncommon.                       */
/* The precision is stored and used,  if need be,  to "recreate" the     */
/* RA/dec in its original form.  (It could,  and probably should,  also  */
/* be used to weight the observations.)                                  */

static int get_precision( const char *ibuff)
{
   int i, rval;

   if( ibuff[8] == '.')              /* hh mm ss.sss... how many places? */
      {
      for( i = 9; i < 12 && ibuff[i] >= '0' && ibuff[i] <= '9'; i++)
         ;
      rval = i - 9;
      }
   else if( ibuff[5] == '.')        /* decimal minutes... how many places? */
      {
      for( i = 6; ibuff[i] >= '0' && ibuff[i] <= '9'; i++)
         ;
      rval = 5 - i;
      }
   else if( ibuff[2] == '.')        /* decimal degrees... how many places? */
      {
      for( i = 3; ibuff[i] >= '0' && ibuff[i] <= '9'; i++)
         ;
      rval = 100 + i - 3;
      }
   else if( ibuff[7] == ' ')         /* hh mm, integer minutes */
      rval = -1;
   else if( ibuff[8] == ' ')         /* hh mm ss,  integer seconds */
      rval = 0;
   else
      rval = -99;                    /* format undetermined */
   return( rval);
}

/* parse_observation( ) takes an MPC astrometric observation of the usual
   80-character variety,  and extracts all relevant data from it and puts
   it into the 'obs' structure.  It also computes the ecliptic J2000
   coordinates of the observer at the time of the observation,  using the
   PS1996 and ELP82 theories,  or a JPL ephemeris.  */

static double input_coordinate_epoch = 2000.;
static double override_time = 0.;
      /* 'override_time' allows one to set the observation time with the */
      /* #time keyword (see below).  If that's done,  the time from the  */
      /* next observation will be ignored.  */

static int parse_observation( OBSERVE FAR *obs, const char *buff)
{
   int month = atoi( buff + 20);
   long year = atol( buff + 15);
   double lon, rho_cos_phi, rho_sin_phi;
   double utc;
   char tbuff[200];
   int i, rval = 0;
   static int n_unfound = 0;
   static char unfound[10][4];

   if( year > 2100L || year < 600L || month < 1 || month > 12)
      return( -1);

   memcpy( obs->packed_id, buff, 12);
   obs->packed_id[12] = '\0';
   if( get_object_name( tbuff, obs->packed_id) == 1)
      obs->is_comet = 1;
   else
      obs->is_comet = 0;
   memcpy( tbuff, buff + 23, 9);       /* copy in dd.dddddd part */
   tbuff[9] = '\0';
   utc = dmy_to_day( 0, month, year, 0) - .5 + atof( tbuff);
   if( override_time)
      {
      utc = override_time;
      override_time = 0.;
      }
   obs->jd = utc + td_minus_utc( utc) / 86400.;

   obs->ra  = read_base_60( buff + 32) * (PI / 12.);
   obs->dec = read_base_60( buff + 45) * (PI / 180.);

   obs->time_precision = 6;         /* start out assuming time to 1e-6 day */
   while( obs->time_precision && buff[25 + obs->time_precision] == ' ')
      obs->time_precision--;
   obs->ra_precision = get_precision( buff + 32);
   obs->dec_precision = get_precision( buff + 45);
   obs->mag_precision = 2;         /* start out assuming mag to .01 mag */
   while( obs->mag_precision && buff[67 + obs->mag_precision] == ' ')
      obs->mag_precision--;
   if( buff[67] == ' ' && buff[66] >= '0')     /* mag given to integer value */
      obs->mag_precision = -1;

   obs->mag_band = buff[70];
   obs->mag_band2 = buff[71];
   obs->discovery_asterisk = buff[12];
   obs->note1 = buff[13];
   obs->note2 = buff[14];

   obs->is_included = (buff[64] != 'x');
   if( buff[44] == '-')
      obs->dec = -obs->dec;
   if( input_coordinate_epoch != 2000.)
      {
      double epoch = input_coordinate_epoch;

      if( epoch == 0.)        /* means 'coords of date' */
         epoch = (obs->jd - J2000) / 365.25 + 2000.;
      obs->ra *= -1.;
      precess_pt( (DPT DLLPTR *)&obs->ra,
                  (DPT DLLPTR *)&obs->ra, epoch, 2000.);
      obs->ra *= -1.;
      obs->note2 = 'A';       /* mark as coordinates precessed */
      }
   if( buff[66] >= '0')
      obs->obs_mag = atof( buff + 65);
   else
      obs->obs_mag = 0.;
   FMEMCPY( obs->mpc_code, buff + 77, 3);
   obs->mpc_code[3] = '\0';
   rho_cos_phi = rho_sin_phi = lon = 0.;
   if( get_observer_data( obs->mpc_code, tbuff,
                         &lon, &rho_cos_phi, &rho_sin_phi) < 0)
      {
      obs->is_included = 0;
      obs->discovery_asterisk = '!';
      for( i = 0; FMEMCMP( unfound[i], obs->mpc_code, 3) && i < n_unfound; i++)
         ;
      if( i == n_unfound)     /* got a new one! */
         {
         FMEMCPY( unfound[n_unfound++], obs->mpc_code, 3);
         sprintf( tbuff, "Didn't find observer %s\n", obs->mpc_code);
         strcat( tbuff, "Observation(s) will be excluded and\n");
         strcat( tbuff, "treated as geocentric.\n");
         generic_message_box( tbuff, "o");
         }
      }

   FMEMCPY( obs->reference, buff + 72, 5);

   compute_observer_loc( obs->jd, 3, rho_cos_phi, rho_sin_phi, lon, obs->obs_posn);
   compute_observer_vel( obs->jd, 3, rho_cos_phi, rho_sin_phi, lon, obs->obs_vel);
   set_obs_vect( obs);
   return( rval);
}

int separate_periodic_comet_apparitions = 1;

static int xref_designation( char *desig)
{
   static char *xlate_table = NULL;
   static char prev_desig_in[12], prev_desig_out[12];
   static int n_lines = 0;
   int i;

   if( !xlate_table)
      {
	//K.S. 2021/2/12////////////////////////////////////////	
	const char *xdesig_filename_org = "xdesig.txt";
	char xdesig_filename[256];
	sprintf(xdesig_filename,"%s/%s",mypath,xdesig_filename_org);
	FILE *ifile = fopen( xdesig_filename, "rb");
	if(ifile==NULL){
	  fprintf(stderr,"cannot open xdesig.txt file! \n");
	  exit(1);
	}
	////////////////////////////////////////////////////////
      char buff[100];
      int j;

      while( fgets( buff, sizeof( buff), ifile))
         if( *buff != ';')
            n_lines++;
      xlate_table = (char *)malloc( n_lines * 25);

      fseek( ifile, 0L, SEEK_SET);
      i = 0;
      while( fgets( buff, sizeof( buff), ifile))
         if( *buff != ';')
            {
            for( j = 0; buff[j] && buff[j] != 10; j++)
               ;
            while( j < 25)
               buff[j++] = ' ';
            memcpy( xlate_table + i * 25, buff, 25);
            i++;
            }
      }

            /* Frequently,  this function is given the same designation */
            /* multiple times in a row.  You can get at least some speedup */
            /* by caching the previous input,  checking to see if it */
            /* matches the new input,  and if it does,  return the previous */
            /* output designation. */
   if( !memcmp( desig, prev_desig_in, 12))
      {
      memcpy( desig, prev_desig_out, 12);
      return( 0);
      }

   memcpy( prev_desig_in, desig, 12);
           /* In theory,  an object should either have a permanent number, */
           /* or a temporary designation.  In practice,  some have both. */
           /* The 'separate_periodic_comet_apparitions' lets you tell    */
           /* Guide which should be used when both are given;  if it's   */
           /* set to TRUE,  it'll zap the permanent designation data     */
           /* (i.e.,  set it to spaces.)  Otherwise,  it'll zap the      */
           /* temporary designation.                                     */

   if( desig[5] != ' ' && strlen( desig) > 9)
      if( isdigit( desig[1]) && isdigit( desig[2]) && isdigit( desig[3]))
         {
         if( strchr( "PCDXA", desig[4]))        /* it's a numbered comet... */
            if( isdigit( desig[0]) && isdigit( desig[1]))
               if( separate_periodic_comet_apparitions)
                  memset( desig, ' ', 4);
               else
                  memset( desig + 5, ' ', 7);

           /* Same problem exists for numbered asteroids,  sometimes: */
         if( isdigit( desig[0]) || isalpha( desig[0]))
            if( isdigit( desig[4]))
               if( separate_periodic_comet_apparitions)
                  memset( desig, ' ', 5);  /* NB: _5_,  not _4_,  for these */
               else
                  memset( desig + 5, ' ', 7);
         }

   for( i = 0; i < n_lines; i++)
      {
      char *xlate_ptr = xlate_table + i * 25;
      int is_a_match = 0;

      if( !memcmp( xlate_ptr, desig, 12))
         is_a_match = 1;
                /* Again in theory,  natural satellites should have either */
                /* a permanent or a temporary designation.  Again,  in     */
                /* practice,  some have both.  The following code will     */
                /* handle such problem cases. */
      if( desig[4] == 'S' && !memcmp( xlate_ptr + 4, desig + 4, 8))
         is_a_match = 1;
      if( is_a_match)
         memcpy( desig, xlate_ptr + 13, 12);
      }
   memcpy( prev_desig_out, desig, 12);
   return( 0);
}

/* If combine_all_observations is non-zero,  then all observations from */
/* the file are treated as if they're from a single object.  This can be */
/* useful if you're trying to link two arcs,  or if the designations from */
/* different sources aren't the same.  */

int combine_all_observations = 0;

/*  The following does some simple error checking to 'buff' to see if it's
    really an observation,  or just a random line in the file.   */

static int is_an_observation( const char *buff, const char *obj_name)
{
   char tbuff[80];

   if( buff[44] == '-' || buff[44] == '+')
      if( strlen( buff) > 80 && (buff[12] == ' ' || buff[12] == '*'))
         if( (buff[15] == '1' || buff[15] == '2') && buff[19] == ' ')
            if( buff[25] == '.' && buff[14] != 's')
               {
#ifdef STRICT_OBSERVATION_CHECKING
               static const char digits[11] =
                     { 15, 16, 17, 18, 21, 23, 24, 26, 78, 79, 0 };
               int i;

               for( i = 0; digits[i]; i++)
                  if( buff[digits[i]] < '0' || buff[digits[i]] > '9')
                     return( 0);
#endif
               get_object_name( tbuff, buff);
               if( !obj_name || !strcmp( obj_name, tbuff)
                                           || combine_all_observations)
                  return( 1);
               }
   return( 0);
}

static int compare_observations( OBSERVE FAR *obs1, OBSERVE FAR *obs2)
{
   int rval;

   if( obs1->jd < obs2->jd)
      rval = -1;
   else if( obs1->jd > obs2->jd)
      rval = 1;
   else
      rval = FMEMCMP( obs1->mpc_code, obs2->mpc_code, 3);
   return( rval);
}

/* Depending on how it was saved,  an NEOCP ephemeris can be plain text;
plain text modified in weird ways by the browser (at least Firefox) so
that bold items are "decorated" with asterisks;  or it might be real HTML
with real HTML tags: */

#define NEOCP_FILE_TYPE_UNKNOWN           0
#define NEOCP_FILE_TYPE_HTML              1
#define NEOCP_FILE_TYPE_ASTERISKED        2

static int neocp_file_type;

static int get_neocp_data( char *buff, char *desig, char *mpc_code)
{
   int len, rval = 0;

   for( len = 0; buff[len] >= ' '; len++)
      ;
   while( len && buff[len - 1] == ' ')    /* eliminate trailing spaces */
      len--;
   if( len < 10 && *buff == '*' && buff[len - 1] == '*')
      {
      memcpy( desig, buff + 1, len - 2);
      desig[len - 2] = '\0';
      neocp_file_type = NEOCP_FILE_TYPE_ASTERISKED;
      }
   else if( !memcmp( buff, " <p><b>", 7) && !memcmp( buff + 14, "</b>", 4))
      {
      memcpy( desig, buff + 7, 7);
      desig[7] = '\0';
      neocp_file_type = NEOCP_FILE_TYPE_HTML;
      }
   else if( len && len < 10 && neocp_file_type == NEOCP_FILE_TYPE_UNKNOWN)
      {
      memcpy( desig, buff, len);
      desig[len] = '\0';
      }
   else if( !memcmp( buff, "Ephemerides are for observatory code ", 37))
      memcpy( mpc_code, buff + 37, 3);
   else if( !memcmp( buff, " observatory code ", 18))
      memcpy( mpc_code, buff + 18, 3);
   else if( len > 64 && buff[26] == '.' && *desig && *mpc_code)
      {
      int i;
      long mask = 0;

      for( i = 0; i < 26; i++)
         if( isdigit( buff[i]))
            mask |= (1L << i);
         else if( buff[i] != ' ')
            i = 99;                    /* mark as bad */
      if( mask == 0x36c1b6f && i == 26)
         {
         char obuff[82];

         memset( obuff, ' ', 80);
         obuff[80] = 10;
         obuff[81] = '\0';
         strcpy( obuff + 5, desig);
         memcpy( obuff + 15, buff, 10);     /* year, month, day */
         sprintf( obuff + 25, ".%05d", atoi( buff + 11) * 100000 / 24);
         memcpy( obuff + 32, buff + 18, 10);      /* RA */
         memcpy( obuff + 44, buff + 29, 9);       /* dec */
         memcpy( obuff + 65, buff + 46, 4);       /* mag */
         strcpy( obuff + 72, "neocp");
         memcpy( obuff + 77, mpc_code, 3);
         obuff[14] = 'C';                          /* assume a CCD obs */
         obuff[70] = 'V';                          /* mags are V */
         for( i = 0; i < 80; i++)
            if( !obuff[i])
               obuff[i] = ' ';
         strcpy( buff, obuff);
         rval = 1;
         }
      }
   return( rval);
}

   /* In the RWO (NEODyS) format,  provisional designations are given */
   /* in the form ' YYYYLL(num)',  where YYYY is the year and LL are  */
   /* two letters A-Z,  and (num) is an optional number.              */

static void reformat_rwo_designation_to_mpc( const char *buff, char *obuff)
{
   if( !isalpha( buff[6]))           /* numbered object */
      {
      const long ast_number = atoi( buff);
      const long leading_digit = ast_number / 10000L;

      if( leading_digit < 10L)                  /* numbers 1...99999 */
         *obuff = (char)( '0' + leading_digit);
      else if( leading_digit < 36L)             /* 100000...359999 */
         *obuff = (char)( 'A' + leading_digit - 10);
      else if( leading_digit < 62L)             /* 360000...619999 */
         *obuff = (char)( 'A' + leading_digit - 10);
                     /* beyond that,  we hit the A620K problem and */
                     /* MPC doesn't have a plan (yet)              */
      sprintf( obuff + 1, "%04ld", ast_number % 10000L);
      obuff[5] = ' ';
      }
   else                       /* provisional designation */
      {
      obuff[5] = (char)( 'K' + (buff[1] - '2') * 10 + buff[2] - '0');
                                    /* obuff[5] is century marker */
      obuff[6] = buff[3];    /* decade */
      obuff[7] = buff[4];    /* year */
      obuff[8] = buff[5];    /* first letter */
      obuff[11] = buff[6];    /* 2nd   letter */
                  /* A provisional designation is a four-digit year, */
                  /* plus two letters,  plus either no number,  or a */
                  /* one, two,  or three-digit number. */
      if( buff[7] == ' ')              /* No number: say,  '2004RW' */
         obuff[9] = obuff[10] = '0';
      else if( buff[8] == ' ')         /* One-digit #: say,  '2004RW1' */
         {
         obuff[9] = '0';
         obuff[10] = buff[7];
         }
      else if( buff[9] == ' ')         /* 2-digit #: say,  '2004RW31' */
         {
         obuff[9] = buff[7];    /* 1st (tens) digit */
         obuff[10] = buff[8];    /* 2nd (units) digit */
         }
      else                             /* 3-digit #: say,  '2004RW314' */
         {
         const int tens = buff[7] * 10 + buff[8] - '0' * 11;

         if( tens > 36)
            obuff[9] = 'a' + tens - 36;      /* lowercase extended hex */
         else
            obuff[9] = 'A' + tens - 10;      /* digit,  or uppercase one */
         obuff[10] = buff[9];    /* 3rd (units) digit */
         }
      }
}

/* Code to convert an observation in the AstDyS and NeoDyS '.rwo' format
to the MPC's 80-byte format.  Return value indicates that the input
buffer _was_ in .rwo format (rval = 1) or was not (rval = 0),  in which
case the input buffer is unaltered.

12 Aug 2005:  revised to also accept the revised AstDyS format. */

static int rwo_to_mpc( char *buff)
{
   int rval = 0, i;
   char obuff[82];

            /* NeoDyS ("old") format: */
   if( strlen( buff) > 128 && *buff == ' ' && buff[19] == ' '
                && buff[22] == ' ' && buff[25] == '.' && buff[42] == '.'
                && (buff[128] == '0' || buff[128] == '1'))
      {
      memset( obuff, ' ', 80);
      obuff[14] = buff[12];   /* obs type */
      for( i = 15; i < 32; i++)     /* Year,  month,  day */
         obuff[i] = buff[i];
      for( i = 32; i < 44; i++)     /* RA */
         obuff[i] = buff[i + 2];
      for( i = 44; i < 56; i++)     /* dec */
         obuff[i] = buff[i + 19];
      for( i = 65; i < 71; i++)     /* mag,  color */
         obuff[i] = buff[i + 28];
      for( i = 77; i < 80; i++)     /* MPC station code */
         obuff[i] = buff[i + 37];
      if( buff[128] == '0')         /* excluded observation */
         obuff[64] = 'x';
      rval = 1;
      }

            /* The slightly different AstDyS ("new") format: */
   if( strlen( buff) > 128 && *buff == ' ' && buff[16] == ' '
                && buff[21] == ' ' && buff[27] == '.' && buff[58] == '.'
                && (buff[190] == '0' || buff[190] == '1'))
      {
      memset( obuff, ' ', 80);
      obuff[14] = buff[12];   /* obs type */
      for( i = 15; i < 33; i++)     /* Year,  month,  day */
         obuff[i] = buff[i + 2];
      for( i = 32; i < 44; i++)     /* RA */
         obuff[i] = buff[i + 18];
      for( i = 44; i < 56; i++)     /* dec */
         obuff[i] = buff[i + 59];
      for( i = 65; i < 71; i++)     /* mag,  color */
         obuff[i] = buff[i + 91];
      for( i = 77; i < 80; i++)     /* MPC station code */
         obuff[i] = buff[i + 99];
      if( buff[190] == '0')         /* excluded observation */
         obuff[64] = 'x';
      rval = 1;
      }
   if( rval)
      {
      obuff[80] = 10;
      obuff[81] = '\0';
      reformat_rwo_designation_to_mpc( buff, obuff);
      strcpy( buff, obuff);
      }
   return( rval);
}

double roving_lon, roving_lat, roving_ht_in_meters;
int n_obs_actually_loaded;

OBSERVE FAR *load_observations( FILE *ifile, const char *packed_desig,
                           const int n_obs)
{
   char buff[250], mpc_code_from_neocp[4], desig_from_neocp[15];
   char obj_name[80];
   OBSERVE FAR *rval;
   int j, gap, including_obs = 1, line_no = 0, i = 0;
   double weight = 1.;
   int using_default_weights = 1;
   int warning_issued = 0;
   const int gap0 = 29524;
   extern int monte_carlo_object_count;  /* we just want to zero this */
   extern int n_monte_carlo_impactors;   /* and this,  too */

   *desig_from_neocp = '\0';
   strcpy( mpc_code_from_neocp, "500");   /* default is geocenter */
   neocp_file_type = NEOCP_FILE_TYPE_UNKNOWN;
   get_object_name( obj_name, packed_desig);
   rval = (OBSERVE FAR *)FCALLOC( n_obs + 1, sizeof( OBSERVE));
   input_coordinate_epoch = 2000.;
   while( fgets( buff, sizeof( buff), ifile) && i != n_obs)
      {
      line_no++;
      if( !i && debug_level)
         debug_printf( "Loading observations...");
      if( debug_level > 2)
         debug_printf( "Line %d: %s", line_no, buff);
      if( get_neocp_data( buff, desig_from_neocp, mpc_code_from_neocp))
         if( !i && debug_level)
            debug_printf( "Got NEOCP data\n");
      if( rwo_to_mpc( buff))
         if( !i && debug_level)
            debug_printf( "Got .rwo data\n");
      xref_designation( buff);
      if( is_an_observation( buff, obj_name))
         if( parse_observation( rval + i, buff))
            return( NULL);
         else           /* Successfully-loaded observation: */
            {
            int observation_is_good = 1;

            if( buff[14] == 'S') /* satellite observation: need second line */
               {
               if( !fgets( buff, sizeof( buff), ifile) || buff[14] != 's')
                  {
                  sprintf( buff, "There is an error in the input file:  for at least one\n");
                  strcat( buff, "satellite observation,  a first line is given,  but\n");
                  strcat( buff, "no second line appears.  This data will be ignored.\n");
                  if( !warning_issued)
                     generic_message_box( buff, "o");
                  warning_issued = 1;
                  observation_is_good = 0;
                  }
               else
                  {
                  double vect[3];
                  int j;

                  line_no++;
                  rval[i].satellite_obs = (buff[32] == '1' ? 1 : 2);
                  for( j = 0; j < 3; j++)
                     {
                     vect[j] = atof( buff + 35 + j * 12);
                     if( buff[34 + j * 12] == '-')
                        vect[j] = -vect[j];
                     if( buff[32] == '1')    /* satellite obs offsets can be */
                        vect[j] /= AU_IN_KM;   /* in AU or, less common,  km */
                     }
                  equatorial_to_ecliptic( vect);
                  for( j = 0; j < 3; j++)
                     rval[i].obs_posn[j] += vect[j];
                  }
               }
            else if( buff[14] == 'V')   /* roving observer: need second line */
               {
               if( !fgets( buff, sizeof( buff), ifile) || buff[14] != 'v')
                  {
                  sprintf( buff, "There is an error in the input file:  for at least one\n");
                  strcat( buff, "roving observation,  a first line is given,  but\n");
                  strcat( buff, "no second line appears.  This data will be ignored.\n");
                  if( !warning_issued)
                     generic_message_box( buff, "o");
                  warning_issued = 1;
                  observation_is_good = 0;
                  }
               else
                  {
                  double rho_sin_phi, rho_cos_phi;

                  line_no++;
                  xref_designation( buff);

                  roving_lon = atof( buff + 34) * PI / 180.;
                  roving_lat = atof( buff + 45) * PI / 180.;
                  roving_ht_in_meters = atof( buff + 56);
                  lat_alt_to_parallax( roving_lat, roving_ht_in_meters,
                                       &rho_cos_phi, &rho_sin_phi);
                  compute_observer_loc( rval[i].jd, 3, rho_cos_phi, rho_sin_phi,
                                         roving_lon, rval[i].obs_posn);
                  compute_observer_vel( rval[i].jd, 3, rho_cos_phi, rho_sin_phi,
                                         roving_lon, rval[i].obs_vel);
                  set_obs_vect( rval + i);
                  }
               }
            else if( buff[14] == 's' || buff[14] == 'v')
               observation_is_good = 0;
            if( observation_is_good)
               {
               if( using_default_weights)    /* from 'weight.txt' */
                  rval[i].weight = get_observation_weight( rval[i].jd,
                     (int)( rval[i].obs_mag * 10. + .001), rval[i].mpc_code);
               else        /* using weights from the '#Weight' command */
                  rval[i].weight = weight;
               if( !including_obs)
                  rval[i].is_included = 0;
               i++;
               }
            }
      if( !memcmp( buff, "#Weight ", 8))
         {
         using_default_weights = 0;
         weight = atof( buff + 8);
         }
      else if( !memcmp( buff, "#default_weight", 15))
         using_default_weights = 1;
      else if( !memcmp( buff, "#coord epoch", 12))
         input_coordinate_epoch = atof( buff + 12);
      else if( !memcmp( buff, "#suppress_obs", 13))
         including_obs = 0;
      else if( !memcmp( buff, "#include_obs", 12))
         including_obs = 1;
      else if( !memcmp( buff, "#time ", 6))
         override_time = get_time_from_string( 0, buff + 6,
                           CALENDAR_JULIAN_GREGORIAN);
               /* Above allows one to reset the time of the preceding obs */
      }

   n_obs_actually_loaded = i;

            /* ShellSort observations,  in order of JD of observation: */
   for( gap = gap0; gap; gap /= 3)
      {
      int i;

      for( i = 0; i < gap; i++)
         for( j = i; j + gap < n_obs_actually_loaded; j += gap)
            if( compare_observations( rval + j + gap, rval + j) < 0)
               {
               OBSERVE temp = rval[j];

               rval[j] = rval[j + gap];
               rval[j + gap] = temp;
               if( j >= gap)
                  j -= gap + gap;
               }
      }
   monte_carlo_object_count = 0;
   n_monte_carlo_impactors = 0;
   return( rval);
}

/* find_objects_in_file( ) reads through the file of MPC astrometric data
   specified by 'filename',  and figures out which objects appear in that
   file.  Those objects can then be listed on the console (DOS_FIND) or
   a scroll box (FIND_ORB),  and the user can select one for which she wants
   to determine an orbit.  We start out by allocating room for 20 objects;
   this is expanded (realloc()ed) as we run out of space. */

OBJECT_INFO *find_objects_in_file( const char *filename,
                                         int *n_found, const char *station)
{
   FILE *ifile = fopen( filename, "rb");
   OBJECT_INFO *rval;
   int n = 0, n_alloced = 20, prev_loc = -1;
   char buff[250], mpc_code_from_neocp[4], desig_from_neocp[15];

   if( !ifile)
      {
      *n_found = -1;
      return( NULL);
      }
   *mpc_code_from_neocp = '\0';
   *desig_from_neocp = '\0';
   strcpy( mpc_code_from_neocp, "500");   /* default is geocenter */
   neocp_file_type = NEOCP_FILE_TYPE_UNKNOWN;
   rval = (OBJECT_INFO *)calloc( n_alloced + 1, sizeof( OBJECT_INFO));
   while( fgets( buff, sizeof( buff), ifile))
      {
      const int iline_len = strlen( buff);
      const int is_neocp = get_neocp_data( buff, desig_from_neocp,
                                                 mpc_code_from_neocp);

      rwo_to_mpc( buff);
      if( is_an_observation( buff, NULL))
         if( !station || !memcmp( buff + 76, station, 3))
            {
            int stepsize = 16384, loc = 0, compare = -1;
            const unsigned long jd =
                  (unsigned long)( dmy_to_day( atoi( buff + 23),
                              atoi( buff + 20),
                              atoi( buff + 15), 0) * 1440L) +
                              (unsigned long)( 1440. * atof( buff + 25));

            if( *buff == '#')
               *buff = ' ';           /* handle remarked-out lines,  too */
            xref_designation( buff);
            if( prev_loc >= 0 &&
                          !memcmp( rval[prev_loc].packed_desig, buff, 12))
               loc = prev_loc;
            else
               while( stepsize && compare)   /* binary-search for desig */
                  {
                  const int loc2 = loc + stepsize;

                  if( loc2 < n)
                     {
                     compare = memcmp( rval[loc2].packed_desig, buff, 12);
                     if( compare <= 0)
                        loc = loc2;
                     }
                  stepsize /= 2;
                  }
            while( loc < n &&
                  (compare = memcmp( rval[loc].packed_desig, buff, 12)) < 0)
               loc++;
            prev_loc = loc;
            buff[46] = '\0';
            if( combine_all_observations && n)
               {
               loc = 0;
               compare = 0;
               }
            if( compare)
               {
               memmove( rval + loc + 1, rval + loc,
                                         (n - loc) * sizeof( OBJECT_INFO));
               memcpy( rval[loc].packed_desig, buff, 12);
               rval[loc].packed_desig[12] = '\0';
               get_object_name( rval[loc].obj_name, rval[loc].packed_desig);
               rval[loc].n_obs = 0;
               rval[loc].jd_start = rval[loc].jd_end = jd;
               if( is_neocp)   /* for NEOCP obs,  we need to start at the */
                  rval[loc].file_offset = 0L;   /* beginning of the file  */
               else
                  rval[loc].file_offset = ftell( ifile) - iline_len;
               n++;
               if( n == n_alloced)
                  {
                  n_alloced += 30 + n_alloced / 3;
                  rval = (OBJECT_INFO *)realloc( rval,
                                    (n_alloced + 1) * sizeof( OBJECT_INFO));
                  }
               }
            rval[loc].n_obs++;
            if( rval[loc].jd_start > jd)
               rval[loc].jd_start = jd;
            if( rval[loc].jd_end < jd)
               rval[loc].jd_end = jd;
            }
      }
   *n_found = n;
   fclose( ifile);
   return( rval);
}

/* put_observer_data_in_text( ) takes a 'station_no' and fills 'buff'
   with a little bit of text about that station,  as found from
   STATIONS.TXT:  bits such as the lat/lon and name of the station.
   In FIND_ORB and DOS_FIND,  these details are shown for the station
   that collected the currently-selected observation. */

void put_observer_data_in_text( const char FAR *mpc_code, char *buff)
{
   double lon, rho_cos_phi, rho_sin_phi;

   if( get_observer_data( mpc_code, buff, &lon, &rho_cos_phi, &rho_sin_phi) < 0)
      {
      char tbuff[4];

      FMEMCPY( tbuff, mpc_code, 4);
      sprintf( buff, "No information about station '%s'", tbuff);
      }
   else
      {
      int i;
      char output_format[30];

      strcpy( output_format, "  (%c%.4lf %c%.4lf)");
      if( buff[12] != ' ')    /* longitude given to five places */
         output_format[7] = '5';
      else if( buff[10] == ' ')        /* longitude given to 3 places */
         output_format[7] = '3';
      else
         output_format[7] = '4';
      output_format[15] = output_format[7];

      memmove( buff, buff + 30, strlen( buff + 28));
      for( i = 0; buff[i] >= ' '; i++)
         ;
      if( rho_cos_phi)
         {
         double lat, ht_in_meters;

                 /* Cvt parallax data from AU back into earth-axis units: */
         rho_cos_phi /= EARTH_MAJOR_AXIS_IN_AU;
         rho_sin_phi /= EARTH_MAJOR_AXIS_IN_AU;
         parallax_to_lat_alt( rho_cos_phi, rho_sin_phi, &lat, &ht_in_meters);
         sprintf( buff + i, output_format,
                           (lat > 0. ? 'N' : 'S'), fabs( lat) * 180. / PI,
                           (lon > 0. ? 'E' : 'W'), fabs( lon) * 180. / PI);
         }
      else
         buff[i] = '\0';
      }
}

static char *edata;
static size_t edata_len = 0;
static const char *environ_dot_dat = "environ.dat";

const char *get_environment_ptr( const char *env_ptr)
{
   unsigned i, j;
   const char *rval = NULL;
   unsigned env_ptr_len;

   if( !env_ptr)
      {
      if( edata)
         free( edata);
      edata = NULL;
      edata_len = 0;
      return( rval);
      }

   env_ptr_len = strlen( env_ptr);
   if( !edata)
      {
      edata = (char *)load_file_into_memory( environ_dot_dat, &edata_len);

      if( !edata)
         {
         edata = (char *)malloc( 4);      /* just so we've got a valid */
         edata_len = 0;                   /* pointer to free up later on */
         }
      edata[edata_len] = '\0';
      for( i = 0; i < edata_len; i++)
         if( edata[i] == 10 || edata[i] == 13)
            edata[i] = 0;
      }

   i = 0;
   while( i < edata_len && !rval)
      {
      const char *tptr = edata + i;

      for( j = 0; tptr[j]; j++)
         ;
      if( j > env_ptr_len && !memcmp( tptr, env_ptr, env_ptr_len) &&
                         tptr[env_ptr_len] == '=')
         rval = tptr + env_ptr_len + 1;
      i += j;
      while( !tptr[j] && i < edata_len)
         {
         j++;
         i++;
         }
      }
   if( !rval)
      rval = "";
   return( rval);
}

void set_environment_ptr( const char *env_ptr, const char *new_value)
{
   FILE *ofile;
   unsigned i, found_it = 0;
   const unsigned env_ptr_len = strlen( env_ptr);

   if( !edata)          /* just to make sure the data gets loaded... */
      get_environment_ptr( "UNUSED");

   ofile = fopen( environ_dot_dat, "wb");
   for( i = 0; i < edata_len; i++)
      if( !i || (edata[i] && !edata[i - 1]))
         {
         if( !memcmp( edata + i, env_ptr, env_ptr_len) &&
                             edata[i + env_ptr_len] == '=')
            {
            found_it = 1;
            fprintf( ofile, "%s=%s\n", env_ptr, new_value);
            }
         else
            fprintf( ofile, "%s\n", edata + i);
         }
   if( !found_it)       /* not a replacement,  but a new value: */
      fprintf( ofile, "%s=%s\n", env_ptr, new_value);
   fclose( ofile);
   get_environment_ptr( NULL);      /* force a reload of the env data */
}

static inline void compute_relative_velocity_vectors( const OBSERVE FAR *obs,
                                    double *vel)
{
   double j2000_vel[3], matrix[9], length;
   int i;

   for( i = 0; i < 3; i++)
      {
      j2000_vel[i] = obs->obj_vel[i] - obs->obs_vel[i];
      matrix[i] = obs->vect[i];
      }
   ecliptic_to_equatorial( j2000_vel);
   ecliptic_to_equatorial( matrix);
   length = sqrt( matrix[0] * matrix[0] + matrix[1] * matrix[1]);
   matrix[3] =  matrix[1] / length;
   matrix[4] = -matrix[0] / length;
   matrix[5] = 0.;

   matrix[6] =  matrix[4] * matrix[2];
   matrix[7] = -matrix[3] * matrix[2];
   matrix[8] = length;

            /* Now we've got an orthonormal matrix,  matrix[012] pointing */
            /* in the direction of the observation,  matrix[345] at right */
            /* angles in the equatorial plane,  matrix[678] at right angles */
            /* to both.  So we can multiply: */
   for( i = 0; i < 9; i += 3)
      vel[i / 3] = matrix[  i  ] * j2000_vel[0]
                 + matrix[i + 1] * j2000_vel[1]
                 + matrix[i + 2] * j2000_vel[2];
}

void reference_to_text( char *obuff, const char *reference)
{
   if( !strcmp( reference, "     "))       /* no reference given */
      *obuff = '\0';
   else if( !strcmp( reference, "neocp"))
      strcpy( obuff, "NEOCP");
   else if( *reference >= '0' && *reference <= '9')
      sprintf( obuff, "MPC %s", reference);
   else if( *reference >= 'a' && *reference <= 'z')
      sprintf( obuff, "MPS %d%s", *reference - 'a', reference + 1);
   else if( *reference == 'E')
      {
      sprintf( obuff, "MPEC ?  ?-%c%d", reference[1], atoi( reference + 2));
      obuff[6] = obuff[7] = '?';    /* attempt to evade trigraph oddities */
      }
   else if( *reference == 'D' && isdigit( reference[1]))
      sprintf( obuff, "DASO %d", atoi( reference + 1));
   else           /* just copy it in,  but add a space */
      {
      while( *reference >= 'A')
         *obuff++ = *reference++;
      *obuff++ = ' ';
      while( *reference == '0')
         reference++;
      strcpy( obuff, reference);
      }
}

int compute_observation_motion_details( const OBSERVE FAR *obs,
               MOTION_DETAILS *m)
{
   double vel[3];

   compute_relative_velocity_vectors( obs, vel);
   if( !obs->r)
      m->ra_motion = m->dec_motion = m->position_angle_of_motion = 0.;
   else
      {
      m->ra_motion = vel[1] * (180. / PI) / obs->r;
      m->dec_motion = vel[2] * (180. / PI) / obs->r;
      m->ra_motion *= -60. / 24.;                 /* cvt to arcmin/hr, or */
      m->dec_motion *= 60. / 24.;                 /* arcsec/minute        */
      m->position_angle_of_motion =
                  180. + (180. / PI) * atan2( -m->ra_motion, -m->dec_motion);
      }
   m->total_motion = sqrt( m->ra_motion * m->ra_motion
                                        + m->dec_motion * m->dec_motion);
   m->xresid = (obs->ra - obs->computed_ra) * cos( obs->dec);
   m->yresid = obs->dec - obs->computed_dec;
               /* cvt xresid, yresid from radians to arcseconds: */
   m->xresid *= (180. / PI) * 3600.;
   m->yresid *= (180. / PI) * 3600.;
               /* time residual is in seconds */
   m->time_residual = m->xresid * m->ra_motion + m->yresid * m->dec_motion;
   m->time_residual *= 60. / (m->total_motion * m->total_motion);
   m->cross_residual = m->xresid * m->dec_motion - m->yresid * m->ra_motion;
   m->cross_residual /= m->total_motion;
   m->radial_vel = vel[0] * AU_IN_KM / 86400.;
   return( 0);
}

         /* motion is in arcminutes/hour */
static void format_motion( char *obuff, const double motion)
{
#ifdef _WIN32
   static const char degree_symbol = (char)0xb0;
#else
   static const char degree_symbol = (char)0xf8;
#endif

   if( motion < 99. && motion > -99.)
      sprintf( obuff, "%5.2lf'/hr", motion);
   else if( motion < 999. && motion > -999.)
      sprintf( obuff, "%5.1lf'/hr", motion);
   else if( motion < 99999. && motion > -99999.)
      sprintf( obuff, "%5.0lf'/hr", motion);
   else if( motion < 99999. * 60. && motion > -99999. * 60.)
      sprintf( obuff, "%5.0lf%c/hr", motion / 60., degree_symbol);
   else if( motion < 99999. * 3600. && motion > -99999. * 3600.)
      sprintf( obuff, "%5.0lf%c/min", motion / 3600., degree_symbol);
   else if( motion < 99999. * 86400. && motion > -99999. * 86400.)
      sprintf( obuff, "%5.0lf%c/sec", motion / 86400., degree_symbol);
   else
      strcpy( obuff, "!!!!!");
}

int generate_observation_text( const OBSERVE FAR *obs, const int n_obs,
                      const int obs_idx, const int line_number, char *buff)
{
   const OBSERVE FAR *optr = obs + obs_idx;
   double earth_sun = 0.;
   int i;

   for( i = 0; i < 3; i++)
      earth_sun += optr->obs_posn[i] * optr->obs_posn[i];
   earth_sun = sqrt( earth_sun);
   *buff = '\0';
   switch( line_number)
      {
      case 0:
         {
         const double cos_elong = (earth_sun * earth_sun + optr->r * optr->r
                                    - optr->solar_r * optr->solar_r)
                                    / (2. * earth_sun * optr->r);
         const double cos_phase = (optr->r * optr->r + optr->solar_r * optr->solar_r
                                    - earth_sun * earth_sun)
                                    / (2. * optr->solar_r * optr->r);
         MOTION_DETAILS m;
         char ra_motion_buff[15], dec_motion_buff[15];

         compute_observation_motion_details( optr, &m);
         sprintf( buff, "Elong %5.1lf    Phase %5.1lf    ",
                                     acose( cos_elong) * 180. / PI,
                                     acose( cos_phase) * 180. / PI);
         format_motion( ra_motion_buff, m.ra_motion);
         format_motion( dec_motion_buff, m.dec_motion);
         sprintf( buff + strlen( buff), "RA vel %s   decvel %s   dT=",
                                        ra_motion_buff, dec_motion_buff);
         buff += strlen( buff);

         if( fabs( m.time_residual) < .999)
            {
            sprintf( buff, "%.3lf sec", fabs( m.time_residual));
            *buff = (m.time_residual > 0. ? '+' : '-');
            }
         else if( fabs( m.time_residual) < 99.9)
            sprintf( buff, "%.2lf sec", m.time_residual);
         else if( fabs( m.time_residual / 60.) < 99.9)
            sprintf( buff, "%.2lf min", m.time_residual / 60.);
         else if( fabs( m.time_residual / 60.) < 9999.)
            sprintf( buff, "%d min", (int)( m.time_residual / 60.));
         else if( fabs( m.time_residual / 3600.) < 9999.)
            sprintf( buff, "%d hr", (int)( m.time_residual / 3600.));
         else
            strcpy( buff, "!!!!");
         }
         break;
      case 1:
         {
         MOTION_DETAILS m;
         char tbuff[15];
         double tdiff;
         const double jan_1_1970 = 2440587.5;

         compute_observation_motion_details( optr, &m);
         format_motion( tbuff, m.total_motion);
         sprintf( buff, "ang vel %s at PA %.1lf", tbuff,
                   m.position_angle_of_motion);
         sprintf( buff + strlen( buff), "   radial vel %.3lf km/s  cross ",
                                   m.radial_vel);
         if( fabs( m.cross_residual) < 9.9)
            sprintf( tbuff, "%.2lf", m.cross_residual);
         else if( fabs( m.cross_residual) < 99.9)
            sprintf( tbuff, "%4.1lf", m.cross_residual);
         else if( fabs( m.cross_residual) < 9999.)
            sprintf( tbuff, "%4d", (int)m.cross_residual);
         else
            strcpy( tbuff, "!!!!");
         strcat( buff, tbuff);
         tdiff = jan_1_1970 + (double)time( NULL) / 86400. - optr->jd;
         if( fabs( tdiff < 1. / 24.))     /* less than an hour ago */
            sprintf( tbuff, "%d min", (int)( tdiff * 1440.));
         else if( fabs( tdiff) < 1.)
            sprintf( tbuff, "%.1lf hr", tdiff * 24.);
         else if( fabs( tdiff) < 100.)
            sprintf( tbuff, "%.1lf days", tdiff);
         else
            *tbuff = '\0';
         if( *tbuff)
            sprintf( buff + strlen( buff), "  %s ago", tbuff);
         if( tdiff < 0.)
            strcat( buff, "!!!!!");
         }
         break;
      case 2:
         {
         strcpy( buff, "Delta=");
         buff += strlen( buff);
         format_dist_in_buff( buff, optr->r);  /* ephem0.cpp */

         strcat( buff, "  r=");
         buff += strlen( buff);
         format_dist_in_buff( buff, optr->solar_r);  /* ephem0.cpp */
         strcat( buff, "  ");
         if( optr->obs_mag > 0. && optr->obs_mag < 99.99)
            sprintf( buff + strlen( buff), "mag=%5.2lf  ", optr->obs_mag);
         else
            strcat( buff, "           ");
         if( optr->computed_mag)
            sprintf( buff + strlen( buff), "mag (computed)=%5.2lf   ",
                      optr->computed_mag);

         full_ctime( buff + strlen( buff),
                           optr->jd - td_minus_utc( optr->jd) / 86400.,
                           FULL_CTIME_TENTHS_SEC | FULL_CTIME_YMD);
         }
         break;
      case 3:
         {
         DPT sun_alt_az, object_alt_az;

         if( optr->weight > 1.01 || optr->weight < .99)
            {
            strcpy( buff, "Weight ");
            sprintf( buff + 7, (optr->weight < .001 ? "%.2e " : "%.4lf "),
                                  optr->weight);
            for( i = strlen( buff); buff[i - 1] == '0'; i--)
               buff[i] = '\0';
            }
         buff += strlen( buff);
         reference_to_text( buff, optr->reference);
         if( *buff)
            strcat( buff, "  ");
         if( !get_obs_alt_azzes( optr, &sun_alt_az, &object_alt_az))
            {
            sprintf( buff + strlen( buff), "Obj alt %.1lf az %.1lf  ",
                     object_alt_az.y * 180. / PI,
                     object_alt_az.x * 180. / PI + 180.);
            sprintf( buff + strlen( buff), "Sun alt %.1lf az %.1lf",
                     sun_alt_az.y * 180. / PI,
                     sun_alt_az.x * 180. / PI + 180.);
            }
         }
         break;
      case 4:
         put_observer_data_in_text( optr->mpc_code, buff);
         break;
     }
   return( 0);
}

int sanity_test_observations( const char *filename)
{
   FILE *ifile = fopen( filename, "rb");
   FILE *ofile = NULL;
   long line_no = 0L;
   char buff[250];
   OBSERVE obs;
   int n_problems_found = 0;

   if( !ifile)
      return( -1);
   while( fgets( buff, sizeof( buff), ifile))
      {
      line_no++;
      if( is_an_observation( buff, NULL))
         if( !parse_observation( &obs, buff))
            {
            DPT alt_az_sun, alt_az_obj;

            if( !get_obs_alt_azzes( &obs, &alt_az_sun, &alt_az_obj))
               if( alt_az_sun.y > 0. || alt_az_obj.y < 0.)
                  {
                  if( !ofile)
                     ofile = fopen( "sanity.txt", "wb");
                  printf( "Line %ld: Sun alt %.1lf az %.1lf; obj alt %.1lf az %.1lf\n",
                           line_no,
                           alt_az_sun.y * 180. / PI,
                           alt_az_sun.x * 180. / PI + 180.,
                           alt_az_obj.y * 180. / PI,
                           alt_az_obj.x * 180. / PI + 180.);
                  printf( "%s", buff);
                  fprintf( ofile, "Line %ld: Sun alt %.1lf az %.1lf; obj alt %.1lf az %.1lf\n",
                           line_no,
                           alt_az_sun.y * 180. / PI,
                           alt_az_sun.x * 180. / PI + 180.,
                           alt_az_obj.y * 180. / PI,
                           alt_az_obj.x * 180. / PI + 180.);
                  fprintf( ofile,  "%s", buff);
                  n_problems_found++;
                  }
            }
      }
   fclose( ifile);
   if( ofile)
      fclose( ofile);
   return( n_problems_found);
}

#ifdef _WIN32
int copy_buffer_to_clipboard( const char *contents, const long length);
int copy_file_to_clipboard( const char *filename);    /* mpc_obs.cpp */
int clipboard_to_file( const char *filename);         /* mpc_obs.cpp */
      /* Following is copied shamelessly from pdcclip.c from PDCurses. */

int copy_buffer_to_clipboard( const char *contents, const long length)
{
   HGLOBAL ptr1;
   LPTSTR ptr2;

   if (!OpenClipboard(NULL))
      return -3;

   ptr1 = GlobalAlloc(GMEM_MOVEABLE|GMEM_DDESHARE,
      (length + 1) * sizeof(TCHAR));

   if (!ptr1)
      return -4;

   ptr2 = (LPTSTR)GlobalLock(ptr1);

   memcpy((char *)ptr2, contents, length + 1);
   GlobalUnlock(ptr1);
   EmptyClipboard();

   if (!SetClipboardData( CF_TEXT, ptr1))
   {
      GlobalFree(ptr1);
      return -5;
   }

   CloseClipboard();
   GlobalFree(ptr1);

   return 0;
}

int copy_file_to_clipboard( const char *filename)
{
   FILE *ifile = fopen( filename, "rb");
   int rval;

   if( ifile)
      {
      size_t filesize;
      char *buff;

      fseek( ifile, 0L, SEEK_END);
      filesize = ftell( ifile);
      fseek( ifile, 0L, SEEK_SET);
      buff = (char *)malloc( filesize);
      if( buff)
         {
         fread( buff, 1, filesize, ifile);
         rval = copy_buffer_to_clipboard( buff, filesize);
         free( buff);
         }
      else
         rval = -2;
      fclose( ifile);
      }
   else
      rval = -1;
   return( rval);
}

int clipboard_to_file( const char *filename)
{
    int rval;

    if( !OpenClipboard(NULL))
        rval =  -1;
    else
        {
        char *text;
        FILE *ofile;

        if( (text = (char *)GetClipboardData( CF_OEMTEXT)) == NULL)
            rval = -2;
        else if( (ofile = fopen( filename, "wb")) != NULL)
            {
            rval = 0;
            fwrite( text, 1, strlen( text), ofile);
            fclose( ofile);
            }
        else
            rval = -3;
        CloseClipboard();
        }
    return rval;
}
#endif         // #ifdef _WIN32
