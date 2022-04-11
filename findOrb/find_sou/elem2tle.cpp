#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "watdefs.h"
#include "afuncs.h"
#include "comets.h"
#include "norad.h"
#include "date.h"

const double earth_mass_over_sun_mass = 2.98994e-6;
#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)
#define PI 3.141592653589793238462643383279502884197169399375105
#define MINUTES_PER_DAY 1440.

int elements_to_tle( tle_t *tle, const ELEMENTS *elem);
int vector_to_tle( tle_t *tle, const double *state_vect, const double epoch);
int write_tle_from_vector( char *buff, const double *state_vect,
        const double epoch, const char *norad_desig, const char *intl_desig);

void convert_elements( const double epoch_from, const double epoch_to,
      double *incl, double *asc_node, double *arg_per);     /* conv_ele.cpp */

#define centralize_angle(x) (fmod( (x) + PI * 10., PI + PI))
#define centralize_angle_and_cvt_to_degrees( x)  \
                             (centralize_angle( x) * (180. / PI))

int elements_to_tle( tle_t *tle, const ELEMENTS *elem)
{
   int rval = -1;

   if( elem->ecc < .99)
      {
      const double t0 =
          elem->major_axis * sqrt( elem->major_axis / earth_mass_over_sun_mass);
      double incl = elem->incl;
      double asc_node = elem->asc_node;
      double arg_per = elem->arg_per;
      double mean_anomaly = elem->mean_anomaly;

      tle->epoch = elem->epoch;
            /* The elements are in J2000,  but TLEs are given  */
            /* in epoch of date: */
      convert_elements( 2000., 2000. + (elem->epoch - 2451545.) / 365.25,
                       &incl, &asc_node, &arg_per);     /* conv_ele.cpp */
      tle->xincl = centralize_angle( incl);
      tle->xnodeo = centralize_angle( asc_node);
      tle->omegao = centralize_angle( arg_per);
      tle->xmo = centralize_angle( mean_anomaly);
      tle->xno = (PI * 2.) / (t0 * 365.25 * MINUTES_PER_DAY);
                     /* xno is now in radians per minute */
      tle->eo = elem->ecc;
            /* Address these three values later: */
      tle->xndt2o = tle->xndd6o = tle->bstar = 0.;
      rval = 0;
      }
   return( rval);
}

int vector_to_tle( tle_t *tle, const double *state_vect, const double epoch)
{
   ELEMENTS elem;
   int rval = -1;

   calc_classical_elements( &elem, state_vect, epoch, 1,
                                    SOLAR_GM * earth_mass_over_sun_mass);
   if( elem.ecc < .99)
      {
      elem.epoch = epoch;
      elements_to_tle( tle, &elem);
      rval = 0;
      }
   return( rval);
}

int write_tle_from_vector( char *buff, const double *state_vect,
        const double epoch, const char *norad_desig, const char *intl_desig)
{
   tle_t tle;
   int rval = 0;

   memset( &tle, 0, sizeof( tle_t));
   rval = vector_to_tle( &tle, state_vect, epoch);
   if( !rval)
      {
      if( norad_desig)
         tle.norad_number = atoi( norad_desig);
      else
         tle.norad_number = 0;
      if( intl_desig)
         strcpy( tle.intl_desig, intl_desig);
      else
         tle.intl_desig[0] = '\0';
      tle.classification = 'U';
      tle.ephemeris_type = '0';
      write_elements_in_tle_format( buff, &tle);
      }
   else
      *buff = '\0';
   return( rval);
}
