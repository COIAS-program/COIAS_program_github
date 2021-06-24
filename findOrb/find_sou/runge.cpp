#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>
#ifndef __GNUC__
#include <conio.h>
#include <io.h>
#else
#include <unistd.h>
#endif
#include "watdefs.h"
#include "lunar.h"
#include "afuncs.h"
#include "mpc_obs.h"
#include "comets.h"

#define PI 3.14159265358979323
#define N_PERTURB 22
#define J2000 2451545.
#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)
#define AU_PER_JRAD ((44382. * 1.609) / 149.6e+6)
#define EARTH_MOON_RATIO 81.30056
#define UNINITIALIZED_J2_MULTIPLIER 999.314159265358

extern int perturbers;
double j2_multiplier = UNINITIALIZED_J2_MULTIPLIER;

void equatorial_to_ecliptic( double FAR *vect);       /* mpc_obs.cpp */
int planet_posn( const int planet_no, const double jd, double *vect_2000);
                                                /* mpc_obs.cpp */
int earth_lunar_posn( const double jd, double FAR *earth_loc, double FAR *lunar_loc);
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
int debug_printf( const char *format, ...);                /* runge.cpp */
int get_asteroid_perturber_elems( ELEMENTS *elem,             /* get_pert.cpp */
                  const double jd, const int perturber_no);
double vector3_length( const double *vect);                 /* ephem0.cpp */
double take_rk_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step);      /* runge.cpp */
double take_pd89_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step);      /* runge.cpp */
int symplectic_6( double jd, ELEMENTS *ref_orbit, double *vect,
                                          const double dt);
static int get_planet_posn_vel( const double jd, const int planet_no,
                     double *posn, double *vel);         /* runge.cpp */

int debug_printf( const char *format, ...)
{
   va_list argptr;
   FILE *ofile = fopen( "debug.txt", "a");

   va_start( argptr, format);
   vfprintf( ofile, format, argptr);
   va_end( argptr);
   fclose( ofile);
   return( 0);
}

      /* The following value for various J2s come from the _Explanatory  */
      /* Supplement_,  p 697.  They're in units of planetary radii,  and */
      /* must be converted to AU squared. */

#define J2_IN_EARTH_UNITS (1.08263e-3)
#define J3_IN_EARTH_UNITS (-2.54e-6)
#define J4_IN_EARTH_UNITS (-1.61e-6)
#define EARTH_R (6378.140 / AU_IN_KM)
#define EARTH_R2 (EARTH_R * EARTH_R)
#define EARTH_J2 (J2_IN_EARTH_UNITS * EARTH_R2)
#define EARTH_J3 (J3_IN_EARTH_UNITS * EARTH_R2 * EARTH_R)
#define EARTH_J4 (J4_IN_EARTH_UNITS * EARTH_R2 * EARTH_R2)

#define J2_IN_MARS_UNITS (1.964e-3)
#define MARS_R (3397.2 / AU_IN_KM)
#define MARS_J2 (J2_IN_MARS_UNITS*MARS_R * MARS_R)
#define MARS_J3 0.
#define MARS_J4 0.

/* 12 Feb 2009:  updated all the following gas giant J2/3/4 data using */
/* data from http://ssd.jpl.nasa.gov/?gravity_fields_op */

#define J2_IN_JUPITER_UNITS (.01469643)
#define J3_IN_JUPITER_UNITS (-6.4e-7)
#define J4_IN_JUPITER_UNITS (-5.8714e-4)
#define JUPITER_R (71492. / AU_IN_KM)
#define JUPITER_R2 (JUPITER_R * JUPITER_R)
#define JUPITER_J2 (J2_IN_JUPITER_UNITS * JUPITER_R2)
#define JUPITER_J3 (J3_IN_JUPITER_UNITS * JUPITER_R2 * JUPITER_R)
#define JUPITER_J4 (J4_IN_JUPITER_UNITS * JUPITER_R2 * JUPITER_R2)

#define J2_IN_SATURN_UNITS (.01629071)
#define J4_IN_SATURN_UNITS (-.00093583)
#define SATURN_R (60330. / AU_IN_KM)
#define SATURN_R2 (SATURN_R * SATURN_R)
#define SATURN_J2 (J2_IN_SATURN_UNITS * SATURN_R2)
#define SATURN_J3 0.
#define SATURN_J4 (J4_IN_SATURN_UNITS * SATURN_R2 * SATURN_R2)

#define J2_IN_URANUS_UNITS (.00334129)
#define J4_IN_URANUS_UNITS (-3.044e-5)
#define URANUS_R (26200. / AU_IN_KM)
#define URANUS_R2 (URANUS_R * URANUS_R)
#define URANUS_J2 (J2_IN_URANUS_UNITS * URANUS_R * URANUS_R)
#define URANUS_J3 0.
#define URANUS_J4 (J4_IN_URANUS_UNITS * URANUS_R2 * URANUS_R2)

#define J2_IN_NEPTUNE_UNITS (.00340849)
#define J4_IN_NEPTUNE_UNITS (-3.348e-5)
#define NEPTUNE_R (25225. / AU_IN_KM)
#define NEPTUNE_R2 (NEPTUNE_R * NEPTUNE_R)
#define NEPTUNE_J2 (J2_IN_NEPTUNE_UNITS * NEPTUNE_R * NEPTUNE_R)
#define NEPTUNE_J3 0.
#define NEPTUNE_J4 (J4_IN_NEPTUNE_UNITS * NEPTUNE_R2 * NEPTUNE_R2)

double jn_potential( const double *loc, const double j2, const double j3,
                                        const double j4)
{
   const double r2 = loc[0] * loc[0] + loc[1] * loc[1] + loc[2] * loc[2];
   const double r = sqrt( r2);
   const double mu = loc[2] / r;
   const double mu2 = mu * mu;
   const double p2 = 1.5 * mu2 - .5;     /* Danby, p. 115 */
   const double p3 = mu * (2.5 * mu2 - 1.5);
   const double p4 = (35. * mu2 * mu2 - 30. * mu2 + 3.) / 8.;

   return( (j2 * p2 + j3 * p3 / r + j4 * p4 / r2) / (r * r2));
}

