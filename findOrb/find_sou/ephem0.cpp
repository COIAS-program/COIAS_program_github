#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>
#include "watdefs.h"
#include "afuncs.h"
#include "lunar.h"
#include "date.h"
#include "comets.h"
#include "mpc_obs.h"

#define J2000 2451545.0
#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)
#define EARTH_MAJOR_AXIS_IN_AU (EARTH_MAJOR_AXIS / (1000. * AU_IN_KM))
#define PI 3.141592653589793238462643383279502884197169399375105
#define LOG_10  2.302585
#define LIGHT_YEAR_IN_KM    (365.25 * 86400. * 299792.456)

// #define ROB_MATSON_TEST_CODE     1

void integrate_orbit( double *orbit, double t0, double t1);
double calc_obs_magnitude( const int is_comet, const double obj_sun,
          const double obj_earth, const double earth_sun); /* elem_out.cpp */
int lat_alt_to_parallax( const double lat, const double ht_in_meters,
                double *rho_cos_phi, double *rho_sin_phi);   /* ephem0.cpp */
int parallax_to_lat_alt_general( const double rho_cos_phi,
               const double rho_sin_phi,
               double *lat, double *ht_in_planetary_radii,
               const double axis_ratio);                      /* ephem0.cpp */
int parallax_to_lat_alt( const double rho_cos_phi, const double rho_sin_phi,
               double *lat, double *ht_in_meters);           /* ephem0.cpp */
int write_residuals_to_file( const char *filename, const char *ast_filename,
          const int n_obs, const OBSERVE FAR *obs_data, const int format);
void put_observer_data_in_text( const char FAR *mpc_code, char *buff);
int compute_observer_loc( const double jde, const int planet_no,
               const double rho_cos_phi,                    /* mpc_obs.cpp */
               const double rho_sin_phi, const double lon, double FAR *offset);
int compute_observer_vel( const double jde, const int planet_no,
               const double rho_cos_phi,                    /* mpc_obs.cpp */
               const double rho_sin_phi, const double lon, double FAR *offset);
int make_pseudo_mpec( const char *mpec_filename, const char *obj_name);
                                              /* ephem0.cpp */
void ecliptic_to_equatorial( double FAR *vect);               /* mpc_obs.cpp */
void remove_trailing_cr_lf( char *buff);      /* ephem0.cpp */
void create_obs_file( const OBSERVE FAR *obs, int n_obs);
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
void set_environment_ptr( const char *env_ptr, const char *new_value);
int text_search_and_replace( char FAR *str, const char *oldstr,
                                     const char *newstr);   /* ephem0.cpp */
void format_dist_in_buff( char *buff, const double dist_in_au); /* ephem0.c */
double vector3_length( const double *vect);                 /* ephem0.cpp */
int debug_printf( const char *format, ...);                /* runge.cpp */

int lat_alt_to_parallax( const double lat, const double ht_in_meters,
                    double *rho_cos_phi, double *rho_sin_phi)
{
   const double u = atan( sin( lat) * EARTH_AXIS_RATIO / cos( lat));

   *rho_sin_phi = EARTH_AXIS_RATIO * sin( u) +
                           (ht_in_meters / EARTH_MAJOR_AXIS) * sin( lat);
   *rho_cos_phi = cos( u) + (ht_in_meters / EARTH_MAJOR_AXIS) * cos( lat);
   *rho_sin_phi *= EARTH_MAJOR_AXIS_IN_AU;
   *rho_cos_phi *= EARTH_MAJOR_AXIS_IN_AU;
   return( 0);
}

/* Following is the general procedure applicable for all planets;  after
this is the 'parallax_to_lat_alt' routine,  which assumes terrestrial
radius and flattening. */

int parallax_to_lat_alt_general( const double rho_cos_phi,
               const double rho_sin_phi,
               double *lat, double *ht_in_planetary_radii,
               const double axis_ratio)
{
   const double tan_u = (rho_sin_phi / rho_cos_phi) / axis_ratio;
   const double radius = sqrt( rho_cos_phi * rho_cos_phi
                             + rho_sin_phi * rho_sin_phi);
   const double ang = atan( rho_sin_phi / rho_cos_phi);
   const double planet_radius = cos( ang) * cos( ang) +
                           sin( ang) * sin( ang) * axis_ratio;

   *ht_in_planetary_radii = (radius - planet_radius);
   *lat = atan( tan_u / axis_ratio);
   return( 0);
}

int parallax_to_lat_alt( const double rho_cos_phi, const double rho_sin_phi,
               double *lat, double *ht_in_meters)
{
   parallax_to_lat_alt_general( rho_cos_phi, rho_sin_phi, lat, ht_in_meters,
                  EARTH_AXIS_RATIO);
   *ht_in_meters *= EARTH_MAJOR_AXIS;
   return( 0);
}

double vector3_length( const double *vect)
{
   return( sqrt( vect[0] * vect[0] + vect[1] * vect[1] + vect[2] * vect[2]));
}

/* format_dist_in_buff() formats the input distance (in AU) into a
seven-byte buffer.  It does this by choosing suitable units: kilometers
if the distance is less than a million km,  AU out to 10000 AU,  then
light-years.  In actual use,  light-years indicates some sort of error,
but I wanted the program to handle that problem without just crashing.

NOTE:  It used to be that I followed MPC practice in showing all distances
between .01 and ten AU in the form d.dddd , but now,  that's only true for
one to ten AU.  For distances less than 1 AU,  I'm using .ddddd,  thereby
getting an extra digit displayed.   */

void format_dist_in_buff( char *buff, const double dist_in_au)
{
   if( dist_in_au < 0.)
      strcpy( buff, " <NEG!>");
   else
      {
      const double dist_in_km = dist_in_au * AU_IN_KM;
      const char *fmt;
                  /* for objects within a million km (about 2.5 times  */
                  /* the distance to the moon),  switch to km          */
      if( dist_in_km < 1000000.)
         sprintf( buff, "%7.0lf", dist_in_km);
      else if( dist_in_au > 9999.999)
         {
         const double dist_in_light_years =
                               dist_in_au * AU_IN_KM / LIGHT_YEAR_IN_KM;

         if( dist_in_light_years > 9999.9)
            fmt = " <HUGE>";
         else if( dist_in_light_years > 99.999)  /* " 1234LY" */
            fmt = "%5.0lfLY";
         else if( dist_in_light_years > 9.999)   /* " 12.3LY" */
            fmt = "%5.1lfLY";
         else if( dist_in_light_years > .999)
            fmt = "%5.2lfLY";           /* " 1.23LY" */
         else
            fmt = "%5.3lfLY";           /* " .123LY" */
         sprintf( buff, fmt, dist_in_light_years);
         }
      else
         {
         if( dist_in_au > 999.999)
            fmt = "%7.1lf";             /* " 1234.5" */
         else if( dist_in_au > 99.999)
            fmt = "%7.2lf";             /* " 123.45" */
         else if( dist_in_au > 9.999)
            fmt = "%7.3lf";             /* " 12.345" */
         else if( dist_in_au > .99)     /* used to be .01 */
            fmt = "%7.4lf";             /* " 1.2345" */
         else
            fmt = "%7.5lf";             /* " .12345" */
         sprintf( buff, fmt, dist_in_au);
         }
      *buff = ' ';                /* remove leading zero for small amts */
      }
}


