#include <math.h>
#include <stdlib.h>
#include "watdefs.h"
#include "comets.h"
#include "afuncs.h"
#include "lunar.h"


#define PI 3.141592653589793238462643383279502884197169399375
#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)

void ecliptic_to_equatorial( double FAR *vect);            /* mpc_obs.cpp */
int parallax_to_lat_alt_general( const double rho_cos_phi,
               const double rho_sin_phi,
               double *lat, double *ht_in_planetary_radii,
               const double axis_ratio);                      /* ephem0.cpp */
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
double find_collision_time( ELEMENTS *elem, double *latlon); /* collide.cpp */
int find_lat_lon_alt( const double jd, const double *ivect,  /* collide.cpp */
                                       double *lat_lon_alt);

int debug_printf( const char *format, ...);                /* runge.cpp */

double planet_radius[15] = { 695992., 2439., 6051.,
/* earth-saturn */         6378.140, 3393., 71492., 60268.,
/* uranus-pluto, luna */   25559., 24764., 1195., 1737.4,
/* jupiter moons */        1821.3, 1565., 2634., 2403. };

#define N_FLATTENINGS 9

double find_collision_time( ELEMENTS *elem, double *latlon)
{
   double t_low = -2. / 24., t_high = 0.;    /* assume impact within 2 hrs */
   double t0 = -1. / 24.;
   const double alt_0 = atof( get_environment_ptr( "COLLISION_ALTITUDE"));
   int iter = 25, i;

   while( iter--)
      {
      double loc2k[4], vel2k[3], planet_matrix[9], loc[3];
      double altitude, ut, jd;
      static const double flattenings[N_FLATTENINGS] = {
            0., 0., 0., .00335364,              /* Sun Mer Ven Earth */
            .00647630, .0647630, .0979624,      /* Mars Jup Satu */
            .0229273, .0171 };                  /* Uran Nep */

      comet_posn_and_vel( elem, elem->perih_time + t0, loc2k, vel2k);
                /* Geocentric elems are already in J2000 equatorial coords. */
                /* Others are in ecliptic,  so cvt them to equatorial:      */
      if( elem->central_obj != 3)
         ecliptic_to_equatorial( loc2k);
      jd = elem->perih_time + t0;
      ut = jd - td_minus_ut( jd) / 86400.;
      calc_planet_orientation( elem->central_obj, 0, ut, planet_matrix);
               /* cvt J2000 to planet-centric coords: */
      precess_vector( planet_matrix, loc2k, loc);
      for( i = 0; i < 3; i++)          /* then cvt from AU to planet radii: */
         loc[i] /= planet_radius[elem->central_obj] / AU_IN_KM;
      parallax_to_lat_alt_general(
                       sqrt( loc[0] * loc[0] + loc[1] * loc[1]), loc[2],
                       latlon + 1, &altitude,
                       (elem->central_obj < N_FLATTENINGS ?
                       1. - flattenings[elem->central_obj] : 1.));
                           /* Convert altitude from planet radii to km: */
      altitude *= planet_radius[elem->central_obj];
      if( altitude < alt_0)
         t_high = t0;
      else
         t_low = t0;
      latlon[0] = -atan2( loc[1], loc[0]);
      if( latlon[0] < 0.)           /* keep in 0-360 range */
         latlon[0] += PI + PI;
//    debug_printf( "t0 = %lf: lat %lf, lon %lf, alt %lf\n",
//             t0, latlon[1] * 180. / PI, latlon[0] * 180. / PI, altitude);
      t0 = (t_low + t_high) / 2.;
      }
   return( t0);
}

/* 30 Jan 2009:  Rob Matson asked if I could provide ephemerides in
   geodetic lat/lon/alt for 2008 TC3,  in aid of running the resulting
   vector through the atmosphere. Input vector is assumed to be in
   geocentric equatorial J2000 and in AU;  time is assumed to be TT.
   Note shameless cannibalisation of code from above. */

int find_lat_lon_alt( const double jd, const double *ivect, double *lat_lon_alt)
{
   double planet_matrix[9];
   double loc[3], loc2k[3], r2;
   const double ut = jd - td_minus_ut( jd) / 86400.;

   loc2k[0] = ivect[0];
   loc2k[1] = ivect[1];
   loc2k[2] = ivect[2];
   calc_planet_orientation( 3, 0, ut, planet_matrix);
               /* cvt J2000 to planet-centric coords: */
   precess_vector( planet_matrix, loc2k, loc);
   lat_lon_alt[0] = -atan2( loc[1], loc[0]);
   if( lat_lon_alt[0] < 0.)           /* keep in 0-360 range */
      lat_lon_alt[0] += PI + PI;
   r2 = loc[0] * loc[0] + loc[1] * loc[1];
   lat_lon_alt[1] = atan( loc[2] / sqrt( r2));
   lat_lon_alt[2] = sqrt( r2 + loc[2] * loc[2]);
   return( 0);
}
