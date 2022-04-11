#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <assert.h>
#include "watdefs.h"
#include "comets.h"
#include "mpc_obs.h"
#include "date.h"
#include "afuncs.h"
#include "showelem.h"

#define J2000 2451545.
#define PI 3.141592653589793238462643383279502884197
#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)

// void elements_in_tle_format( char *buff, const ELEMENTS *elem);
int elements_in_mpcorb_format( char *buff, const char *packed_desig,
                const char *full_desig, const ELEMENTS *elem,
                const OBSERVE FAR *obs, const int n_obs);   /* orb_func.c */
int elements_in_guide_format( char *buff, const ELEMENTS *elem,
                     const char *obj_name);                 /* orb_func.c */
int find_worst_observation( const OBSERVE FAR *obs, const int n_obs);
double initial_orbit( OBSERVE FAR *obs, int n_obs, double *orbit);
double compute_rms( const OBSERVE FAR *obs, int n_obs, int method);
int set_locs( const double *orbit, double t0, OBSERVE FAR *obs, int n_obs);
double calc_obs_magnitude( const int is_comet, const double obj_sun,
          const double obj_earth, const double earth_sun); /* elem_out.cpp */
int find_best_fit_planet( const double jd, const double *ivect,
                                 double *rel_vect);         /* runge.cpp */
void observation_summary_data( char *obuff, const OBSERVE FAR *obs,
                                const int n_obs);        /* orb_func.cpp */
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
void remove_trailing_cr_lf( char *buff);      /* ephem0.cpp */
int find_relative_orbit( const double jd, const double *ivect,
               ELEMENTS *elements, double *rel_vect, const int ref_planet);
int write_tle_from_vector( char *buff, const double *state_vect,
        const double epoch, const char *norad_desig, const char *intl_desig);
double find_moid( const ELEMENTS *elem1, const ELEMENTS *elem2); /* moid4.c */
void setup_planet_elem( ELEMENTS *elem, const int planet_idx,
                                          const double t_cen);   /* moid4.c */
void set_environment_ptr( const char *env_ptr, const char *new_value);
int store_defaults( const int ephemeris_output_options);    /* elem_out.c */
int get_defaults( int *ephemeris_output_options);           /* elem_out.c */
double find_collision_time( ELEMENTS *elem, double *latlon);
int get_idx1_and_idx2( const int n_obs, const OBSERVE FAR *obs,
                                int *idx1, int *idx2);      /* elem_out.c */

double asteroid_magnitude_slope_param = .15;
double comet_magnitude_slope_param = 10.;
char default_comet_magnitude_type = 'N';

char *fgets_trimmed( char *buff, size_t max_bytes, FILE *ifile)
{
   char *rval = fgets( buff, max_bytes, ifile);

   if( rval)
      {
      int i;

      for( i = 0; buff[i] && buff[i] != 10 && buff[i] != 13; i++)
         ;
      buff[i] = '\0';
      }
   return( rval);
}

static void get_first_and_last_included_obs( const OBSERVE *obs,
              const int n_obs, int *first, int *last)
{
   if( first)
      for( *first = 0; *first < n_obs - 1 && !obs[*first].is_included;
                                    (*first)++)
         ;
   if( last)
      for( *last = n_obs - 1; *last && !obs[*last].is_included; (*last)--)
         ;
}

void make_date_range_text( char *obuff, const double jd1, const double jd2)
{
   long year, year2;
   int month, month2;
   const int day1 = (int)decimal_day_to_dmy( jd1, &year,  &month , 0);
   const int day2 = (int)decimal_day_to_dmy( jd2, &year2, &month2, 0);
   static const char *month_names[12] = { "Jan.", "Feb.", "Mar.", "Apr.", "May",
            "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec." };

   if( year == year2 && month == month2)
      sprintf( obuff, "%ld %s %d-%d", year, month_names[month - 1], day1, day2);
   else if( year == year2)
      sprintf( obuff, "%ld %s %d-%s %d", year, month_names[month - 1],
                             day1, month_names[month2 - 1], day2);
   else
      sprintf( obuff, "%ld %s %d-%ld %s %d", year, month_names[month - 1],
                             day1, year2, month_names[month2 - 1], day2);

   obuff += strlen( obuff);
   if( jd2 - jd1 < 100. / 1440.)
      sprintf( obuff, " (%.1lf min)", (jd2 - jd1) * 1440.);
   else if( jd2 - jd1 < 1.)
      sprintf( obuff, " (%.1lf hr)", (jd2 - jd1) * 24.);
}

/* observation_summary_data( ) produces the final line in an MPC report,
   such as 'From 20 observations 1997 Oct. 20-22;  RMS error .345 arcseconds'.
*/

void observation_summary_data( char *obuff, const OBSERVE FAR *obs,
                                      const int n_obs)
{
   int i, n_included, first_idx, last_idx;

   get_first_and_last_included_obs( obs, n_obs, &first_idx, &last_idx);

   for( i = n_included = 0; i < n_obs; i++)
      n_included += obs[i].is_included;
   sprintf( obuff, "From %d observations ", n_included);
   if( n_included)
      {
      obuff += strlen( obuff);
      make_date_range_text( obuff, obs[first_idx].jd, obs[last_idx].jd);
      sprintf( obuff + strlen( obuff), ";   RMS error %.3lf arcseconds",
             compute_rms( obs, n_obs, 1));
      }
}

static double centralize_ang( double ang)
{
   ang = fmod( ang, PI + PI);
   if( ang < 0.)
      ang += PI + PI;
   return( ang);
}

void convert_elements( const double epoch_from, const double epoch_to,
      double *incl, double *asc_node, double *arg_per);     /* conv_ele.cpp */

   /* Packed MPC designations have leading and/or trailing spaces.  This */
   /* function lets you get the designation minus those spaces.          */