static void format_velocity_in_buff( char *buff, const double vel)
{
   const char *format;

   if( vel < 9.999 && vel > -9.999)
      format = "%7.3lf";
   else if( vel < 99.999 && vel > -99.999)
      format = "%7.2lf";
   else if( vel < 999.9 && vel > -999.9)
      format = "%7.1lf";
   else
      format =  " !!!!!!";
   sprintf( buff, format, vel);
}

/* Rob Matson asked about having the program produce ECF (Earth-Centered
Fixed) coordinates,  in geometric lat/lon/altitude form.  I just hacked
it in,  then commented it out.  I'd have removed it,  but I'm thinking
this might be a useful option someday.  */

#ifdef ROB_MATSON_TEST_CODE
int find_lat_lon_alt( const double jd, const double *ivect,  /* collide.cpp */
                                       double *lat_lon_alt);
#endif

/* 'get_step_size' parses input text to get a step size in days,  so that */
/* '4h' becomes .16667 days,  '30m' becomes 1/48 day,  and '10s' becomes  */
/* 10/(24*60*60) days.  The units (days, hours, minutes,  or seconds) are */
/* returned in 'step_units' if the input pointer is non-NULL.  The number */
/* of digits necessary is returned in 'step_digits' if that pointer is    */
/* non-NULL.  Both are used to ensure correct time format in ephemeris    */
/* output;  that is,  if the step size is (say) .05d,  the output times   */
/* ought to be in a format such as '2009 Mar 8.34', two places in days.   */

double get_step_size( const char *stepsize, char *step_units, int *step_digits)
{
   double step = 0.;
   char units = 'd';

   if( sscanf( stepsize, "%lf%c", &step, &units) >= 1)
      if( step)
         {
         if( step_digits)
            {
            double tval = fabs( step);

            for( *step_digits = 0; tval < .999; (*step_digits)++)
               tval *= 10.;
            }
         units = tolower( units);
         if( step_units)
            *step_units = units;
         switch( units)
            {
            case 'd':
               break;
            case 'h':
               step /= 24.;
               break;
            case 'm':
               step /= 1440.;
               break;
            case 's':
               step /= 86400.;
               break;
            case 'w':
               step *= 7.;
               break;
            case 'y':
               step *= 365.25;
               break;
            }
         }
   return( step);
}