#ifndef PREVIOUS_J2_METHOD
void analytical_j2_gradient( double *grad, const double x,
                           const double y, const double z)
{
   const double r2 = x * x + y * y + z * z;
   const double r7 = r2 * r2 * r2 * sqrt( r2);
   const double tval = (1.5 * r2 - 7.5 * z * z) / r7;

   grad[0] = x * tval;
   grad[1] = y * tval;
   grad[2] = z * (3. * r2 / r7 + tval);
}
#endif

void numerical_gradient( double *grad, const double *loc,
                   const double j2, const double j3, const double j4)
{
   const double r2 = loc[0] * loc[0] + loc[1] * loc[1] + loc[2] * loc[2];
   const double delta = sqrt( r2) * .01;
   int i;

   for( i = 0; i < 3; i++)
      {
      double tval, tloc[3];
      int j;

      for( j = 0; j < 3; j++)
         tloc[j] = loc[j];
      tloc[i] += delta;
      tval = jn_potential( tloc, j2, j3, j4);
      tloc[i] -= delta + delta;
      tval -= jn_potential( tloc, j2, j3, j4);

      grad[i] = tval / (delta * 2.);
      }
}

double relativistic_factor = 1.;
int reset_of_elements_needed = 1;

   /* Somewhat artificially,  we set the relativistic effect to be zero */
   /* when an object goes inside the sun (r < radius of the sun).  This */
   /* just avoids a situation wherein the relativistic acceleration     */
   /* explodes to infinity,  and the program drags to a crawl.  Similar */
   /* trickery takes place for J2, J3, and J4 when an object runs inside */
   /* a planet. */

static void set_relativistic_accel( double *accel, const double *posnvel)
{
   int i;
   const double c = AU_PER_DAY;           /* speed of light in AU per day */
   const double r_squared = posnvel[0] * posnvel[0] + posnvel[1] * posnvel[1]
                                                    + posnvel[2] * posnvel[2];
   const double v_squared = posnvel[3] * posnvel[3] + posnvel[4] * posnvel[4]
                                                    + posnvel[5] * posnvel[5];
   const double v_dot_r   = posnvel[0] * posnvel[3] + posnvel[1] * posnvel[4]
                                                    + posnvel[2] * posnvel[5];
   const double r = sqrt( r_squared), r_cubed_c_squared = r_squared * r * c * c;
   const double r_component =
                  (4. * SOLAR_GM / r - v_squared) / r_cubed_c_squared;
   const double v_component = 4. * v_dot_r / r_cubed_c_squared;
   const double solar_radius_in_au = 696000. / AU_IN_KM;

   if( r > solar_radius_in_au)
      for( i = 0; i < 3; i++)
         accel[i] = r_component * posnvel[i] + v_component * posnvel[i + 3];
   else
      for( i = 0; i < 3; i++)
         accel[i] = 0.;
}

#define MASS_OF_SUN_IN_KILOGRAMS 1.9891E+30

#define MASS_IO               (893.3E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_EUROPA           (479.7E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_GANYMEDE         (1482E+20  / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_CALLISTO         (1076E+20  / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_GALILEANS  (MASS_IO + MASS_EUROPA + MASS_GANYMEDE + MASS_CALLISTO)
#define MASS_JUPITER_SYSTEM   0.0009547919384243268
#define MASS_JUPITER   (MASS_JUPITER_SYSTEM - MASS_GALILEANS)
#ifdef TRY_SOMETHING_ELSE
#define MASS_JUPITER          0.0009547919384243268
#define MASS_JUPITER_SYSTEM   (MASS_JUPITER + MASS_GALILEANS)
#endif

#define MASS_SATURN_SYSTEM    0.0002858859806661309
#define MASS_TETHYS            (6.22E+20  / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_DIONE             (10.52E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_RHEA              (23.12E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_TITAN            (1345.5E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_IAPETUS            (15.9E+20 / MASS_OF_SUN_IN_KILOGRAMS)
#define MASS_SATURN_SATS  (MASS_TETHYS + MASS_DIONE + MASS_RHEA + MASS_TITAN + MASS_IAPETUS)
#define MASS_SATURN          (MASS_SATURN_SYSTEM - MASS_SATURN_SATS)
#define MASS_CERES             4.7622e-10
#define MASS_PALLAS            1.0775e-10
#define MASS_VESTA             1.3412e-10


      /* 22 Oct 2001:  replaced Uranus,  Neptune masses w/DE-405 values */

double planet_mass[N_PERTURB + 1] = { 1.,                            /*  0 */
         1.660136795271931e-007,                /* mercury */        /*  1 */
         2.447838339664545e-006,                /* venus */          /*  2 */
         3.003489596331057e-006,                /* Earth */          /*  3 */
         3.227151445053866e-007,                /* Mars */           /*  4 */
         MASS_JUPITER,                          /* Jupiter */        /*  5 */
         MASS_SATURN,                           /* saturn */         /*  6 */
         4.366244043351564e-005,                /* Uranus */         /*  7 */
         5.151389020466116e-005,                /* Neptune */        /*  8 */
         7.396449704142013e-009,                /* Pluto */          /*  9 */
         3.003489596331057e-006 / EARTH_MOON_RATIO, /* Moon */       /* 10 */

         MASS_IO,                                                    /* 11 */
         MASS_EUROPA,                                                /* 12 */
         MASS_GANYMEDE,                                              /* 13 */
         MASS_CALLISTO,                                              /* 14 */

         MASS_TETHYS,                                                /* 15 */
         MASS_DIONE,                                                 /* 16 */
         MASS_RHEA,                                                  /* 17 */
         MASS_TITAN,                                                 /* 18 */
         MASS_IAPETUS,                                               /* 19 */
         MASS_CERES, MASS_PALLAS, MASS_VESTA };  /* Cere Pall Vest   20-22 */

double planetary_system_mass( const int planet_no)
{
   double rval;

   if( planet_no == 5)
      rval = MASS_JUPITER_SYSTEM;
   else if( planet_no == 6)
      rval = MASS_SATURN_SYSTEM;
   else
      rval = planet_mass[planet_no];
   return( rval);
}

      /* If we're closer than .1 AU,  include Galileans separately: */