static void packed_desig_minus_spaces( char *obuff, const char *ibuff)
{
   while( *ibuff && *ibuff == ' ')
      ibuff++;
   while( *ibuff && *ibuff != ' ')
      *obuff++ = *ibuff++;
   *obuff = '\0';
}

int elements_in_mpcorb_format( char *buff, const char *packed_desig,
                const char *full_desig, const ELEMENTS *elem,
                const OBSERVE FAR *obs, const int n_obs)   /* orb_func.c */
{
   int month, day, i, first_idx, last_idx, n_included_obs = 0;
   long year;
   const double jan_1970 = 2440587.5;
   const double rms_err = compute_rms( obs, n_obs, 1);
   double arc_length;
   char packed_desig2[40];

   packed_desig_minus_spaces( packed_desig2, packed_desig);
   sprintf( buff, "%-8s%5.2lf  %4.2lf ", packed_desig2, elem->abs_mag,
                           asteroid_magnitude_slope_param);
   day = (int)( decimal_day_to_dmy( elem->epoch, &year, &month, 0) + .0001);
   sprintf( buff + 20, "%c%02ld%X%c",
                  (char)( 'A' + year / 100L - 10),
                  year % 100L, month,
                  (day < 10 ? '0' + day : 'A' + day - 10));
   sprintf( buff + 25, "%10.5lf%11.5lf%11.5lf%11.5lf%11.7lf",
           centralize_ang( elem->mean_anomaly) * 180. / PI,
           centralize_ang( elem->arg_per) * 180. / PI,
           centralize_ang( elem->asc_node) * 180. / PI,
           centralize_ang( elem->incl) * 180. / PI,
           elem->ecc);
   sprintf( buff + 79, "%12.8lf%12.7lf",
            (180 / PI) / elem->t0,        /* n */
            elem->major_axis);
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         n_included_obs++;
   day = (int)( decimal_day_to_dmy( jan_1970 + (double)time( NULL) / 86400.,
                                        &year, &month, 0) + .0001);
   sprintf( buff + 103,
      "    FO %02d%02d%02d  %4d  ** ****-**** **** *** **  Find_Orb   ****",
                  (int)( year % 100), month, (int)day, n_included_obs);
   get_first_and_last_included_obs( obs, n_obs, &first_idx, &last_idx);
   arc_length = obs[last_idx].jd - obs[first_idx].jd;
   if( arc_length < .1)
      sprintf( buff + 127, "%4d min ", (int)( arc_length * 1440.));
   else if( arc_length < 2.)
      sprintf( buff + 127, "%4.1lf hrs ", arc_length * 24.);
   else if( arc_length < 600.)
      sprintf( buff + 127, "%4d days", (int)arc_length + 1);
   else
      sprintf( buff + 127, "%4d-%4d",
               (int)( 2000. + (obs[first_idx].jd         - 2451545.0) / 365.25),
               (int)( 2000. + (obs[last_idx ].jd - 2451545.0) / 365.25));
   buff[136] = ' ';
   sprintf( buff + 165, " %-30s", full_desig);
   day = (int)( decimal_day_to_dmy( obs[last_idx].jd, &year, &month, 0) + .0001);
   sprintf( buff + 194, "%04ld%02d%02d", year, month, day);
   if( rms_err < 9.9)
      sprintf( buff + 137, "%4.2lf", rms_err);
   else if( rms_err < 99.9)
      sprintf( buff + 137, "%4.1lf", rms_err);
   else if( rms_err < 9999.)
      sprintf( buff + 137, "%4.0lf", rms_err);
   buff[141] = ' ';
   return( 0);
}

int elements_in_guide_format( char *buff, const ELEMENTS *elem,
                     const char *obj_name)
{
   int month;
   double day;
   long year;

   day = decimal_day_to_dmy( elem->epoch, &year, &month, 0);
            /*      name day  mon yr MA      q      e */
   sprintf( buff, "%-43s%7.4lf%4d%5ld%10.5lf%14.7lf%12.7lf%11.6lf%12.6lf%12.6lf",
            obj_name, day, month, year,
            centralize_ang( elem->mean_anomaly) * 180. / PI,
            elem->q, elem->ecc,
            centralize_ang( elem->incl) * 180. / PI,
            centralize_ang( elem->arg_per) * 180. / PI,
            centralize_ang( elem->asc_node) * 180. / PI);
   if( elem->q < .01)
      {
      sprintf( buff + 71, "%12.10lf", elem->q);
      buff[71] = buff[83] = ' ';
      }
   sprintf( buff + strlen( buff), "  2000.0%7.1lf%6.2lf A",
            elem->abs_mag, elem->slope_param);
   if( elem->central_obj)
      sprintf( buff + strlen( buff), "  Center: %d", elem->central_obj);
   return( 0);
}

static int is_cometary( const char *constraints)
{
   const char *ecc = strstr( constraints, "e=1");

   return( ecc && atof( ecc + 2) == 1.);
}

                   /* 'magic' number;  the CRC polynomial */
#define FM 0x4c11db7

static void fill_crc_table( uint32_t *tbl, const uint32_t polynomial)
{
   unsigned i, bit;
   uint32_t tblval;

   for( i = 0; i < 256; i++)
      {
      tblval = (uint32_t)i << 24;
      for( bit = 8; bit; bit--)
         if( tblval & 0x80000000)
            tblval = (tblval << 1) ^ polynomial;
         else
            tblval <<= 1;
      *tbl++ = tblval;
      }
}