int ephemeris_in_a_file( const char *filename, const double *orbit,
         const int planet_no,
         const double epoch_jd, const double jd_start, const char *stepsize,
         const double abs_mag,  const double lon,
         const double rho_cos_phi, const double rho_sin_phi,
         const int n_steps, const int is_comet, const char *note_text,
         const int options)
{
   double orbi[6], step;
   double prev_ephem_t = epoch_jd, prev_radial_vel = 0.;
   int i, j, date_format, hh_mm, n_step_digits;
   FILE *ofile;
   char step_units;
   const char *timescale = get_environment_ptr( "TT_EPHEMERIS");
   const int show_alt_az = ((options & OPTION_ALT_AZ_OUTPUT)
                  && rho_cos_phi && rho_sin_phi);

   step = get_step_size( stepsize, &step_units, &n_step_digits);
   if( !step)
      return( -2);
   ofile = fopen( filename, "w");
   if( !ofile)
      return( -1);
   memcpy( orbi, orbit, 6 * sizeof( double));
   setvbuf( ofile, NULL, _IONBF, 0);
   switch( step_units)
      {
      case 'd':
         hh_mm = 0;
         date_format = FULL_CTIME_DATE_ONLY;
         break;
      case 'h':
         hh_mm = 1;
         date_format = FULL_CTIME_FORMAT_HH;
         break;
      case 'm':
         hh_mm = 2;
         date_format = FULL_CTIME_FORMAT_HH_MM;
         break;
      case 's':
      default:
         hh_mm = 3;
         date_format = FULL_CTIME_FORMAT_SECONDS;
         break;
      }
   date_format |= FULL_CTIME_YEAR_FIRST | FULL_CTIME_MONTH_DAY
            | FULL_CTIME_MONTHS_AS_DIGITS | FULL_CTIME_LEADING_ZEROES;
   date_format |= (n_step_digits << 4);
   if( options & OPTION_STATE_VECTOR_OUTPUT)
      {
      timescale = "y";        /* force TT output */
      fprintf( ofile, "%.5lf %lf %d\n", jd_start, step, n_steps);
      }
   else
      {
      char hr_min_text[80];
      const char *pre_texts[4] = { "", " HH", " HH:MM", " HH:MM:SS" };

      strcpy( hr_min_text, pre_texts[hh_mm]);
      if( n_step_digits)
         {
         strcat( hr_min_text, ".");
         for( i = n_step_digits; i; i--)
            {
            char tbuff[2];

            tbuff[0] = step_units;
            tbuff[1] = '\0';
            strcat( hr_min_text, tbuff);
            }
         }
      if( note_text)
         fprintf( ofile, "#%s\n", note_text);
      fprintf( ofile, "Date (%s) %s   RA              ",
                     (*timescale ? "TT" : "UT"), hr_min_text);
      fprintf( ofile, "Dec         delta   r     elong mag");

      if( options & OPTION_MOTION_OUTPUT)
         fprintf( ofile, "  '/hr   PA ");
      if( show_alt_az)
         fprintf( ofile, "  alt  az");
      if( options & OPTION_RADIAL_VEL_OUTPUT)
         fprintf( ofile, "   rvel ");
      fprintf( ofile, "\n");

      for( i = 0; hr_min_text[i]; i++)
         if( hr_min_text[i] != ' ')
            hr_min_text[i] = '-';
      fprintf( ofile, "---- -- --%s  ------------   ",  hr_min_text);
      fprintf( ofile, "------------  ------ ------ ----- --- ");
      if( options & OPTION_MOTION_OUTPUT)
         fprintf( ofile, " ----- -----");
      if( show_alt_az)
         fprintf( ofile, " --- ---");
      if( options & OPTION_RADIAL_VEL_OUTPUT)
         fprintf( ofile, " ------");
      fprintf( ofile, "\n");
      }

   for( i = 0; i < n_steps; i++)
      {
      double ephemeris_t, utc;
      double topo[3], r = 0., solar_r = 0., obs_posn[3];
      double obs_vel[3], topo_vel[3];
#ifdef ROB_MATSON_TEST_CODE
      double lat_lon_alt[3];
#endif
      double ra, dec, sec, earth_r = 0.;
      int hr, min, deg, dec_sign = '+';
      char buff[180], ra_buff[80], dec_buff[80], date_buff[80];
      char r_buff[10], solar_r_buff[10];
      double cos_elong;
//    const double curr_jd = jd_start + (double)i * step;
      const double curr_jd =
              floor( (jd_start - .5) / step + (double)i + .5) * step + .5;
      const double delta_t = td_minus_utc( curr_jd) / 86400.;
      OBSERVE obs;

      if( *timescale)                     /* we want a TT ephemeris */
         {
         ephemeris_t = curr_jd;
         utc = curr_jd - delta_t;
         }
      else                                /* "standard" UTC ephemeris */
         {
         ephemeris_t = curr_jd + delta_t;
         utc = curr_jd;
         }
      integrate_orbit( orbi, prev_ephem_t, ephemeris_t);
      prev_ephem_t = ephemeris_t;
      compute_observer_loc( ephemeris_t, planet_no, rho_cos_phi, rho_sin_phi,
                              lon, obs_posn);
      compute_observer_vel( ephemeris_t, planet_no, rho_cos_phi, rho_sin_phi,
                              lon, obs_vel);

      for( j = 0; j < 3; j++)
         {
         topo[j] = orbi[j] - obs_posn[j];
         topo_vel[j] = orbi[j + 3] - obs_vel[j];
         r += topo[j] * topo[j];
         }
      r = sqrt( r);
                 /* for non-state-vector output,  include light-time lag: */
      if( !(options & OPTION_STATE_VECTOR_OUTPUT))
         for( j = 0; j < 3; j++)
            topo[j] -= orbi[j + 3] * r / AU_PER_DAY;

      memset( &obs, 0, sizeof( OBSERVE));
      obs.r = vector3_length( topo);
      for( j = 0; j < 3; j++)
         {
         obs.vect[j] = topo[j] / r;
         obs.obs_vel[j] = -topo_vel[j];
         }
                  /* rotate topo from ecliptic to equatorial */
      ecliptic_to_equatorial( topo);                           /* mpc_obs.cpp */
      ecliptic_to_equatorial( topo_vel);
      ecliptic_to_equatorial( obs_posn);

      if( options & OPTION_STATE_VECTOR_OUTPUT)
         {
         sprintf( buff, "%.5lf %15.10lf %15.10lf %15.10lf",
                           curr_jd, topo[0], topo[1], topo[2]);
         if( options & OPTION_VELOCITY_OUTPUT)
            sprintf( buff + strlen( buff), "  %15.10lf %15.10lf %15.10lf",
                           topo_vel[0], topo_vel[1], topo_vel[2]);
         }
      else
         {
         DPT ra_dec;
         double radial_vel = 0;

         r = 0.;
         for( j = 0; j < 3; j++)
            {
            r += topo[j] * topo[j];
            solar_r += orbi[j] * orbi[j];
            earth_r += obs_posn[j] * obs_posn[j];
            radial_vel += topo[j] * topo_vel[j];
            }
         r = sqrt( r);
         radial_vel /= r;
         solar_r = sqrt( solar_r);
         earth_r = sqrt( earth_r);
         cos_elong = r * r + earth_r * earth_r - solar_r * solar_r;
         cos_elong /= 2. * earth_r * r;

         ra_dec.x = atan2( topo[1], topo[0]);
         ra = ra_dec.x * 12. / PI;
         if( ra < 0.) ra += 24.;
         hr = (int)ra;
         min = (int)((ra - (double)hr) * 60.);
         sec =       (ra - (double)hr) * 3600. - 60. * (double)min;
         sprintf( ra_buff, "%02d %02d %6.3lf", hr, min, sec);
         if( ra_buff[6] == ' ')        /* leading zero */
            ra_buff[6] = '0';

         ra_dec.y = asin( topo[2] / r);
         dec = ra_dec.y * 180. / PI;
         if( dec < 0.)
            {
            dec = -dec;
            dec_sign = '-';
            }
         deg = (int)dec;
         min = (int)( (dec - (double)deg) * 60.);
         sec =        (dec - (double)deg) * 3600. - (double)min * 60.;
         sprintf( dec_buff, "%c%02d %02d %5.2lf", dec_sign, deg, min, sec);
         if( dec_buff[7] == ' ')        /* leading zero */
            dec_buff[7] = '0';

         full_ctime( date_buff, curr_jd, date_format);
         format_dist_in_buff( r_buff, r);
         format_dist_in_buff( solar_r_buff, solar_r);
         sprintf( buff, "%s  %s   %s %s%s %5.1lf",
               date_buff, ra_buff, dec_buff, r_buff, solar_r_buff,
               acose( cos_elong) * 180. / PI);
         if( abs_mag)
            {
            double curr_mag = abs_mag + calc_obs_magnitude( is_comet,
                                 solar_r, r, earth_r);      /* orb_func.cpp */

            if( curr_mag > 99.89)       /* avoid overflow for objects     */
               curr_mag = 99.89;        /* essentially at zero elongation */
            sprintf( buff + strlen( buff), " %4.1lf", curr_mag + .05);
            }
         if( options & OPTION_MOTION_OUTPUT)
            {
            MOTION_DETAILS m;
            char motion_buff[6];
            const char *motion_format;

            compute_observation_motion_details( &obs, &m);

            if( m.total_motion > 99999.)
               motion_format = "-----";
            else if( m.total_motion > 999.)
               motion_format = "%5.0lf";
            else if( m.total_motion > 99.9)
               motion_format = "%5.1lf";
            else
               motion_format = "%5.2lf";
            sprintf( motion_buff, motion_format, m.total_motion);
            sprintf( buff + strlen( buff), " %s %5.1lf", motion_buff,
                  m.position_angle_of_motion);
            }
         if( show_alt_az)
            {
            DPT latlon, alt_az;
            double unused_ht_in_meters;

            ra_dec.x = -ra_dec.x;
            parallax_to_lat_alt( rho_cos_phi, rho_sin_phi, &latlon.y,
                                       &unused_ht_in_meters);
            latlon.x = lon;
            full_ra_dec_to_alt_az( &ra_dec, &alt_az, NULL, &latlon, utc, NULL);
            while( alt_az.x < 0.)
               alt_az.x += PI + PI;
            while( alt_az.x > PI + PI)
               alt_az.x -= PI + PI;
            sprintf( buff + strlen( buff), " %c%02d %03d",
                                 (alt_az.y > 0. ? '+' : '-'),
                                 (int)( fabs( alt_az.y * 180. / PI) + .5),
                                 (int)( alt_az.x * 180. / PI + .5));
            }
         if( options & OPTION_RADIAL_VEL_OUTPUT)
            format_velocity_in_buff( buff + strlen( buff),
                                     radial_vel * AU_IN_KM / 86400.);
         if( options & OPTION_CLOSE_APPROACHES)
            if( step > 0. && radial_vel >= 0. && prev_radial_vel < 0.
               || step < 0. && radial_vel <= 0. && prev_radial_vel > 0.)
               {
               const double delta_t =
                      - step * radial_vel / (radial_vel - prev_radial_vel);

               full_ctime( date_buff, curr_jd + delta_t,
                        FULL_CTIME_FORMAT_HH_MM
                      | FULL_CTIME_YEAR_FIRST | FULL_CTIME_MONTH_DAY
                      | FULL_CTIME_MONTHS_AS_DIGITS
                      | FULL_CTIME_LEADING_ZEROES);
               sprintf( buff, "Close approach at %s: ", date_buff);
               for( j = 0; j < 3; j++)
                  topo[j] += delta_t * topo_vel[j];
               format_dist_in_buff( buff + strlen( buff),
                        vector3_length( topo));
               }
            else        /* suppress output */
               *buff = '\0';
#ifdef NOT_IN_USE
         if( options & OPTION_SPACE_VEL_OUTPUT)
            {
                     /* get 'full' velocity; cvt AU/day to km/sec: */
            const double total_vel =
                       vector3_length( topo_vel) * AU_IN_KM / 86400.;

            format_velocity_in_buff( buff + strlen( buff), total_vel);

            }
#endif
         prev_radial_vel = radial_vel;
         }

#ifdef ROB_MATSON_TEST_CODE
      find_lat_lon_alt( ephemeris_t, topo, lat_lon_alt);
      sprintf( buff + strlen( buff), "%11.6lf%11.6lf%11.4lf",
               lat_lon_alt[0] * 180. / PI,
               lat_lon_alt[1] * 180. / PI,
               lat_lon_alt[2] * AU_IN_KM);
#endif
      if( *buff)
         fprintf( ofile, "%s\n", buff);
      }
   fclose( ofile);
   return( 0);
}