#define GALILEAN_LIMIT .03
#define TITAN_LIMIT .03

static int excluded_perturbers = -1;
int use_cowell = -1;
int best_fit_planet;
double best_fit_planet_dist;

int calc_derivatives( const double jd, const double *ival, double *oval,
                           const int reference_planet)
{
   double r, r2 = 0., accel = 1.;
   int i, j, local_perturbers = perturbers;
   double lunar_loc[3], jupiter_loc[3], saturn_loc[3];
   double relativistic_accel[3];
   extern int n_extra_params;
   static const double sphere_of_influence_radius[10] = {
            10000., 0.00075, 0.00412, 0.00618,   /* sun, mer, ven, ear */
            0.00386, 0.32229, 0.36466, 0.34606,  /* mar, jup, sat, ura */
            0.57928, 0.02208 };                  /* nep, plu */

   oval[0] = ival[3];
   oval[1] = ival[4];
   oval[2] = ival[5];
   best_fit_planet = 0;
   for( i = 0; i < 3; i++)
      r2 += ival[i] * ival[i];
   r = sqrt( r2);
   if( n_extra_params)
      {
      extern double solar_pressure[];
      double accel_fraction = 1.;

      if( n_extra_params == 2)      /* Marsden & Sekanina comet formula */
         {
         const double r0 = 2.808, m = 2.15, n = 5.093, k = 23.5 / n;
         const double alpha = .1113;

         accel_fraction = alpha * pow( r / r0, -m);
         accel_fraction *= pow( 1. + pow( r / r0, n), -k);
         }
#ifdef FAILED_CODE_FOR_J002E3
               /* I tried to model the odd SRP behavior of J002E3 with a     */
               /* fairly simple model... apparently,  too simple;  it didn't */
               /* help the solution at all.                                  */
      if( n_extra_params == 3)
         {
         double ecliptic[3], sin_lon, cos_lon, sin_2lon, cos_2lon;

         memcpy( ecliptic, ival, 3 * sizeof( double));
         equatorial_to_ecliptic( ecliptic);       /* mpc_obs.cpp */
         sin_lon = ecliptic[0] / r;
         cos_lon = ecliptic[1] / r;
         sin_2lon = 2. * sin_lon * cos_lon;
         cos_2lon = 2. * cos_lon * cos_lon - 1.;
         accel_fraction += solar_pressure[1] * cos_2lon +
                           solar_pressure[2] * sin_2lon;
         }
#endif
      accel -= solar_pressure[0] * accel_fraction;
      }
   accel *= -SOLAR_GM / (r2 * r);

   if( j2_multiplier == UNINITIALIZED_J2_MULTIPLIER)
      {
      const char *j2_mul_str = get_environment_ptr( "J2_MULTIPLIER");

      if( *j2_mul_str)
         j2_multiplier = atof( j2_mul_str);
      else
         j2_multiplier = 1.;
      }

   if( perturbers)
      set_relativistic_accel( relativistic_accel, ival);
   else                             /* shut off relativity if no perturbers */
      for( i = 0; i < 3; i++)
         relativistic_accel[i] = 0.;

   for( i = 0; i < 3; i++)
      oval[i + 3] = accel * ival[i]
                 + SOLAR_GM * relativistic_factor * relativistic_accel[i];

   if( perturbers)
      for( i = 1; i < N_PERTURB + 1; i++)
         if( ((local_perturbers >> i) & 1)
                   && !((excluded_perturbers >> i) & 1))
            {
            double planet_loc[15], accel[3], mass_to_use = planet_mass[i];

            r = r2 = 0.;
            if( i == 20 || i == 21 || i == 22)     /* three asteroids */
               {
               ELEMENTS elem;

               if( !get_asteroid_perturber_elems( &elem, jd, i - 20))
                  comet_posn_and_vel( &elem, jd, planet_loc + 12, NULL);
               else
                  planet_loc[12] = planet_loc[13] = planet_loc[14] = 0.;
               planet_loc[2] = vector3_length( planet_loc + 12);
               }
            else if( i > 10)       /* Galileans,  Titan */
               {
               double matrix[10], sat_loc[15];
               const double t_years = (jd - J2000) / 365.25;

               if( i >= 15)         /* Saturnian satell */
                  calc_ssat_loc( jd, sat_loc, ((i == 19) ? 7 : i - 13), 0L);
               else
                  {
                  calc_jsat_loc( jd, sat_loc, 1 << (i - 11), 0L);
                  memmove( sat_loc, sat_loc + (i - 11) * 3,
                                                      3 * sizeof( double));
                  }
                                 /* turn ecliptic of date to equatorial: */
               rotate_vector( sat_loc, mean_obliquity( t_years / 100.), 0);
                                 /* then to equatorial J2000: */
               setup_precession( matrix, 2000. + t_years, 2000.);
               precess_vector( matrix, sat_loc, planet_loc + 12);
                                 /* then to ecliptic J2000: */
               equatorial_to_ecliptic( planet_loc + 12);
               for( j = 0; j < 3; j++)
                  {
                  double coord;

                  if( i >= 15)         /* Saturnian */
                     coord = saturn_loc[j] + planet_loc[12 + j];
                  else
                     coord = jupiter_loc[j] + planet_loc[12 + j] * AU_PER_JRAD;
                  r2 += coord * coord;
                  planet_loc[12 + j] = coord;
                  }
               planet_loc[2] = sqrt( r2);
               }
            else
               {
               if( local_perturbers & 1024)   /* if the moon is included */
                  {
                  if( i == 3)
                     earth_lunar_posn( jd, planet_loc, lunar_loc);
                  else if( i == 10)
                     memcpy( planet_loc, lunar_loc, 3 * sizeof( double));
                  else
                     planet_posn( i, jd, planet_loc);
                  }
               else
                  planet_posn( i, jd, planet_loc);

               for( j = 0; j < 3; j++)
                  r2 += planet_loc[j] * planet_loc[j];
               memcpy( planet_loc + 12, planet_loc, 3 * sizeof( double));
               planet_loc[2] = sqrt( r2);
               }

            for( j = 0; j < 3; j++)
               {
               accel[j] = ival[j] - planet_loc[12 + j];
               r += accel[j] * accel[j];
               }
            r = sqrt( r);

            if( i == 5)
               if( r < GALILEAN_LIMIT)
                  {
                  memcpy( jupiter_loc, planet_loc + 12, 3 * sizeof( double));
                  local_perturbers |= (15 << 11);
                  }
               else     /* "throw" Galileans into Jupiter: */
                  mass_to_use = MASS_JUPITER_SYSTEM;

            if( i == 6)
               if( r < TITAN_LIMIT)
                  {
                  memcpy( saturn_loc, planet_loc + 12, 3 * sizeof( double));
                  local_perturbers |= (31 << 15);
                  }
               else        /* "throw" saturn's satellites into the primary: */
                  mass_to_use = MASS_SATURN_SYSTEM;

            if( i >= 3 && i <= 8 && r < .015 && j2_multiplier)
               {          /* Within .015 AU,  we take J2 into account: */
               double grad[3], delta_j2000[3], matrix[10], delta_planet[3];
               const double j2[6] = { EARTH_J2, MARS_J2, JUPITER_J2,
                        SATURN_J2, URANUS_J2, NEPTUNE_J2 };
               const double j3[6] = { EARTH_J3, MARS_J3, JUPITER_J3,
                        SATURN_J3, URANUS_J3, NEPTUNE_J3 };
               const double j4[6] = { EARTH_J4, MARS_J4, JUPITER_J4,
                        SATURN_J4, URANUS_J4, NEPTUNE_J4 };
               const double radius[6] = { EARTH_R, MARS_R, JUPITER_R,
                        SATURN_R, URANUS_R, NEPTUNE_R };
               const double obliq_2000 = 23.4392911 * PI / 180.;
               double total_j_mul =
                             j2_multiplier * planet_mass[i] * SOLAR_GM;

                              /* The following evades problems for orbits  */
                              /* that end up _inside_ a planet.  Such      */
                              /* orbits can occur during the preliminary   */
                              /* determination step,  and you want to have */
                              /* the accelerations not climb to infinity.  */
                              /* You also want to evade a discontinuity    */
                              /* as the object plows through the surface:  */
               if( r < radius[i - 3])
                  {
                  const double mult = r / radius[i - 3];

                  total_j_mul *= mult * mult * mult;
                  }
                        /* Really oughta convert from TT to UT here,  but */
                        /* it won't matter unless we're including zonal   */
                        /* harmonics.  That day is far off:               */
               calc_planet_orientation( i, 0, jd, matrix);
                           /* Remembering the 'accels' are 'deltas' now... */
               memcpy( delta_j2000, accel, 3 * sizeof( double));
                           /* Cvt ecliptic to equatorial 2000...: */
               rotate_vector( delta_j2000, obliq_2000, 0);
                           /* ...then to planet-centered coords: */
               precess_vector( matrix, delta_j2000, delta_planet);

#ifdef ANALYTICAL_GRADIENT
               analytical_j2_gradient( grad, delta_planet[0],
                                       delta_planet[1], delta_planet[2]);
               for( j = 0; j < 3; j++)
                  grad[j] *= j2[i - 3];
#else
               numerical_gradient( grad, delta_planet,
                        j2[i - 3], j3[i - 3], j4[i - 3]);
//             numerical_gradient( grad, delta_planet,
//                      j2[i - 3], 0., 0.);
#endif
                           /* now convert gradient back to J2000 equatorial: */
               deprecess_vector( matrix, grad, delta_j2000);
                           /* Cvt equatorial to ecliptic: */
               rotate_vector( delta_j2000, -obliq_2000, 0);
                           /* And add 'em to the output acceleration: */
               for( j = 0; j < 3; j++)
                  oval[j + 3] -= total_j_mul * delta_j2000[j];
               }

                     /* If we're including the earth,  but the moon isn't */
                     /* being included separately,  add the mass of the moon:*/
            if( i == 3)
               if( !((local_perturbers >> 10) & 1) ||
                    ((excluded_perturbers >> 10) & 1))
                  mass_to_use += planet_mass[10];

            if( i < 10 && r < sphere_of_influence_radius[i] && !use_cowell)
               {
               best_fit_planet = i;
               best_fit_planet_dist = r;
               }

            if( r)
               {
               const double accel_factor =
                                   -SOLAR_GM * mass_to_use / (r * r * r);

               for( j = 0; j < 3; j++)
                  oval[j + 3] += accel_factor * accel[j];
               }
            if( i != reference_planet)
               {
               if( reference_planet >= 0)
                  {
                  double planet_posn[3];

                  get_planet_posn_vel( jd, reference_planet, planet_posn, NULL);
                  r = 0.;
                  for( j = 0; j < 3; j++)
                     {
                     planet_loc[j + 12] -= planet_posn[j];
                     r += planet_loc[j + 12] * planet_loc[j + 12];
                     }
                  r = sqrt( r);
                  }
               else
                  r = planet_loc[2];
               if( r)
                   r = -SOLAR_GM * mass_to_use / (r * r * r);
               for( j = 0; j < 3; j++)
                  oval[j + 3] += r * planet_loc[j + 12];
               }
            else        /* subtract sun's attraction to reference planet */
               {
               r = planet_loc[2];
               if( r)
                   r = SOLAR_GM / (r * r * r);
               for( j = 0; j < 3; j++)
                  oval[j + 3] += r * planet_loc[j + 12];
               }
            }
   return( 0);
}