static uint32_t crc_32( const unsigned char *buff, unsigned nbytes)
{
   static uint32_t *table = NULL;
   uint32_t rval;
   unsigned n;

   if( !table)    /* first pass through,  set up the CRC table */
      {           /* table can be made static,  no problem */
      const uint32_t crc_polynomial = 0x4c11db7;

      table = (uint32_t *)malloc( 256 * sizeof( uint32_t));
      fill_crc_table( table, crc_polynomial);
      }
   for( rval = 0xffffffff; nbytes; nbytes--)
      {
      n = ((unsigned)(rval >> 24) & 0xff) ^ *buff++;
      rval = (rval << 8) ^ table[n];
      }
   return( ~rval);
}

uint32_t compute_orbit_crc( const double curr_epoch, const double epoch_shown,
            OBSERVE FAR *obs, const int n_obs)
{
   uint32_t rval;
   double buff[8];
   int i;

   buff[0] = curr_epoch;
   buff[1] = epoch_shown;
   rval = crc_32( (const unsigned char *)buff, 2 * sizeof( double));
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         buff[0] = obs[i].jd;
         buff[1] = obs[i].obs_posn[0];
         buff[2] = obs[i].obs_posn[1];
         buff[3] = obs[i].obs_posn[2];
         buff[4] = obs[i].weight;
         buff[5] = obs[i].obs_mag;
         rval ^= crc_32( (const unsigned char *)buff, 6 * sizeof( double));
         }
   return( rval);
}


int monte_carlo_object_count = 0;
int n_monte_carlo_impactors = 0;
int append_elements_to_element_file = 0;
char orbit_summary_text[80];

#define SRP1AU 2.3e-7
   /* "Solar radiation pressure at 1 AU",  in kg*AU^3 / (m^2*d^2) */
   /* from a private communication from Steve Chesley             */

/* The results from write_out_elements_to_file() can be somewhat
varied.  The output for elliptical and parabolic/hyperbolic orbits are
very different.  Asteroids and comets differ in whether H and G are
given,  or M(N)/M(T) and K.  Or those fields can be blank if no
magnitude data is given.

   Constraints or Monte Carlo data can modify the perihelion line,  such as

   Perihelion 1998 Mar 16.601688 TT;  Constraint: a=2.5
   Perihelion 1998 Mar 16.601688 TT;  20.3% impact (203/1000)

   AMR data appears on the epoch line:

Epoch 1997 Oct 13.0 TT; AMR 0.034 m^2/kg

   MOIDs can carry on to next line,  wiping out P Q header and even
the (2000.0) text if there are enough extra MOIDs.

   Examples:

Orbital elements:
1996 XX1
   Perihelion 1998 Mar 8.969329 TT = 23:15:50 (JD 2450881.469329)
Epoch 1997 Oct 13.0 TT = JDT 2450734.5   Earth MOID: 0.0615   Ma: 0.0049
M 322.34260              (2000.0)            P               Q
n   0.25622619     Peri.   72.47318     -0.50277681     -0.86441429
a   2.45501241     Node    47.71084      0.79213697     -0.46159019
e   0.5741560      Incl.    0.14296      0.34602670     -0.19930484
P   3.85           H   15.8     G   0.15   q 1.04545221  Q 3.86457261
From 13 observations 1997 Oct. 12-22;   RMS error 0.485 arcseconds


Orbital elements:
1997 ZZ99
   Perilune 1997 Apr 22.543629 TT = 13:02:49 (JD 2450561.043629)
Epoch 1997 Apr 22.5 TT = JDT 2450561.0                  Find_Orb
q 24606.5028km           (2000.0)            P               Q
H   22.9  G 0.15   Peri.  111.16531      0.57204494     -0.81965341
                   Node   193.85513     -0.79189676     -0.54220560
e 659.1509995      Incl.    7.32769     -0.21369156     -0.18488202
From 35 observations 1997 Apr. 21-22;   RMS error 1.128 arcseconds
*/