static void output_angle_to_buff( char *obuff, const double angle,
                               const int precision)
{
   const int ihr = (int)angle;
   const double min = (angle - (double)ihr) * 60.;
   const int imin = (int)min;
   const double sec = (min - (double)imin) * 60.;

   if( precision >= 100)         /* decimal quantity */
      {
      char format_buff[10];
      int i;

      sprintf( format_buff, "%%%d.0%dlf\t", (precision - 100) + 3,
                                           (precision - 100));

      sprintf( obuff, format_buff, angle);
      if( *obuff == ' ')
         *obuff = '0';
      for( i = strlen( obuff); i < 12; i++)
         obuff[i] = ' ';
      obuff[12] = '\0';
      return;
      }

   sprintf( obuff, "%02d\t", ihr);
   switch( precision)
      {
      case -1:       /* hh mm,  integer minutes */
      case -2:       /* hh mm.m,  tenths of minutes */
      case -3:       /* hh mm.mm,  hundredths of minutes */
      case -4:       /* hh mm.mmm,  milliminutes */
         {
         static const char *format_text[4] = {
                              "%2.0lf\t      ",
                              "%4.1lf     ",
                              "%5.2lf    ",
                              "%6.3lf   " };

         sprintf( obuff + 3, format_text[ -1 - precision], min);
         }
         break;
      case 0:        /* hh mm ss,  integer seconds */
      case 1:        /* hh mm ss.s,  tenths of seconds */
      case 2:        /* hh mm ss.ss,  hundredths of seconds */
      case 3:        /* hh mm ss.sss,  thousands of seconds */
         {
         static const char *format_text[4] = {
                  "%02d\t%2.0lf    ",
                  "%02d\t%4.1lf  ",
                  "%02d\t%5.2lf ",
                  "%02d\t%6.3lf"   };

         sprintf( obuff + 3, format_text[precision], imin, sec);
         if( obuff[6] == ' ')
            obuff[6] = '0';
         }
         break;
      }
   if( obuff[3] == ' ')
      obuff[3] = '0';
}

/* 'put_residual_into_text( )' expresses a residual,  from 0 to 180 degrees, */
/* such that the text starts with a space,  followed by four characters,   */
/* and a sign:  six bytes in all.  This can be in forms such as:           */
/*                                                                         */
/*  179d-    (for values above ten degrees)                                */
/*  8.7d+    (for values below 10 degrees but above 9999 arcseconds)       */
/*  7821-    (for values below 9999 arcsec but above 99 arcsec)            */
/*  12.3+    (for values above one arcsec but below 99 arcsec)             */
/*   .87-    (for values under an arcsecond)                               */

static void put_residual_into_text( char *text, const double resid)
{
   const double zval = fabs( resid);

   if( zval > 35999.9)             /* >10 degrees: show integer degrees */
      sprintf( text, "%4.0lfd", zval / 3600.);
   else if( zval > 9999.9)         /* 10 deg > x > 9999": show #.# degrees */
      sprintf( text, "%4.1lfd", zval / 3600.);
   else if( zval > 99.9)
      sprintf( text, "%5.0lf", zval);
   else if( zval > .99)
      sprintf( text, "%5.1lf", zval);
   else
      {
      sprintf( text, "%5.2lf", zval);
      text[1] = ' ';
      }
   if( !strcmp( text, "  .00"))
      text[5] = ' ';
   else
      text[5] = (resid > 0. ? '+' : '-');
   text[6] = '\0';
}

static void put_mag_resid( char *output_text, const double obs_mag,
                           const double computed_mag)
{
   if( obs_mag && computed_mag)
      sprintf( output_text, "%6.2lf ", obs_mag - computed_mag);
   else
      strcpy( output_text, "------ ");
 }

/* format_observation( ) takes an observation and produces text for it,
   suitable for display on a console (DOS_FIND) or in a Windoze scroll
   box (FIND_ORB),  or for writing to a file.  */