static int get_planet_posn_vel( const double jd, const int planet_no,
                     double *posn, double *vel)
{
   if( posn)
      {
      if( !planet_no)       /* sun doesn't move in the heliocentric frame */
         memset( posn, 0, 3 * sizeof( double));
      else if( planet_no == 3)
         earth_lunar_posn( jd, posn, NULL);
      else if( planet_no == 10)
         earth_lunar_posn( jd, NULL, posn);
      else
         planet_posn( planet_no, jd, posn);
      }
   if( vel)
      if( !planet_no)       /* sun doesn't move in the heliocentric frame */
         memset( vel, 0, 3 * sizeof( double));
      else
         {
         int i;
         double loc1[3], loc2[3];
         const double delta = 60. / 86400.;    /* ten second delta... */

         get_planet_posn_vel( jd + delta, planet_no, loc2, NULL);
         get_planet_posn_vel( jd - delta, planet_no, loc1, NULL);
         for( i = 0; i < 3; i++)
            vel[i] = (loc2[i] - loc1[i]) / (2. * delta);
         }
   return( 0);
}

int find_relative_orbit( const double jd, const double *ivect,
               ELEMENTS *elements, double *rel_vect, const int ref_planet)
{
   double local_rel_vect[6];

   memcpy( local_rel_vect, ivect, 6 * sizeof( double));
   if( ref_planet)
      {
      double planet_state[6];
      int i;

      get_planet_posn_vel( jd, ref_planet, planet_state, planet_state + 3);
      for( i = 0; i < 6; i++)
         local_rel_vect[i] -= planet_state[i];
      }
   if( rel_vect)
      memcpy( rel_vect, local_rel_vect, 6 * sizeof( double));
   if( elements)
      {
      calc_classical_elements( elements, local_rel_vect, jd, 1,
                           SOLAR_GM * planetary_system_mass( ref_planet));
      elements->epoch = jd;
      elements->central_obj = ref_planet;
      }
   return( 0);
}