int write_out_elements_to_file( const double *orbit,
            const double curr_epoch,
            const double epoch_shown,
            OBSERVE FAR *obs, const int n_obs, const char *constraints,
            const int precision, const int monte_carlo,
            const int heliocentric_only)
{
   static const double jan_1970 = 2440587.5;
   const char *file_permits = (append_elements_to_element_file ? "a" : "w");
   extern const char *elements_filename;
   extern double planet_mass[];
   FILE *ofile = fopen( elements_filename, file_permits);
   double rel_orbit[6], orbit2[6];
   int planet_orbiting, n_lines, i, bad_elements;
   ELEMENTS elem;
   char *tptr, *tbuff = (char *)malloc( 80 * 9);
   char object_name[80], buff[100], more_moids[80];
   char impact_buff[80];
   int n_more_moids = 0;
   int output_format = (precision | SHOWELEM_PERIH_TIME_MASK);
   extern int n_extra_params, perturbers;
   double jd;
   double moids[9];

   if( default_comet_magnitude_type == 'N')
      output_format |= SHOWELEM_COMET_MAGS_NUCLEAR;
   fprintf( ofile, "Orbital elements:\n");
   memcpy( orbit2, orbit, 6 * sizeof( double));
   integrate_orbit( orbit2, curr_epoch, epoch_shown);
   planet_orbiting = find_best_fit_planet( epoch_shown, orbit2, rel_orbit);
   if( heliocentric_only)
      {
      planet_orbiting = 0;       /* insist on heliocentric display */
      memcpy( rel_orbit, orbit2, 6 * sizeof( double));
      }
// if( planet_orbiting == 3 && !monte_carlo)
   if( planet_orbiting == 3)
      {
      const double obliq_2000 = 23.4392911 * PI / 180.;

                           /* Cvt ecliptic to equatorial: */
      rotate_vector( rel_orbit, obliq_2000, 0);
      rotate_vector( rel_orbit + 3, obliq_2000, 0);
      }
   if( monte_carlo)
      {
      static uint32_t crc = 0;
      uint32_t new_crc = compute_orbit_crc( curr_epoch, epoch_shown,
                                    obs, n_obs);

      if( new_crc != crc)     /* gotta reset the Monte Carlo orbits */
         n_monte_carlo_impactors = monte_carlo_object_count = 0;
      crc = new_crc;
      }

   calc_classical_elements( &elem, rel_orbit, epoch_shown, 1,
                                    SOLAR_GM * planet_mass[planet_orbiting]);
   if( elem.ecc < .9)
      sprintf( orbit_summary_text, "a=%.3lf, ", elem.major_axis);
   else
      sprintf( orbit_summary_text, "q=%.3lf, ", elem.q);
   sprintf( orbit_summary_text + strlen( orbit_summary_text),
            "e=%.3lf, i=%d", elem.ecc, (int)( elem.incl * 180. / PI + .5));
   elem.central_obj = planet_orbiting;
   elem.epoch = epoch_shown;
   elem.abs_mag = calc_absolute_magnitude( obs, n_obs);
   elem.is_asteroid = !obs->is_comet;
   elem.slope_param = (elem.is_asteroid ? asteroid_magnitude_slope_param
                                        : comet_magnitude_slope_param);
   get_object_name( object_name, obs->packed_id);
   n_lines = elements_in_mpc_format( tbuff, &elem, object_name,
               is_cometary( constraints) && fabs( elem.ecc - 1.) < 1.e-8,
               output_format);
   tptr = tbuff;
   *more_moids = '\0';
   for( i = 0; i < 9; i++)
      moids[i] = 0.;
   for( i = 0; *tptr && i < n_lines; i++)
      {
      char *tt_ptr;
      extern double solar_pressure[];

      strcpy( buff, tptr);
      tt_ptr = strstr( buff, "TT") + 2;
      if( i == 1)    /* line with 'Perihelion = ...' */
         {
         if( *constraints)
            sprintf( tt_ptr, ";  Constraint: %s", constraints);
         else if( n_extra_params == 2)
            sprintf( tt_ptr, "; A1=%lf, A2=%lf",
                                   solar_pressure[0], solar_pressure[1]);
         else if( n_monte_carlo_impactors && monte_carlo)
            sprintf( tt_ptr, ";  %.2lf%% impact (%d/%d)",
                100. * (double)n_monte_carlo_impactors /
                       (double)monte_carlo_object_count,
                       n_monte_carlo_impactors, monte_carlo_object_count);
         }

      if( i == 2)          /* line with 'Epoch...' */
         {
         int j;

         if( n_extra_params == 1)
            sprintf( tt_ptr, "; AMR %.5lg m^2/kg",
                                 solar_pressure[0] * SOLAR_GM / SRP1AU);
         else if( !planet_orbiting)
            for( j = 0; n_more_moids < 5 && j < 8; j++)
               {
               static const char moid_idx[8] = { 3, 5, 2, 1, 4, 6, 7, 8 };
               double moid;
               ELEMENTS planet_elem;

               setup_planet_elem( &planet_elem, moid_idx[j],
                                (epoch_shown - J2000) / 36525.);
               moid = find_moid( &elem, &planet_elem);
               moids[(int)moid_idx[j]] = moid;
               if( (j < 2 && moid < 1.) || (j > 4 && moid < 1.)
                           || moid < .1)
                  {
                  char addendum[30];
                  static const char *moid_text[8] = { "Earth MOID", "Ju",
                           "Ve", "Me", "Ma", "Sa", "Ur", "Ne" };

                  sprintf( addendum, "   %s: %.4lf", moid_text[j], moid);
                  if( strlen( addendum) + strlen( buff) < 79)
                     strcat( buff, addendum);
                  else
                     {
                     n_more_moids++;
                     strcat( more_moids, addendum);
                     }
                  if( !j && moid < .1)
                      sprintf( orbit_summary_text + strlen( orbit_summary_text),
                         " MOID %.3lf", moid);
                  }
            }
         if( strlen( buff) < 56)
            {
            const char *reference = get_environment_ptr( "REFERENCE");

            if( !*reference)
               {
               reference = "Find_Orb";
               set_environment_ptr( "REFERENCE", reference);
               }
            for( j = strlen( buff); j < 56; j++)
               buff[j] = ' ';
            strcpy( buff + 56, reference);
            }
         }
      if( i == 3 && *more_moids)
         {
         int output_location = 38;

         if( n_more_moids == 4)
            output_location = 25;
         if( n_more_moids == 5)
            output_location = 12;
         strcpy( buff + output_location, more_moids);
         }
      fprintf( ofile, "%s\n", buff);
      tptr += strlen( tptr) + 1;
      }
   observation_summary_data( tbuff, obs, n_obs);
   fprintf( ofile, "%s\n", tbuff);
   if( elem.central_obj == 3 && elem.ecc < .99)
      {
      write_tle_from_vector( tbuff, rel_orbit, elem.epoch, NULL, NULL);
      fprintf( ofile, "%s", tbuff);
      }
   fprintf( ofile, "# State vector:\n# %17.12lf%17.12lf%17.12lf AU\n",
            orbit[0], orbit[1], orbit[2]);
   fprintf( ofile, "# %17.12lf%17.12lf%17.12lf mAU/day\n",
            orbit[3] * 1000., orbit[4] * 1000., orbit[5] * 1000.);
   if( !planet_orbiting)
      {
      fprintf( ofile, "# MOIDs: Me%8.4lf Ve%8.4lf Ea%8.4lf Ma%8.4lf\n",
               moids[1], moids[2], moids[3], moids[4]);
      fprintf( ofile, "# MOIDs: Ju%8.4lf Sa%8.4lf Ur%8.4lf Ne%8.4lf\n",
               moids[5], moids[6], moids[7], moids[8]);
      }
   jd = jan_1970 + time( NULL) / 86400.;
   full_ctime( buff, jd, 0);
   fprintf( ofile, "# Elements written: %s (JD %lf)\n", buff, jd);
   fprintf( ofile, "# Find_Orb ver: %s %s\n", __DATE__, __TIME__);
   fprintf( ofile, "# Perturbers: %08lx ", (unsigned long)perturbers);
   if( !perturbers)
      fprintf( ofile, "(unperturbed orbit)\n");
   else if( (perturbers & 0x3fe) == 0x3fe)
      fprintf( ofile, (perturbers & 0x400) ? "(Merc-Pluto plus Luna)\n" :
               "(Merc-Pluto, Earth & moon combined)\n");
   else
      fprintf( ofile, "\n");
   if( !elem.central_obj && elem.ecc != 1.)
      for( i = 0; i < 3; i++)           /* show Tisserand data for Jup & Nep */
         {
         const double semimajor_axes[3] = { 1., 5.2033, 30.069 };
         const char *names[3] = { "Earth", "Jupiter", "Neptune" };
         const double ratio =  semimajor_axes[i] / elem.major_axis;
         const double tisserand = ratio
            + 2. * sqrt( (1. - elem.ecc * elem.ecc) / ratio) * cos( elem.incl);

         fprintf( ofile, "# Tisserand relative to %s: %.5lf\n",
                  names[i], tisserand);
         }

   *impact_buff = '\0';
   if( elem.central_obj < 15)
      {
      extern double planet_radius[];

      if( elem.q < planet_radius[elem.central_obj] / AU_IN_KM)
         {
         double latlon[2];
         const double saved_mean_anomaly = elem.mean_anomaly;
         const double t0 = find_collision_time( &elem, latlon);

         elem.mean_anomaly = saved_mean_anomaly;
         if( t0 < 0.)      /* t0 = 0 -> it was a miss after all */
            {
            char *end_ptr;
            const double lon = latlon[0] * 180. / PI;
            const double impact_time_td = elem.perih_time + t0;
            const double impact_time_utc = impact_time_td -
                           td_minus_utc( impact_time_td) / 86400.;

            full_ctime( buff, impact_time_utc, FULL_CTIME_HUNDREDTH_SEC);
            sprintf( impact_buff, " %s lat %+9.5lf lon ", buff,
                  latlon[1] * 180. / PI);
            end_ptr = impact_buff + strlen( impact_buff);
                        /* 0 < longitude < 360;  for Earth,  show this in */
                        /* "conventional" East/West 0-180 degree format:  */
            if( elem.central_obj == 3)
               {
               sprintf( end_ptr, "%c%.5lf",
                     (lon < 180. ? 'E' : 'W'),
                     (lon < 180. ? lon : 360. - lon));
               fprintf( ofile, "IMPACT at %s\n", impact_buff);
               }
                        /* Then show in 0-360 format,  for all other  */
                        /* planets, and for output to file:           */
            sprintf( end_ptr, "%9.5lf", lon);
            if( elem.central_obj != 3)
               fprintf( ofile, "IMPACT at %s\n", impact_buff);
            }
         }
      }
   fclose( ofile);
         /* Return value indicates probable trouble if the eccentricity      */
         /* is greater than 1.2 for an heliocentric orbit.  If that happens, */
         /* the orbital elements ought to be shown in,  say,  flashing red.  */
   bad_elements = ( elem.ecc < 1.2 || elem.central_obj ? 0 : -1);
   if( elem.q > 90.)
      bad_elements |= 2;

         /* Also,  write out elements in MPCORB-like format: */
   if( !elem.central_obj)
      {
      elements_in_mpcorb_format( tbuff, obs->packed_id, object_name,
                              &elem, obs, n_obs);
      ofile = fopen( "mpc_fmt.txt", file_permits);
      fprintf( ofile, "%s\n", tbuff);
      fclose( ofile);
      }

   if( monte_carlo)
      {
      const char *element_filename = get_environment_ptr( "MONTE_CARLO");
      char name_buff[48], virtual_full_desig[40];

      if( !*element_filename)
         element_filename = "mpcorb.dat";
      monte_carlo_object_count++;
      if( *impact_buff)
         n_monte_carlo_impactors++;
      sprintf( name_buff, "%05d", monte_carlo_object_count);
      packed_desig_minus_spaces( virtual_full_desig, obs->packed_id);
      sprintf( virtual_full_desig + strlen( virtual_full_desig), " [%d]",
                                  monte_carlo_object_count);
      if( elem.central_obj)
         {
         elements_in_guide_format( tbuff, &elem, virtual_full_desig);
         ofile = fopen( "virtual.txt", "ab");
         }
      else
         {
         elements_in_mpcorb_format( tbuff, name_buff, virtual_full_desig,
                              &elem, obs, n_obs);
         ofile = fopen( element_filename, "ab");
         }
      fprintf( ofile, "%s%s\n", tbuff, impact_buff);
      fclose( ofile);
      }
   free( tbuff);
   return( bad_elements);
}