void format_observation( const OBSERVE FAR *obs, char *text,
                                        const int resid_format)
{
   const double pi = 3.141592653589793238462643383279502884197;
   double angle;
   char xresid[30], yresid[30];
   int i;
   const int base_format = (resid_format & 3);
   const int four_digit_years =
                    (resid_format & RESIDUAL_FORMAT_FOUR_DIGIT_YEARS);
   int month;
   long year;
   double day, utc;
   char *original_text_ptr = text;
   MOTION_DETAILS m;

   utc = obs->jd - td_minus_utc( obs->jd) / 86400.;
   day = decimal_day_to_dmy( utc, &year, &month, 0);

   if( base_format != RESIDUAL_FORMAT_SHORT)
      {
      const char *date_format_text[7] = { "%2.0lf       \t",
                                          "%4.1lf     \t",
                                          "%5.2lf    \t",
                                          "%6.3lf   \t",
                                          "%7.4lf  \t",
                                          "%8.5lf \t",
                                          "%9.6lf\t" };

      if( four_digit_years)
         sprintf( text, "%04ld\t%02d\t", year, month);
      else
         sprintf( text, "%02ld\t%02d\t", year % 100, month);
      text += strlen( text);
      if( resid_format & RESIDUAL_FORMAT_HMS)
         {
         const long seconds = (long)( day * 86400. + .001);

         sprintf( text, "%02ld %02ld:%02ld:%02ld\t", seconds / 86400,
                  (seconds / 3600) % 24, (seconds / 60) % 60, seconds % 60);
         }
      else
         sprintf( text, date_format_text[obs->time_precision], day);
      if( *text == ' ')       /* ensure a leading zero here: */
         *text = '0';
      sprintf( text + strlen( text), "%c\t%s\t",
                   (obs->is_included ? ' ' : 'X'), obs->mpc_code);
      angle = obs->ra * 12. / pi;
      if( angle < 0.) angle += 24.;
      output_angle_to_buff( text + strlen( text), angle, obs->ra_precision);
      strcat( text, (base_format == RESIDUAL_FORMAT_FULL_WITH_TABS) ?
                              "\t" : "\t ");
      }
   else        /* 'short' MPC format: */
      {
      if( four_digit_years)
         *text++ = (char)( 'A' + year / 100 - 10);
      sprintf( text, "%02ld%02d%02d %s",
                       year % 100L, month, (int)day, obs->mpc_code);
      }
   text += strlen( text);

   compute_observation_motion_details( obs, &m);        /* mpc_obs.cpp */
   if( resid_format & RESIDUAL_FORMAT_TIME_RESIDS)
      {
      if( fabs( m.time_residual) < .999)
         {
         sprintf( xresid, "%5.2lfs", fabs( m.time_residual));
         xresid[1] = (m.time_residual > 0. ? '+' : '-');
         }
      else if( fabs( m.time_residual) < 99.9)
         sprintf( xresid, "%5.1lfs", m.time_residual);
      else if( fabs( m.time_residual / 60.) < 99.9)
         sprintf( xresid, "%5.1lfm", m.time_residual / 60.);
      else if( fabs( m.time_residual / 60.) < 9999.)
         sprintf( xresid, "%5dm", (int)( m.time_residual / 60.));
      else if( fabs( m.time_residual / 3600.) < 9999.)
         sprintf( xresid, "%5dh", (int)( m.time_residual / 3600.));
      else
         strcpy( xresid, "!!!!  ");
      put_residual_into_text( yresid, m.cross_residual);
      }
   else
      {
      put_residual_into_text( xresid, m.xresid);
      put_residual_into_text( yresid, m.yresid);
      }
   if( base_format != RESIDUAL_FORMAT_SHORT)
      {
      angle = obs->dec * 180. / pi;
      if( angle < 0.)
         {
         angle = -angle;
         *text++ = '-';
         }
      else
         *text++ = '+';
      output_angle_to_buff( text, angle, obs->dec_precision);

      sprintf( text + strlen( text), "\t%s\t%s\t", xresid, yresid);
      format_dist_in_buff( xresid, obs->r);
      if( resid_format & RESIDUAL_FORMAT_MAG_RESIDS)
         put_mag_resid( yresid, obs->obs_mag, obs->computed_mag);
      else
         format_dist_in_buff( yresid, obs->solar_r);
      sprintf( text + strlen( text),
                  ((base_format == RESIDUAL_FORMAT_FULL_WITH_TABS) ?
                            "%s\t%s" : "%s%s"), xresid, yresid);
      }
   else        /* 'short' MPC format */
      {
      if( resid_format & RESIDUAL_FORMAT_MAG_RESIDS)
         {
         put_mag_resid( yresid, obs->obs_mag, obs->computed_mag);
         put_residual_into_text( xresid, sqrt( m.xresid * m.xresid
                                             + m.yresid * m.yresid));
         xresid[5] = ' ';        /* replace the '+' with a ' ' */
         }
      strcpy( text, xresid);
      strcpy( text + 6, yresid);
      text[0] = (obs->is_included ? ' ' : '(');
      text[12] = (obs->is_included ? ' ' : ')');
      text[13] = '\0';
      }
                       /* for all other formats, replace tabs w/spaces: */
   if( base_format != RESIDUAL_FORMAT_FULL_WITH_TABS)
      for( i = 0; original_text_ptr[i]; i++)
         if( original_text_ptr[i] == '\t')
            original_text_ptr[i] = ' ';
}

static const char *observe_filename = "observe.txt";

/* The MPC report format goes to only six decimal places in time,
a "microday".  If the reported time is more precise than that -- as can
happen with video observations -- a workaround is to make use of the object
motion data to adjust the position by up to half a microday.  We only do
this if the time given is more than a nanoday away from an integer
microday.  That simply avoids processing in the (overwhelmingly likely)
case that the data doesn't fall on a microday. */

static inline void set_obs_to_microday( OBSERVE FAR *obs)
{
   double delta_jd = obs->jd - floor( obs->jd);

   delta_jd = 1e+6 * delta_jd + .5;
   delta_jd = (delta_jd - floor( delta_jd) - .5) * 1e-6;
// if( delta_jd > 1e-9 || delta_jd < -1e-9)
      {
      MOTION_DETAILS m;
      const double cvt_motions_to_radians_per_day =
                  (PI / 180.) * 24. / 60.;

      compute_observation_motion_details( obs, &m);
      obs->jd -= delta_jd;
                  /* motions are given in '/hr, a.k.a. "/min: */
      obs->ra -= m.ra_motion * delta_jd * cvt_motions_to_radians_per_day
                        / cos( obs->dec);
      obs->dec -= m.dec_motion * delta_jd * cvt_motions_to_radians_per_day;
      }
}

void recreate_observation_line( char *obuff, const OBSERVE FAR *obs)
{
   char buff[100];
   int mag_digits_to_erase = 0;
   OBSERVE tobs = *obs;

   set_obs_to_microday( &tobs);
   format_observation( &tobs, buff, 4);
   memcpy( obuff, obs->packed_id, 12);
   obuff[12] = obs->discovery_asterisk;
   obuff[13] = obs->note1;
   obuff[14] = obs->note2;
   memcpy( obuff + 15, buff, 17);      /* date/time */
   memcpy( obuff + 32, buff + 24, 12);      /* RA */
   memcpy( obuff + 44, buff + 38, 13);      /* dec */
   sprintf( obuff + 57, "%13.2lf%c%c%s%s", obs->obs_mag,
              obs->mag_band, obs->mag_band2, obs->reference, obs->mpc_code);
   if( obs->obs_mag < 0.05)        /* no mag given;  clean out that value */
      mag_digits_to_erase = 5;
   else
      mag_digits_to_erase = 2 - obs->mag_precision;
   memset( obuff + 70 - mag_digits_to_erase, ' ', mag_digits_to_erase);
   if( !obs->is_included)
      obuff[64] = 'x';
}

#ifdef NOT_QUITE_READY_YET
void recreate_second_observation_line( char *buff, const OBSERVE FAR *obs)
{
   int i;
   double vect[3];

   buff[32] = '0' + obs->satellite_obs;
   for( i = 0; i < 3; i++)
      vect[i] = obs->obs_posn[j] - ?; (gotta get earths loc somewhere...)
   ecliptic_to_equatorial( vect);
   for( i = 0; i < 3; i++)
      sprintf( buff + 33 + i * 12, "%12.8lf", vect[i]);
   buff[69] = ' ';
}
#endif

void create_obs_file( const OBSERVE FAR *obs, int n_obs)
{
   FILE *ofile = fopen( observe_filename, "wb");

   while( n_obs--)
      {
      char obuff[81];

      recreate_observation_line( obuff, obs);
      fprintf( ofile, "%s\n", obuff);
      obs++;
      }
   fclose( ofile);
}

static void add_final_period( char *buff)
{
   if( *buff && buff[strlen( buff) - 1] != '.')
      strcat( buff, ".");
}