int check_for_perturbers( const double t_cen, const double *vect);

int find_best_fit_planet( const double jd, const double *ivect,
                                 double *rel_vect)
{
   int i, j, rval = 0;
   double best_fit = 0., vel[3];
   int included = 1;          /* the Sun is always included in this */
   const int possible_perturber = check_for_perturbers( (jd - J2000) / 36525.,
                                             ivect);

   included |= (1 << possible_perturber);
   if( possible_perturber == 3)
      included |= (1 << 10);
   for( i = 0; i < 11; i++)
      if( (included >> i) & 1)
         {
         double planet_loc[3], delta[3], dist2 = 0., curr_fit;

         get_planet_posn_vel( jd, i, planet_loc, NULL);
         for( j = 0; j < 3; j++)
            {
            delta[j] = ivect[j] - planet_loc[j];
            dist2 += delta[j] * delta[j];
            }

         curr_fit = planet_mass[i] / exp( log( dist2) * 1.25);
         if( !i || curr_fit > best_fit)
            {
            rval = i;
            best_fit = curr_fit;
            if( rel_vect)
               memcpy( rel_vect, delta, 3 * sizeof( double));
            }
         }

   get_planet_posn_vel( jd, rval, NULL, vel);
   if( rel_vect)
      for( j = 0; j < 3; j++)
         rel_vect[j + 3] = ivect[j + 3] - vel[j];
   return( rval);
}

   /* When solving orbits for objects orbiting very near to Jupiter and
      Saturn,  Find_Orb will default to including perturbations from the
      satellites of those planets.  That can be a problem if the object
      in question _is_ a satellite of that planet;  when computing an
      orbit for,  say,  Callisto,  you don't really want to include
      perturbations from Callisto.  Only the other three Galileans ought
      to be considered in that case.  (If you _do_ attempt to include
      "perturbations by Callisto on Callisto",  you ought to get a
      divide-by-zero error.  In practice,  you just get wacky results.)

      The following function looks at a packed designation and tells
      you which perturber it is.  It returns -1 in the (usual) case
      that you're not solving for the orbit of an inner satellite that
      also happens to be a perturbing body in Find_Orb.        */

int obj_desig_to_perturber( const char *packed_desig)
{
   int rval = -1;

                     /* The EXCLUDED environment variable provides a way */
                     /* to specifically exclude some perturbers,  either */
                     /* to speed things up or for debugging purposes.    */
   sscanf( get_environment_ptr( "EXCLUDED"), "%x", &excluded_perturbers);
   if( excluded_perturbers == -1)
      excluded_perturbers = 0;
// excluded_perturbers |= 512;      /* Pluto is _always_ excluded */

   if( !memcmp( packed_desig + 4, "S    ", 5) && packed_desig[1] == '0'
                                              && packed_desig[2] == '0')
      if( *packed_desig == 'J')
         {
         if( packed_desig[3] >= '1' && packed_desig[3] <= '4')
            rval = 11 + packed_desig[3] - '1';  /* Io..Callisto = 11..14 */
         }
      else if( *packed_desig == 'S')
         {
         if( packed_desig[3] >= '3' && packed_desig[3] <= '6')
            rval = 15 + packed_desig[3] - '3';  /* Tethys...Titan = 15..18 */
         else if( packed_desig[3] == '8')
            rval = 19;                          /* Iapetus */
         }
   if( rval > 0)
      excluded_perturbers |= (1 << rval);
   return( rval);
}

void compute_ref_state( ELEMENTS *ref_orbit, double *ref_state,
                                          const double jd)
{
   double r2 = 0., accel;
   int i;

   if( use_cowell == -1)
      use_cowell = atoi( get_environment_ptr( "COWELL"));

   if( use_cowell)
      {
      memset( ref_state, 0, 9 * sizeof( double));
      return;
      }

   comet_posn_and_vel( ref_orbit, jd, ref_state, ref_state + 3);
   for( i = 0; i < 3; i++)
      r2 += ref_state[i] * ref_state[i];
   accel = -SOLAR_GM * planetary_system_mass( ref_orbit->central_obj) / (r2 * sqrt( r2));
   for( i = 0; i < 3; i++)
      ref_state[i + 6] = accel * ref_state[i];

   if( ref_orbit->central_obj)
      {
      double planet_state[6];

      get_planet_posn_vel( jd, ref_orbit->central_obj, planet_state, planet_state + 3);
      for( i = 0; i < 6; i++)
         ref_state[i] += planet_state[i];
      }
}