static const char *vector_data_file = "vectors.dat";

void set_solutions_found( OBJECT_INFO *ids, const int n_ids)
{
   FILE *ifile = fopen( vector_data_file, "rb");
   char buff[120];
   int i;

   for( i = 0; i < n_ids; i++)
      ids[i].solution_exists = 0;
   if( ifile)
      {
      while( fgets_trimmed( buff, sizeof( buff), ifile))
         {
         for( i = 0; i < n_ids; i++)
            if( !strcmp( buff + 11, ids[i].obj_name))
               ids[i].solution_exists = 1;
         fgets_trimmed( buff, sizeof( buff), ifile);
         fgets_trimmed( buff, sizeof( buff), ifile);
         }
      fclose( ifile);
      }
}

int fetch_previous_solution( OBSERVE *obs, const int n_obs, double *orbit,
               double *orbit_epoch, int *perturbers)
{
   FILE *ifile = fopen( vector_data_file, "rb");
   int got_vectors = 0, i;

   if( ifile)
      {
      char buff[120], object_name[80];
      double jd1 = 0., jd2 = 0.;

      get_object_name( object_name, obs->packed_id);
      while( fgets_trimmed( buff, sizeof( buff), ifile))
         if( !FMEMCMP( object_name, buff + 11, FSTRLEN( object_name)))
            if( buff[ FSTRLEN( object_name) + 11] < ' ' && *buff == ' ')
               {
               extern int n_extra_params;
               double unused_step_size;
               extern double solar_pressure[];

               for( i = 0; i < 3; i++)
                  solar_pressure[i] = 0.;
               got_vectors = 1;
               *orbit_epoch = atof( buff);
               *perturbers = 0;
               fgets_trimmed( buff, sizeof( buff), ifile);
               sscanf( buff, "%lf%lf%lf%x%lf %lf %lf",
                             &orbit[0], &orbit[1], &orbit[2], perturbers,
                             solar_pressure,
                             solar_pressure + 1,
                             solar_pressure + 2);
               n_extra_params = 0;
               if( solar_pressure[2])
                  n_extra_params = 3;
               else if( solar_pressure[1])
                  n_extra_params = 2;
               else if( solar_pressure[0])
                  n_extra_params = 1;
               fgets_trimmed( buff, sizeof( buff), ifile);
               sscanf( buff, "%lf%lf%lf%lf%lf%lf",
                             orbit + 3, orbit + 4, orbit + 5,
                             &unused_step_size, &jd1, &jd2);
               for( i = 3; i < 6; i++)
                  orbit[i] *= .001;
               for( i = 0; i < n_obs; i++)
                  {
                  obs[i].computed_ra  = obs[i].ra;
                  obs[i].computed_dec = obs[i].dec;
                  }
               }
      if( got_vectors)
         {
         set_locs( orbit, *orbit_epoch, obs, n_obs);
         if( jd2)
            for( i = 0; i < n_obs; i++)
               if( obs[i].jd < jd1 - .00001 || obs[i].jd > jd2 + .00001)
                  obs[i].is_included = 0;
         }
      fclose( ifile);
      }
   if( !got_vectors)
      {
      perturbers = 0;
      *orbit_epoch = initial_orbit( obs, n_obs, orbit);
      }
   return( got_vectors);
}