static void tack_on_names( char *list, const char *names)
{
   while( *names)
      {
      int i, len, already_in_list = 0;

      while( *names == ' ')
         names++;
      for( len = 0; names[len] && names[len] != ','; len++)
         ;
      for( i = 0; list[i]; i++)
         if( !i || (i > 1 && list[i - 2] == ','))
            if( !memcmp( list + i, names, len))
               if( list[i + len] == ',' || !list[i + len])
                  already_in_list = 1;
      if( !already_in_list)
         {
         char *lptr;

         if( *list)
            strcat( list, ", ");
         lptr = list + strlen( list);
         memcpy( lptr, names, len);
         lptr[len] = '\0';
         }
      names += len;
      if( *names == ',')
         names++;
      }
}

static int get_observer_details( const char *observation_filename,
      const char *mpc_code, char *observers, char *measurers, char *scope)
{
   FILE *ifile = fopen( observation_filename, "rb");
   int rval = 0, no_codes_found = 1;

   *observers = *measurers = *scope = '\0';
   if( ifile)
      {
      char buff[90];

      while( fgets( buff, sizeof( buff), ifile))
         if( !memcmp( buff, "COD ", 4))
            {
            int new_code_found = 0;

            no_codes_found = 0;
            if( !memcmp( buff + 4, mpc_code, 3))
               while( fgets( buff, sizeof( buff), ifile) && !new_code_found)
                  {
                  char *add_to = NULL;

                  remove_trailing_cr_lf( buff);
                  if( !memcmp( buff, "OBS ", 4))
                     add_to = observers;
                  if( !memcmp( buff, "MEA ", 4))
                     add_to = measurers;
                  if( !memcmp( buff, "TEL ", 4))  /* allow for only one scope */
                     strcpy( scope, buff + 4);
                  if( add_to)
                     tack_on_names( add_to, buff + 4);
                  if( !memcmp( buff, "COD ", 4))
                     if( memcmp( buff + 4, mpc_code, 3))
                        new_code_found = 1;
                  }
            }
      fclose( ifile);
      add_final_period( observers);
      add_final_period( measurers);
      add_final_period( scope);
      if( !strcmp( observers, measurers))
         *measurers = '\0';
      }

   if( *observers)
      rval = 1;
   if( *measurers)
      rval |= 2;
   if( *scope)
      rval |= 4;
   if( no_codes_found)        /* we can just ignore this file completely, */
      rval = -1;              /* even for other observatory codes */
   return( rval);
}

#define REPLACEMENT_COLUMN 42

static void observer_link_substitutions( char *buff)
{
   FILE *ifile = fopen( "observer.txt", "rb");

   if( ifile)
      {
      char line[200], *loc;

      while( fgets( line, sizeof( line), ifile))
         if( *line != ';' && *line != '#')
            {
            line[REPLACEMENT_COLUMN - 1] = '\0';
            remove_trailing_cr_lf( line);
            loc = strstr( buff, line);
            if( loc)
               {
               int len = strlen( line), len2;

               if( loc[len] <= ' ' || loc[len] == '.' || loc[len] == ',')
                  {
                  remove_trailing_cr_lf( line + REPLACEMENT_COLUMN);
                  len2 = strlen( line + REPLACEMENT_COLUMN);
                  memmove( loc + len2, loc + len, strlen( loc + len) + 2);
                  memcpy( loc, line + REPLACEMENT_COLUMN, len2);
                  }
               }
            }
      fclose( ifile);
      }
}

static int write_observer_data_to_file( FILE *ofile, const char *ast_filename,
                 const int n_obs, const OBSERVE FAR *obs_data)
{
   int stations[100], n_stations = 0, i, j;
   int try_ast_file = 1, try_details_file = 1, try_scope_file = 1;

   for( i = 0; i < n_obs; i++)
      {
      int match_found = 0;

      for( j = 0; j < n_stations && !match_found; j++)
         match_found = !FSTRCMP( obs_data[i].mpc_code,
                                obs_data[stations[j]].mpc_code);
      if( !match_found)    /* new one:  add it to the array */
         stations[n_stations++] = i;
      }
               /* now do a simple bubblesort: */
   for( i = 0; i < n_stations; i++)
      for( j = 0; j < i; j++)
         if( FSTRCMP( obs_data[stations[i]].mpc_code,
                     obs_data[stations[j]].mpc_code) < 0)
            {
            int temp = stations[i];

            stations[i] = stations[j];
            stations[j] = temp;
            }

   for( i = 0; i < n_stations; i++)
      {
      char buff[200], tbuff[100];
      char details[3][300];
      int loc, j = 0, details_found = 0;

      FSTRCPY( tbuff, obs_data[stations[i]].mpc_code);
      put_observer_data_in_text( tbuff, buff);
      fprintf( ofile, "(%s) %s", tbuff, buff);

      if( try_ast_file)
         {
         details_found = get_observer_details( ast_filename, tbuff,
                                 details[0], details[1], details[2]);
         if( details_found == -1)         /* total washout; skip this file */
            {
            details_found = 0;
            try_ast_file = 0;
            }
         }

      if( !details_found && try_details_file)
         {
         details_found = get_observer_details( "details.txt", tbuff,
                                 details[0], details[1], details[2]);
         if( details_found == -1)         /* total washout; skip this file */
            {
            details_found = 0;
            try_details_file = 0;
            }
         }

      if( !details_found && try_scope_file)
         {
         details_found = get_observer_details( "scopes.txt", tbuff,
                                 details[0], details[1], details[2]);
         if( details_found == -1)         /* total washout; skip this file */
            {
            details_found = 0;
            try_scope_file = 0;
            }
         }

      fprintf( ofile, ".");
      loc = 7 + strlen( buff);
      for( j = 0; j < 3; j++)
         if( *details[j])
            {
            char inserted_text[15], *outtext = details[j];

            if( j == 2)
               strcpy( inserted_text, " ");
            else
               {
               strcpy( inserted_text, j ? " Measurer" : "  Observer");
               if( strchr( outtext, ','))
                  strcat( inserted_text, "s");
               strcat( inserted_text, " ");
               }
            memmove( outtext + strlen( inserted_text), outtext,
                              strlen( outtext) + 1);
            memcpy( outtext, inserted_text, strlen( inserted_text));
            while( *outtext)
               {
               int k, done;

               for( k = 0; outtext[k] && outtext[k] != ' '; k++)
                  ;
               done = !outtext[k];
               outtext[k] = '\0';
               if( loc + k > 78)    /* gotta go to a new line */
                  {
                  fprintf( ofile, "\n    %s", outtext);
                  loc = k + 4;
                  }
               else
                  {
                  fprintf( ofile, " %s", outtext);
                  loc += k + 1;
                  }
               outtext += k;
               if( !done)
                  outtext++;
               }
            }
      fprintf( ofile, "\n");
      }
   return( 0);
}