#define B_2_1     .0555555555555555555555555555556
#define B_3_1     .0208333333333333333333333333333
#define B_3_2     .0625
#define B_4_1     .03125
#define B_4_2    0.
#define B_4_3     .09375
#define B_5_1     .3125
#define B_5_2    0.
#define B_5_3   -1.171875
#define B_5_4    1.171875
#define B_6_1     .0375
#define B_6_2    0.
#define B_6_3    0.
#define B_6_4     .1875
#define B_6_5     .15
#define B_7_1     .0479101371111111111111111111111
#define B_7_2    0.
#define B_7_3    0.
#define B_7_4     .112248712777777777777777777778
#define B_7_5    -.0255056737777777777777777777778
#define B_7_6     .0128468238888888888888888888889
#define B_8_1        .016917989787292281181431107136
#define B_8_2       0.
#define B_8_3       0.
#define B_8_4       .387848278486043169526545744159
#define B_8_5       .0359773698515003278967008896348
#define B_8_6       .196970214215666060156715256072
#define B_8_7      -.172713852340501838761392997002
#define B_9_1       .0690957533591923006485645489846
#define B_9_2      0.
#define B_9_3      0.
#define B_9_4      -.634247976728854151882807874972
#define B_9_5      -.161197575224604080366876923982
#define B_9_6       .138650309458825255419866950133
#define B_9_7       .94092861403575626972423968413
#define B_9_8       .211636326481943981855372117132
#define B_10_1      .183556996839045385489806023537
#define B_10_2     0.
#define B_10_3     0.
#define B_10_4    -2.46876808431559245274431575997
#define B_10_5     -.291286887816300456388002572804
#define B_10_6     -.026473020233117375688439799466
#define B_10_7     2.84783876419280044916451825422
#define B_10_8      .281387331469849792539403641827
#define B_10_9      .123744899863314657627030212664
#define B_11_1    -1.21542481739588805916051052503
#define B_11_2     0.
#define B_11_3     0.
#define B_11_4    16.6726086659457724322804132886
#define B_11_5      .915741828416817960595718650451
#define B_11_6    -6.05660580435747094755450554309
#define B_11_7   -16.0035735941561781118417064101
#define B_11_8    14.849303086297662557545391898
#define B_11_9   -13.3715757352898493182930413962
#define B_11_10    5.13418264817963793317325361166
#define B_12_1      .258860916438264283815730932232
#define B_12_2     0.
#define B_12_3     0.
#define B_12_4    -4.77448578548920511231011750971
#define B_12_5     -.43509301377703250944070041181
#define B_12_6    -3.04948333207224150956051286631
#define B_12_7     5.57792003993609911742367663447
#define B_12_8     6.15583158986104009733868912669
#define B_12_9    -5.06210458673693837007740643391
#define B_12_10    2.19392617318067906127491429047
#define B_12_11     .134627998659334941535726237887
#define B_13_1      .822427599626507477963168204773
#define B_13_2     0.
#define B_13_3     0.
#define B_13_4   -11.6586732572776642839765530355
#define B_13_5     -.757622116690936195881116154088
#define B_13_6      .713973588159581527978269282765
#define B_13_7    12.0757749868900567395661704486
#define B_13_8    -2.12765911392040265639082085897
#define B_13_9     1.99016620704895541832807169835
#define B_13_10    -.234286471544040292660294691857
#define B_13_11     .17589857770794226507310510589
#define B_13_12    0.

/*  The coefficients BHAT(*) refer to the formula used to advance the
   integration, here the one of order 8.  The coefficients B(*) refer
   to the other formula, here the one of order 7.  */

#define CHAT_1     .0417474911415302462220859284685
#define CHAT_2    0.
#define CHAT_3    0.
#define CHAT_4    0.
#define CHAT_5    0.
#define CHAT_6    -.0554523286112393089615218946547
#define CHAT_7     .239312807201180097046747354249
#define CHAT_8     .70351066940344302305804641089
#define CHAT_9    -.759759613814460929884487677085
#define CHAT_10    .660563030922286341461378594838
#define CHAT_11    .158187482510123335529614838601
#define CHAT_12   -.238109538752862804471863555306
#define CHAT_13    .25

#define C_1      .029553213676353496981964883112
#define C_2     0.
#define C_3     0.
#define C_4     0.
#define C_5     0.
#define C_6     -.828606276487797039766805612689
#define C_7      .311240900051118327929913751627
#define C_8     2.46734519059988698196468570407
#define C_9    -2.54694165184190873912738007542
#define C_10    1.44354858367677524030187495069
#define C_11     .0794155958811272872713019541622
#define C_12     .0444444444444444444444444444445
#define C_13    0.

#define A_1     0.
#define A_2      .0555555555555555555555555555556
#define A_3      .0833333333333333333333333333334
#define A_4      .125
#define A_5      .3125
#define A_6      .375
#define A_7      .1475
#define A_8      .465
#define A_9      .564865451382259575398358501426
#define A_10     .65
#define A_11     .924656277640504446745013574318
#define A_12    1.
#define A_13      A_12

#define N_EVALS 13
#define N_EVALS_PLUS_ONE 14