int store_solution( const OBSERVE *obs, const int n_obs, const double *orbit,
       const double orbit_epoch, const int perturbers)
{
   FILE *ofile = fopen( vector_data_file, "ab");

   if( ofile)
      {
      char buff[80];
      int i, j;

      get_object_name( buff, obs->packed_id);
      fprintf( ofile, "%10.1lf %s\n", orbit_epoch, buff);
      for( i = 0; i < 3; i++)
         fprintf( ofile, "%17.12lf", orbit[i]);
      if( perturbers)
         {
         extern int n_extra_params;

         fprintf( ofile, " %04x", perturbers);
         if( n_extra_params)
            {
            extern double solar_pressure[];

            fprintf( ofile, " %.5lg", solar_pressure[0]);
            for( i = 1; i < n_extra_params; i++)
               fprintf( ofile, "%.3lf", solar_pressure[i]);
            }
         }
      get_first_and_last_included_obs( obs, n_obs, &i, &j);
      fprintf( ofile, "\n%17.12lf%17.12lf%17.12lf %.3lf %.5lf %.5lf\n",
              orbit[3] * 1000., orbit[4] * 1000., orbit[5] * 1000.,
              0., obs[i].jd, obs[j].jd);
      fclose( ofile);
      }
   return( ofile ? 0 : -1);
}


#define LOG_10 2.302585

double calc_obs_magnitude( const int is_comet, const double obj_sun,
                      const double obj_earth, const double earth_sun)
{
   double rval;

   if( is_comet)
      rval = comet_magnitude_slope_param * log( obj_sun);
   else
      {
      double phase_ang;
      double phi1, phi2, log_tan_half_phase;

      phase_ang = obj_sun * obj_sun +
                     obj_earth * obj_earth - earth_sun * earth_sun;
      phase_ang /= 2. * obj_earth * obj_sun;
      if( phase_ang > .99999) phase_ang = .99999;
      if( phase_ang <-.99999) phase_ang = -.99999;
      phase_ang = acos( phase_ang);
      log_tan_half_phase = log( sin( phase_ang / 2.) / cos( phase_ang / 2.));
      phi1 = exp( -3.33 * exp( log_tan_half_phase * 0.63));
      phi2 = exp( -1.87 * exp( log_tan_half_phase * 1.22));
      rval = 5. * log( obj_sun) - 2.5 *
                  log( (1. - asteroid_magnitude_slope_param) * phi1
                + asteroid_magnitude_slope_param * phi2);
      }
   rval += 5. * log( obj_earth);
   rval /= LOG_10;         /* allow for common logs,  not naturals */
   return( rval);
}

/* The following function,  as the comment indicates,  assumes that a */
/* "no band" case (obs->mag_band == ' ') must be an R mag.  That's    */
/* probably the best guess for most modern,  unfiltered CCD           */
/* observations.  MPC assumes a B (photographic) magnitude,  which is */
/* probably the best guess for older observations.  I suppose one would */
/* ideally look at the second 'note'  which is C for CCD observations   */
/* and P for photographic observations.  The code could then assume a   */
/* default of R for CCD obs,  B for photographic,  and V for the admittedly */
/* rare micrometer or encoder-based observations.           */
/* http://www.cfa.harvard.edu/iau/info/OpticalObs.html         */