int write_residuals_to_file( const char *filename, const char *ast_filename,
       const int n_obs, const OBSERVE FAR *obs_data, const int resid_format)
{
   FILE *ofile = fopen( filename, "w");
   int rval = 0;

   if( ofile )
      {
      char buff[100];
      int number_lines = (n_obs + 2) / 3;
      int i;

      if( (resid_format & 3) == RESIDUAL_FORMAT_SHORT)
         for( i = 0; i < number_lines * 3; i++)
            {
            int num = (i % 3) * number_lines + i / 3;
            OBSERVE FAR *obs = ((OBSERVE FAR *)obs_data) + num;

            if( num < n_obs)
               format_observation( obs, buff, resid_format);
            else
               *buff = '\0';
            fprintf( ofile, "%s%s", buff, (i % 3 == 2) ? "\n" : "   ");
            }
      else
         for( i = 0; i < n_obs; i++)
            {
            format_observation( obs_data + i, buff, resid_format);
            fprintf( ofile, "%s\n", buff);
            }
      fprintf( ofile, "\nStation data:\n");
      write_observer_data_to_file( ofile, ast_filename, n_obs, obs_data);
      fclose( ofile);
      }
   else                    /* file not opened */
      rval = -1;
   return( rval);
}

#ifdef FUTURE_PROJECT_IN_WORKS

int create_residual_scattergram( const char *filename, const int n_obs,
                         const OBSERVE FAR *obs)
{
   const int tbl_height = 19, tbl_width = 71;
   const int xspacing = 12, yspacing = 5,
   short *remap_table = (short *)calloc( tbl_height * tbl_width, sizeof( short));
   int i, j;
   FILE *ofile = fopen( filename, "wb");

   for( i = 0; i < n_obs; i++, obs++)
      {
      const double yresid = 3600. * (180./pi) * (obs->dec - obs->computed_dec);
      const double xresid = 3600. * (180./pi) * (obs->ra - obs->computed_ra)
                                        * cos( obs->computed_dec);
      int xloc = (int)floor( xresid * (double)xspacing / .5)
      }

   fclose( ofile);
   free( remap_table);
}
#endif

            /* String file name defaults to English,  but can be replaced */
            /* with ifindorb.dat (Italian), ffindorb.dat (French), etc.   */
char findorb_language = 'e';

int get_findorb_text( char *buff, const int ival)
{
   char filename[20];
   int rval = -2;
   FILE *ifile;

   strcpy( filename, "efindorb.dat");
   *filename = findorb_language;
   ifile = fopen( filename, "r");

   if( !ifile)
      {
      strcpy( buff, filename);
      rval = -1;
      }
   else
      {
      while( fgets( buff, 80, ifile) && memcmp( buff, "@messages", 9))
         ;
      while( fgets( buff, 80, ifile) && atoi( buff) != ival)
         ;
      fclose( ifile);
      if( *buff != '@')    /* stopped before end of file; must have found */
         {                 /* target, so remove first six bytes & cr/lf  */
         remove_trailing_cr_lf( buff);
         memmove( buff, buff + 6, strlen( buff + 5));
         rval = 0;
         }
      else
         buff[4] = '\0';
      }
   return( rval);
}

void remove_trailing_cr_lf( char *buff)
{
   int i;

   for( i = 0; buff[i] && buff[i] != 13 && buff[i] != 10; i++)
      ;
   while( i && buff[i - 1] == ' ')
      i--;
   buff[i] = '\0';
}

int text_search_and_replace( char FAR *str, const char *oldstr,
                                     const char *newstr)
{
   int ilen = FSTRLEN( str), rval = 0;
   const int oldlen = strlen( oldstr);
   const int newlen = strlen( newstr);

   while( ilen >= oldlen)
      if( !FMEMCMP( str, oldstr, oldlen))
         {
         FMEMMOVE( str + newlen, str + oldlen, ilen - oldlen + 1);
         FMEMCPY( str, newstr, newlen);
         str += newlen;
         ilen -= oldlen;
         rval = 1;
         }
      else
         {
         str++;
         ilen--;
         }
   return( rval);
}

static long round_off( const double ival, const double prec)
{
   long rval = 0L, digit;
   int got_it = 0;
   double diff;

   for( digit = 10000000L; !got_it; digit /= 10)
      {
      rval = (((long)ival + digit / 2L) / digit) * digit;
      diff = fabs( (double)rval - ival);
      if( digit == 1 || diff < ival * prec)
         got_it = 1;
      }
   return( rval);
}

const char *residual_filename = "residual.txt";
const char *ephemeris_filename = "ephemeri.txt";
const char *elements_filename = "elements.txt";