double take_pd89_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step)
{
   double *ivals[N_EVALS_PLUS_ONE], *ivals_p[N_EVALS], rval = 0.;
   int i, j, k;
   const double bvals[91] = { B_2_1,
       B_3_1, B_3_2,
       B_4_1, B_4_2, B_4_3,
       B_5_1, B_5_2, B_5_3, B_5_4,
       B_6_1, B_6_2, B_6_3, B_6_4, B_6_5,
       B_7_1, B_7_2, B_7_3, B_7_4, B_7_5, B_7_6,
       B_8_1, B_8_2, B_8_3, B_8_4, B_8_5, B_8_6, B_8_7,
       B_9_1, B_9_2, B_9_3, B_9_4, B_9_5, B_9_6, B_9_7, B_9_8,
       B_10_1, B_10_2, B_10_3, B_10_4, B_10_5, B_10_6, B_10_7, B_10_8, B_10_9,
       B_11_1, B_11_2, B_11_3, B_11_4, B_11_5, B_11_6, B_11_7, B_11_8, B_11_9, B_11_10,
       B_12_1, B_12_2, B_12_3, B_12_4, B_12_5, B_12_6, B_12_7, B_12_8, B_12_9, B_12_10, B_12_11,
       B_13_1, B_13_2, B_13_3, B_13_4, B_13_5, B_13_6, B_13_7, B_13_8, B_13_9, B_13_10, B_13_11, B_13_12,
       CHAT_1, CHAT_2, CHAT_3, CHAT_4, CHAT_5, CHAT_6, CHAT_7, CHAT_8, CHAT_9, CHAT_10, CHAT_11, CHAT_12, CHAT_13 };
   const double avals[N_EVALS_PLUS_ONE] = { 0, A_1, A_2, A_3, A_4, A_5,
             A_6, A_7, A_8, A_9, A_10, A_11, A_12, A_13 };
   const double *bptr = bvals;

   ivals[0] = (double *)calloc( (2 * N_EVALS + 1) * n_vals, sizeof( double));
   for( i = 0; i < N_EVALS; i++)
      {
      ivals[i + 1] = ivals[0] + (i + 1) * n_vals;
      ivals_p[i] = ivals[0] + (i + N_EVALS + 1) * n_vals;
      }

   for( j = 0; j <= N_EVALS; j++)
      {
      double ref_state_j[9], state_j[6];
      const double jd_j = jd + step * avals[j];

      compute_ref_state( ref_orbit, ref_state_j, jd_j);
      if( !j)
         {
//       debug_printf( "At JD %lf; step %lf\n", jd, step);
         memcpy( state_j, ival, 6 * sizeof( double));
               /* subtract the analytic posn/vel from the numeric: */
         for( i = 0; i < n_vals; i++)
            ivals[0][i] = ival[i] - ref_state_j[i];
         }
      else
         for( i = 0; i < n_vals; i++)
            {
            double tval = 0.;

            for( k = 0; k < j; k++)
               tval += bptr[k] * ivals_p[k][i];
            ivals[j][i] = tval * step + ivals[0][i];
            state_j[i] = ivals[j][i] + ref_state_j[i];
            }
      bptr += j;
      if( j != N_EVALS)
         {
         int k;

         calc_derivatives( jd_j, state_j, ivals_p[j], ref_orbit->central_obj);
         for( k = 0; k < 6; k++)
            ivals_p[j][k] -= ref_state_j[k + 3];
         }
      else     /* on last iteration,  we have our answer: */
         memcpy( ovals, state_j, n_vals * sizeof( double));
#ifdef PREVIOUSLY_USEFUL_DEBUGS
      if( count < DEBUG_COUNT)
         dump_rk_debug( j, ref_state_j, ivals[j], ivals_p[j]);
#endif
      }

   for( i = 0; i < n_vals; i++)
      {
      double tval = 0.;
      const double err_coeff[N_EVALS] = { CHAT_1 - C_1, CHAT_2 - C_2,
               CHAT_3  -  C_3, CHAT_4  -  C_4, CHAT_5  -  C_5, CHAT_6 - C_6,
               CHAT_7  -  C_7, CHAT_8  -  C_8, CHAT_9  -  C_9, CHAT_10 - C_10,
               CHAT_11 - C_11, CHAT_12 - C_12, CHAT_13 - C_13 };

      for( k = 0; k < N_EVALS; k++)
         tval += err_coeff[k] * ivals_p[k][i];
      rval += tval * tval;
      }
   return( sqrt( rval * step * step));
}

         /* These "original" constants can be found in Danby, p. 298.  */
         /* The ones actually used are from _Numerical Recipes_,  and  */
         /* are claimed to be slightly better.  (Must admit,  I've not */
         /* done a really careful comparison!)                         */
#ifdef ORIGINAL_FEHLBERG_CONSTANTS
#define RKF_B21 2. / 9.
#define RKF_B31 1. / 12.
#define RKF_B32 1. / 4.
#define RKF_B41 69. / 128.
#define RKF_B42 -243. / 128.
#define RKF_B43 135. / 64.
#define RKF_B51 -17. / 12.
#define RKF_B52 27. / 4.
#define RKF_B53 -27. / 5.
#define RKF_B54 16. / 15.
#define RKF_B61 65. / 432.
#define RKF_B62 -5. / 16.
#define RKF_B63 13 / 16.
#define RKF_B64 4 / 27.
#define RKF_B65 5. / 144.
#define RKF_CHAT1 47. / 450.
#define RKF_CHAT2 0.
#define RKF_CHAT3 12 / 25.
#define RKF_CHAT4 32. / 225.
#define RKF_CHAT5 1. / 30.
#define RKF_CHAT6 6. / 25.
#define RKF_C1  1. / 9.
#define RKF_C2 0.
#define RKF_C3 9. / 20.
#define RKF_C4 16. / 45.
#define RKF_C5 1. / 12.
#define RKF_C6 0.
#define RKF_A1       0.
#define RKF_A2       2. / 9.
#define RKF_A3       1. / 3.
#define RKF_A4       .75
#define RKF_A5       1.
#define RKF_A6       5. / 6.
#endif

#define RKF_B21     1. / 5.
#define RKF_B31     3. / 40.
#define RKF_B32     9. / 40.
#define RKF_B41     3. / 10.
#define RKF_B42    -9. / 10.
#define RKF_B43     6. / 5.
#define RKF_B51   -11. / 54.
#define RKF_B52     5. / 2.
#define RKF_B53   -70. / 27.
#define RKF_B54    35. / 27.
#define RKF_B61  1631. / 55296
#define RKF_B62   175. / 512.
#define RKF_B63   575. / 13824.
#define RKF_B64 44275. / 110592.
#define RKF_B65   253. / 4096.
#define RKF_CHAT1  2825. / 27648.
#define RKF_CHAT2 0.
#define RKF_CHAT3 18575. / 48384.
#define RKF_CHAT4 13525. / 55296.
#define RKF_CHAT5 277. / 14336.
#define RKF_CHAT6 .25
#define RKF_C1    37. / 378.
#define RKF_C2            0.
#define RKF_C3   250. / 621.
#define RKF_C4   125. / 594.
#define RKF_C5            0.
#define RKF_C6  512. / 1771.
#define RKF_A1           0.
#define RKF_A2            .2
#define RKF_A3            .3
#define RKF_A4            .6
#define RKF_A5           1.
#define RKF_A6            .875