double calc_absolute_magnitude( OBSERVE FAR *obs, int n_obs)
{
   int i, obs_no;
   double n_mags = 0.;
   double rval = 0.;

   for( obs_no = 0; obs_no < n_obs; obs_no++)
      {
      obs->computed_mag = 0.;
      if( obs->r && obs->solar_r)
         {
         double earth_sun = 0.;

         for( i = 0; i < 3; i++)
            earth_sun += obs->obs_posn[i] * obs->obs_posn[i];
         earth_sun = sqrt( earth_sun);
         if( earth_sun)
            {
            double mag_band_shift = 0., weight = 1.;

            if( obs->mag_band == 'R')    /* V-R=+0.3 */
               mag_band_shift = .3;
            if( obs->mag_band == ' ')    /* assume "no band" = "R" */
               mag_band_shift = .3;
            if( obs->mag_band == 'B')    /* B-V=-0.8 */
               mag_band_shift = -.8;
            if( obs->mag_precision == -1)    /* integer magnitude */
               weight = .1;
            if( obs->mag_precision == 2)  /* mag to .01;  assume it's good */
               weight = 5.;
            if( obs->is_comet && obs->mag_band != default_comet_magnitude_type)
               weight = 0.;
            if( !obs->obs_mag || !obs->is_included)
               weight = 0.;
            obs->computed_mag = calc_obs_magnitude( obs->is_comet,
                         obs->solar_r, obs->r, earth_sun) - mag_band_shift;
            rval += weight * (obs->obs_mag - obs->computed_mag);
            n_mags += weight;
            }
         }
      obs++;
      }
   if( n_mags)
      rval /= n_mags;
   obs -= n_obs;
   for( obs_no = 0; obs_no < n_obs; obs_no++, obs++)
      if( n_mags)
         obs->computed_mag += rval;
      else
         obs->computed_mag = 0.;
   return( rval);
}

int find_worst_observation( const OBSERVE FAR *obs, const int n_obs)
{
   int i, rval = -1;
   double worst_rms = 0., rms;

   for( i = 0; i < n_obs; i++, obs++)
      if( obs->is_included)
         {
         rms = compute_rms( obs, 1, 1);
         if( rms > worst_rms)
            {
            worst_rms = rms;
            rval = i;
            }
         }
   return( rval);
}

/* If you've got n_obs observations stored in the obs array,  the
   get_idx1_and_idx2( ) function will puzzle through them to find the first
   and last valid observation (those that haven't had their 'is_included'
   flags set to FALSE),  and will store the indices to them in *idx1 and
   *idx2.  These are shown near the top of the display,  and are used in
   the method of Herget.  Return value is the number of included obs.   */

int get_idx1_and_idx2( const int n_obs, const OBSERVE FAR *obs,
                                          int *idx1, int *idx2)
{
   int i, rval = 0;

   for( i = 0; i < n_obs && (!obs[i].is_included || !obs[i].r); i++)
      ;
   if( i == n_obs)
      *idx1 = *idx2 = 0;
   else
      {
      *idx1 = i;
      for( ; i < n_obs; i++)
         if( obs[i].is_included && obs[i].r)
            rval++;
      for( i = n_obs - 1; i && (!obs[i].is_included || !obs[i].r); i--)
         ;
      *idx2 = i;
      }
   return( rval);
}

int get_r1_and_r2( const int n_obs, const OBSERVE FAR *obs,
                           double *r1, double *r2)
{
   int idx1, idx2, rval = get_idx1_and_idx2( n_obs, obs, &idx1, &idx2);

   if( !rval)
      *r1 = *r2 = 0.;
   else
      {
      *r1 = obs[idx1].r;
      *r2 = obs[idx2].r;
      }
   return( rval);
}

static const char *defaults = "DEFAULTS";

int store_defaults( const int ephemeris_output_options)
{
   char buff[50];

   sprintf( buff, "%c%x", default_comet_magnitude_type,
                                        ephemeris_output_options);
   set_environment_ptr( defaults, buff);
   return( 0);
}

int get_defaults( int *ephemeris_output_options)
{
   const char *def_values = get_environment_ptr( defaults);

   *ephemeris_output_options = 0;
   sscanf( def_values, "%c%x", &default_comet_magnitude_type,
                               ephemeris_output_options);
   return( 0);
}

/* The following functions are used to "color" observations.  The idea
resembles that of the four-color map problem,  except in this case,
we'd like to show observations in max_n_colors,  such that adjacent
observations from different MPC codes show up in different colors.
You can't always do this.  For example,  with observations from eight
observatories,  mixed up so that each "pair" occurs,  you'd obviously
need eight different colors.  This code just tries a lot of possible
colorings and returns the one resulting in the fewest mismatches.

   To do this,  it uses an "annealing" sort of algorithm:  it first
sets the color for each MPC observatory at random (a value from zero
to max_n_colors - 1).  It then uses the improve_mpc_colors() to get
a better solution;  that function can make "obvious" improvements,
such as "if we change this MPC code to red,  there will be fewer
mismatches".  If the result has no mismatches,  we're home free and
stop looking for a "better" solution.  Otherwise,  we set a new set
of random colors and try to improve that... and repeat the procedure
for up to two seconds;  it's probably not worth spending much more time
on it than that.

   There are other ways to do this,  of course,  including a formal
pruned tree search among all possible color combinations.  But this
appears to work quite well,  and I thought it would result in simpler
code.  (I'm no longer so sure of that.  But I don't think I'll spend
the time to write a tree search version.)
*/

#define NO_MPC_COLOR_SET   -1