int make_pseudo_mpec( const char *mpec_filename, const char *obj_name)
{
   FILE *ofile = fopen( mpec_filename, "wb");
   FILE *ifile = fopen( "header.htm", "rb");
   FILE *elements_file;
   char buff[500], mpec_buff[7];
   int line_no = 0, rval = 0, total_lines = 0;
   int mpec_no = atoi( get_environment_ptr( "MPEC"));

   if( mpec_no)
      sprintf( mpec_buff, "_%02x", mpec_no % 256);
   else
      *mpec_buff = '\0';
   if( ifile)                 /* copy header data to pseudo-MPEC */
      {
      while( fgets( buff, sizeof( buff), ifile))
         {
         char *tptr = strstr( buff, "_xx");

         if( tptr)
            {
            memmove( tptr + strlen( mpec_buff), tptr + 3, strlen( tptr));
            memcpy( tptr, mpec_buff, strlen( mpec_buff));
            }
         if( (tptr = strstr( buff, "%t")))
            {
            time_t t = time( NULL);

            tptr[1] = 's';
            fprintf( ofile, buff, ctime( &t));
            }
         else if( strstr( buff, "%s"))
            fprintf( ofile, buff, obj_name);
         else
            fputs( buff, ofile);
         }
      fclose( ifile);
      }

   if( mpec_no)
      {
      sprintf( buff, "%d", mpec_no % 255 + 1);
      set_environment_ptr( "MPEC", buff);
      }

   ifile = fopen( observe_filename, "rb");
   if( ifile)
      {
      int neocp_line_found = 0;

      while( fgets( buff, sizeof( buff), ifile))
         if( buff[14] == 's' || buff[14] == 'v')
            fprintf( ofile, "%s", buff);
         else
            {
            char mpc_code[4];

            total_lines++;
            memcpy( mpc_code, buff + 77, 3);
            buff[12] = mpc_code[3] = buff[77] = '\0';
            fprintf( ofile, "<a name=\"o%s%03d\"></a><a href=\"#r%s%03d\">%s</a>",
                     mpec_buff, total_lines, mpec_buff, total_lines, buff);
            if( !memcmp( buff + 72, "NEOCP", 5))
               {
               const char *replacement_text;

               if( !neocp_line_found)
                  replacement_text = "<font style=\"background-color: black;\">    </font>Astrometry<font style=\"background-color: black;\">    </font>redacted;<font style=\"background-color: black;\">      </font>see<font style=\"background-color: black;\">      </font>NEOCP<font style=\"background-color: black;\">NEOCP</font>";
               else
                  replacement_text = "<font style=\"background-color: black;\">                                               NEOCP</font>";
               strcpy( buff + 25, replacement_text);
               neocp_line_found = 1;
               }
            fprintf( ofile, " %s<a href=\"#stn_%s\">%s</a>\n",
                     buff + 13, mpc_code, mpc_code);
            if( !strcmp( mpc_code, "247"))         /* roving observer */
               {
               extern double roving_lon, roving_lat, roving_ht_in_meters;

               buff[12] = ' ';      /* repair line */
               buff[14] = 'v';
               sprintf( buff + 32, "%11.5lf%11.5lf%7d                247",
                        roving_lon * 180. / PI, roving_lat * 180. / PI,
                        (int)roving_ht_in_meters);
               fprintf( ofile, "%s\n", buff);
               }
            }
      fclose( ifile);
      }
   else
      rval |= 1;

   ifile = fopen( residual_filename, "rb");
   if( ifile)
      {
      FILE *obslinks_file = fopen( "obslinks.htm", "rb");
      long obslinks_header_len;
      char url[200];

      if( obslinks_file)
         while( fgets( url, sizeof( url), obslinks_file)
                        && memcmp( url, "<a name=\"0\">", 12))
            ;
      obslinks_header_len = ftell( obslinks_file);
      while( fgets( buff, sizeof( buff), ifile) && memcmp( buff, "Station", 7))
         ;
      fprintf( ofile, "<a name=\"stations\"></a>\n");
      fprintf( ofile, "<b>%s</b>", buff);
      while( fgets( buff, sizeof( buff), ifile))
         if( *buff == ' ')
            {
            observer_link_substitutions( buff);
            fprintf( ofile, "%s", buff);
            }
         else
            {
            char tbuff[4];

            memcpy( tbuff, buff + 1, 3);
            tbuff[3] = '\0';
            remove_trailing_cr_lf( buff);
            fprintf( ofile, "<a name=\"stn_%s\"></a>", tbuff);
            if( !obslinks_file)
               fprintf( ofile, "%s\n", buff);
            else
               {
               int compare, i;
               char *latlon, *remains;

               for( i = strlen( buff); i > 5 && buff[i] != ')'; i--)
                  ;
               remains = buff + i;

               if( i > 5)
                  {
                  while( i > 2 && buff[i] != '(')
                     i--;
                  buff[i - 2] = *remains = '\0';
                  latlon = buff + i + 1;
                  }
               else
                  latlon = NULL;

               fseek( obslinks_file, obslinks_header_len, SEEK_SET);
               while( (compare = memcmp( url + 19, buff + 1, 3)) != 0 &&
                                 fgets( url, sizeof( url), obslinks_file))
                  ;
               if( !compare)   /* we got a match */
                  {
                  for( i = 21; url[i] && url[i] != '>'; i++)
                     ;
                  url[i + 1] = '\0';
                  buff[5] = '\0';
                  fprintf( ofile, "%s %s%s</a>",
                          buff, url + 24, buff + 6);
                  }
               else
                  fprintf( ofile, "%s", buff);

               if( latlon)
                  {
                  double lat, lon;
                  char lat_sign, lon_sign;

                  sscanf( latlon, "%c%lf %c%lf", &lat_sign, &lat, &lon_sign, &lon);
                  if( lat_sign == 'S')
                     lat = -lat;
                  if( lon_sign == 'W')
                     lon = -lon;
                  fprintf( ofile, " (<a title=\"Click for map\"");
                  fprintf( ofile, " href=\"http://mappoint.msn.com/map.aspx?&amp;C=%.3lf,%.3lf&amp;A=1000\">",
                              lat, lon);
                  observer_link_substitutions( remains + 1);
                  fprintf( ofile, "%s</a>)%s\n", latlon, remains + 1);
                  }
               else
                  fprintf( ofile, "\n");
               }
            }
      if( obslinks_file)
         fclose( obslinks_file);
      }
   else
      rval |= 2;

   elements_file = fopen( elements_filename, "rb");
   if( elements_file)
      {
      fprintf( ofile, "<a name=\"elements%s\"></a>\n", mpec_buff);
      while( fgets( buff, sizeof( buff), elements_file) && *buff != '#')
         {
         if( !memcmp( buff, "Orbital ele", 11))
            fprintf( ofile, "<b>%s</b>", buff);
         else if( *buff == 'P' && buff[19] == 'H')
            {
            const double abs_mag = atof( buff + 20);
                     /* H=4 indicates 420 to 940 km,  so: */
            double upper_size = 940. * exp( (4. - abs_mag) * LOG_10 / 5.);
            const char *units = "km";
            const char *size_url =
                "href=\"http://www.cfa.harvard.edu/iau/lists/Sizes.html\">";
            char title[50];

            buff[19] = '\0';
            if( upper_size < 4)
               {
               upper_size *= 1000.;
               units = "meters";
               }
            sprintf( title, "\"Size is probably %ld to %ld %s\"\n",
                       round_off( upper_size / sqrt( 5.), .1),
                       round_off( upper_size, .1), units);
            fprintf( ofile, "%s<a title=%s%sH</a>%s",
                        buff, title, size_url, buff + 20);
            }
         else
            {
            text_search_and_replace( buff, "m^2", "m<sup>2</sup>");
            text_search_and_replace( buff, "   Find_Orb",
                             "   <a href=\"http://www.projectpluto.com/find_orb.htm\">Find_Orb</a>");
            fputs( buff, ofile);
            }
         }
      fclose( elements_file);
      }
   else
      rval |= 4;

               /* _now_ write out residuals: */
   if( ifile)
      {
      fseek( ifile, 0L, SEEK_SET);
      fprintf( ofile, "<a name=\"residuals%s\"></a>\n", mpec_buff);
      fprintf( ofile, "<b>Residuals in arcseconds:</b>\n");
      line_no = 0;
      while( fgets( buff, sizeof( buff), ifile) && *buff > ' ')
         {
         int i, column_off = (total_lines + 2) / 3, line;

         line_no++;
         for( i = 0; i < 3; i++)
            if( (line = line_no + column_off * i) <= total_lines)
               {
               char *tptr = buff + i * 26, tbuff[20];

               tptr[6] = '\0';         /* put out the YYMMDD... */
               fprintf( ofile, "<a name=\"r%s%03d\"></a><a href=\"#o%s%03d\">%s</a>",
                        mpec_buff, line, mpec_buff, line, tptr);

               memcpy( tbuff, tptr + 7, 3);     /* ...then the obs code.. */
               tbuff[3] = '\0';
               fprintf( ofile, " <a href=\"#stn_%s\">%s</a>", tbuff, tbuff);

               tptr[23] = '\0';        /* ...and finally,  the residuals */
               fprintf( ofile, "%s   ", tptr + 10);
               }
         fprintf( ofile, "\n");
         }
      fclose( ifile);
      }

               /* ...and now,  the ephemeris: */
   ifile = fopen( ephemeris_filename, "r");
   if( ifile && fgets( buff, sizeof( buff), ifile))
      {
      remove_trailing_cr_lf( buff);
      fprintf( ofile, "\n<a name=\"eph%s\"></a>", mpec_buff);
      if( !strcmp( buff, "#Geocentric"))
         fprintf( ofile, "<b>Ephemerides:</b>\n");
      else
         fprintf( ofile, "<b>Ephemerides (%s):</b>\n", buff + 1);

      while( fgets( buff, sizeof( buff), ifile))
         fputs( buff, ofile);
      fclose( ifile);
      }
   else
      rval |= 8;

   fprintf( ofile, "</pre></body></html>\n");
   fclose( ofile);
   return( 0);
}