#ifdef PREVIOUSLY_USEFUL_DEBUGS
static void dump_rk_debug( const int step, const double *ref_state,
                  const double *ivals, const double *ivals_p)
{
   int i;

   debug_printf( "Step %d:", step);
   debug_printf( "\n   Ref state: ");
   for( i = 0; i < 9; i++)
      debug_printf( "%.6e  ", ref_state[i]);
   debug_printf( "\n   ivals:     ");
   for( i = 0; i < 6; i++)
      debug_printf( "%.6e  ", ivals[i]);
   debug_printf( "\n   true state:");
   for( i = 0; i < 6; i++)
      debug_printf( "%.6e  ", ivals[i] + ref_state[i]);
   if( step != 6)
      {
      debug_printf( "\n   ivals_p:   ");
      for( i = 0; i < 6; i++)
         debug_printf( "%.6e  ", ivals_p[i]);
      debug_printf( "\n");
      }
}
#endif

#define DEBUG_COUNT 20

double take_rk_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step)
{
   double *ivals[7], *ivals_p[6], rval = 0.;
   int i, j, k;
            /* Revised values from _Numerical Recipes_: */
   const double bvals[21] = { RKF_B21,
            RKF_B31, RKF_B32,
            RKF_B41, RKF_B42, RKF_B43,
            RKF_B51, RKF_B52, RKF_B53, RKF_B54,
            RKF_B61, RKF_B62, RKF_B63, RKF_B64, RKF_B65,
            RKF_CHAT1, RKF_CHAT2, RKF_CHAT3,
            RKF_CHAT4, RKF_CHAT5, RKF_CHAT6 };

   const double avals[7] = { RKF_A1, RKF_A2, RKF_A3, RKF_A4, RKF_A5, RKF_A6, 1.};
   const double *bptr = bvals;
   double temp_ivals[78];
   static int count;

   if( count < DEBUG_COUNT)
      count++;
   if( n_vals > 6)
      ivals[0] = (double *)calloc( 13 * n_vals, sizeof( double));
   else
      ivals[0] = temp_ivals;
   for( i = 0; i < 6; i++)
      {
      ivals[i + 1] = ivals[0] + (i + 1) * n_vals;
      ivals_p[i] = ivals[0] + (i + 7) * n_vals;
      }

   for( j = 0; j < 7; j++)
      {
      double ref_state_j[9], state_j[6];
      const double jd_j = jd + step * avals[j];

      compute_ref_state( ref_orbit, ref_state_j, jd_j);
      if( !j)
         {
//       debug_printf( "At JD %lf; step %lf\n", jd, step);
         memcpy( state_j, ival, 6 * sizeof( double));
               /* subtract the analytic posn/vel from the numeric: */
         for( i = 0; i < n_vals; i++)
            ivals[0][i] = ival[i] - ref_state_j[i];
         }
      else
         for( i = 0; i < n_vals; i++)
            {
            double tval = 0.;

            for( k = 0; k < j; k++)
               tval += bptr[k] * ivals_p[k][i];
            ivals[j][i] = tval * step + ivals[0][i];
            state_j[i] = ivals[j][i] + ref_state_j[i];
            }
      bptr += j;
      if( j != 6)
         {
         int k;

         calc_derivatives( jd_j, state_j, ivals_p[j], ref_orbit->central_obj);
         for( k = 0; k < 6; k++)
            ivals_p[j][k] -= ref_state_j[k + 3];
         }
      else     /* on last iteration,  we have our answer: */
         memcpy( ovals, state_j, n_vals * sizeof( double));
#ifdef PREVIOUSLY_USEFUL_DEBUGS
      if( count < DEBUG_COUNT)
         dump_rk_debug( j, ref_state_j, ivals[j], ivals_p[j]);
#endif
      }

   for( i = 0; i < n_vals; i++)
      {
      double tval = 0.;
      static const double err_coeffs[6] = {
            RKF_CHAT1 - RKF_C1, RKF_CHAT2 - RKF_C2, RKF_CHAT3 - RKF_C3,
            RKF_CHAT4 - RKF_C4, RKF_CHAT5 - RKF_C5, RKF_CHAT6 - RKF_C6 };

      for( k = 0; k < 6; k++)
         tval += err_coeffs[k] * ivals_p[k][i];
      rval += tval * tval;
      }

#ifdef PREVIOUSLY_USEFUL_DEBUGS
   if( count < DEBUG_COUNT)
      {
      debug_printf( "\n   Returned vector:   ");
      for( i = 0; i < 6; i++)
         debug_printf( "%.6e  ", ovals[i]);
      debug_printf( "\n   Best fit planet: %d, %d\n", best_fit_planet,
                  ref_orbit->central_obj);
      }
#endif

   if( n_vals > 6)
      free( ivals[1]);
   return( sqrt( rval * step * step));
}

int symplectic_6( double jd, ELEMENTS *ref_orbit, double *vect,
                                          const double dt)
{
   int i, j;
#ifdef FOR_REFERENCE_ONLY
         /* Some compilers object to mathematically defined consts,  so  */
         /* I had to replace these lines with explicit numerical consts: */
   const double w1 = -0.117767998417887E1;
   const double w2 = 0.235573213359357E0;
   const double w3 = 0.784513610477560E0;
   const double w0 = (1-2*(w1+w2+w3));
   const double d6[7] = { w3, w2, w1, w0, w1, w2, w3 };
   const double c6[8] = { w3/2, (w3+w2)/2, (w2+w1)/2, (w1+w0)/2,
                         (w1+w0)/2, (w2+w1)/2, (w3+w2)/2, w3/2 };
#endif
   static const double d6[7] = { 0.7845136104775600,  0.2355732133593570,
            -1.1776799841788700, 1.3151863206839060, -1.1776799841788700,
             0.2355732133593570, 0.7845136104775600 };
   static const double c6[8] = { 0.3922568052387800,  0.5100434119184585,
            -0.4710533854097566, 0.0687531682525180,  0.0687531682525180,
            -0.4710533854097566, 0.5100434119184585,  0.3922568052387800 };

   for( i = 0; i < 8; i++)
      {
      double deriv[6];
      const double step = dt * c6[i];

      for( j = 0; j < 3; j++)
         vect[j] += step * vect[j + 3];
      jd += step;
      if( i != 7)
         {
         calc_derivatives( jd, vect, deriv, ref_orbit->central_obj);
         for( j = 3; j < 6; j++)
            vect[j] += dt * d6[i] * deriv[j];
         }
      }
   return( 0);
}