int find_mpc_color( const MPC_STATION *sdata, const char *mpc_code)
{
   int rval = NO_MPC_COLOR_SET;

   if( !mpc_code)       /* indicates 'just count colors */
      {
      rval = 0;
      while( sdata[rval].code[0])
         rval++;
      }
   else while( rval == NO_MPC_COLOR_SET && sdata->code[0])
      {
      if( mpc_code[0] == sdata->code[0] &&
             mpc_code[1] == sdata->code[1] &&
             mpc_code[2] == sdata->code[2])
         rval = sdata->color;
      sdata++;
      }
   return( rval);
}

static void set_mpc_colors_semirandomly( MPC_STATION *sdata,
               const int max_n_colors, unsigned long seed)
{
   srand( seed);
   while( sdata->code[0])
      {
      sdata->color = (char)( rand( ) % (unsigned long)max_n_colors);
      sdata++;
      }
}

/* After setting the colors at random,  we look for "simple" improvements:
for each MPC code,  we check the adjacent observations with different
MPC codes,  and see what colors they have.  We might see that (say)
there are four red neighbors,  three green,  and one blue.  In that case,
changing the color of the current MPC code to blue would result in only
one problem case,  instead of three or four.  (Ideally,  we'll find that
there are _no_ blue neighbors,  of course.)

   We keep trying this until no color changes are made.
*/

static void improve_mpc_colors( const int n_obs, const OBSERVE FAR *obs,
                   const int max_n_colors, MPC_STATION *sdata)
{
   int i, changes_made = 1, n_iterations = 0;

   while( changes_made)
      {
      changes_made = 0;
      for( i = 0; sdata[i].code[0]; i++)
         {
         int counts[20], j, color = sdata[i].color;

         assert( color >=0 && color < max_n_colors);
         for( j = 0; j < max_n_colors; j++)
            counts[j] = 0;
         for( j = 0; j < n_obs; j++)
            if( !strcmp( obs[j].mpc_code, sdata[i].code))
               {
               if( j > 0 && strcmp( obs[j - 1].mpc_code, sdata[i].code))
                  {
                  const int adjacent_color =
                          find_mpc_color( sdata, obs[j - 1].mpc_code);

                  assert( adjacent_color >=0 && adjacent_color < max_n_colors);
                  counts[adjacent_color]++;
                  }
               if( j < n_obs - 1 && strcmp( obs[j + 1].mpc_code, sdata[i].code))
                  {
                  const int adjacent_color =
                          find_mpc_color( sdata, obs[j + 1].mpc_code);

                  assert( adjacent_color >=0 && adjacent_color < max_n_colors);
                  counts[adjacent_color]++;
                  }
               }
         for( j = 0; j < max_n_colors; j++)
            if( counts[j] < counts[color])
               {
               color = j;
               sdata[i].color = (char)color;
               changes_made = 1;
               }
         assert( color >=0 && color < max_n_colors);
         }
      n_iterations++;
      assert( n_iterations < 10);
      }
}

extern int debug_level;
int debug_printf( const char *format, ...);                /* runge.cpp */

MPC_STATION *find_mpc_color_codes( const int n_obs, const OBSERVE FAR *obs,
                   const int max_n_colors)
{
   int n_codes = 0, i, j, n_alloced = 10;
   int best_score = 99999, best_seed = 0;
   clock_t t0;
   MPC_STATION *rval =
               (MPC_STATION *)calloc( n_alloced + 1, sizeof( MPC_STATION));

   for( i = 0; i < n_obs; i++)
      if( find_mpc_color( rval, obs[i].mpc_code) == NO_MPC_COLOR_SET)
         {
         int loc = 0;

         if( n_codes == n_alloced)
            {
            const int new_size = n_alloced * 2;
            MPC_STATION *new_array =
                   (MPC_STATION *)calloc( new_size + 1, sizeof( MPC_STATION));

            memcpy( new_array, rval, n_alloced * sizeof( MPC_STATION));
            n_alloced = new_size;
            free( rval);
            rval = new_array;
            }
         for( loc = 0; loc < n_codes
              && strcmp( rval[loc].code, obs[i].mpc_code) < 0; loc++)
            ;
                     /* move the rest of the array forward... */
         memmove( rval + loc + 1, rval + loc,
                          (n_codes - loc) * sizeof( MPC_STATION));
                     /* ...so we can copy in the new code: */
         strcpy( rval[loc].code, obs[i].mpc_code);
         n_codes++;
         }
   if( debug_level)
      {
      debug_printf( "%d obs, %d codes\n", n_obs, n_codes);
      for( i = 0; i < n_codes; i++)
         debug_printf( "%d: '%s'\n", i, rval[i].code);
      }
   t0 = clock( );
   for( i = 1; best_score && clock( ) < t0 + 2 * CLOCKS_PER_SEC; i++)
      {
      int score = 0;

      set_mpc_colors_semirandomly( rval, max_n_colors, (unsigned long)i);
      improve_mpc_colors( n_obs, obs, max_n_colors, rval);
      for( j = 0; j < n_obs - 1; j++)
         if( strcmp( obs[j].mpc_code, obs[j + 1].mpc_code))
            if( find_mpc_color( rval, obs[j].mpc_code) ==
               find_mpc_color( rval, obs[j + 1].mpc_code))
                  score++;
      if( score < best_score)   /* "lower" is "better" */
         {
         best_score = score;
         best_seed = i;
         }

      if( debug_level > 1 && (i < 10 || !(i % 100)))
          debug_printf( "Seed: %d, score %d, best %d\n", i, score, best_score);
      }
   if( debug_level)
      debug_printf( "Color setting: best score %d, i = %d\n", best_score, i);
   set_mpc_colors_semirandomly( rval, max_n_colors, (unsigned long)best_seed);
   improve_mpc_colors( n_obs, obs, max_n_colors, rval);
   return( rval);
}
