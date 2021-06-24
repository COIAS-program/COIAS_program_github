#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include "watdefs.h"
#include "comets.h"
#include "mpc_obs.h"
#include "monte0.h"

#define PI 3.14159265358979323846264338397

void add_monte_orbit( double *monte_data, const ELEMENTS *elem,
                  const int n_orbits)
{
   double tarr[MONTE_N_ENTRIES];
   double *offsets = monte_data + 2 * MONTE_N_ENTRIES;
   int i;

   tarr[MONTE_TP] = elem->perih_time;
// tarr[MONTE_PER] = elem->major_axis *
//                    sqrt( elem->major_axis / planet_mass[elem->central_obj]);
   tarr[MONTE_ECC] = elem->ecc;
   tarr[MONTE_q] = elem->major_axis * (1. - elem->ecc);
   tarr[MONTE_Q] = elem->major_axis * (1. + elem->ecc);
   tarr[MONTE_INV_A] = 1. / elem->major_axis;
   tarr[MONTE_INCL] = elem->incl;
   tarr[MONTE_MEAN_ANOM] = elem->mean_anomaly * 180. / PI;
   tarr[MONTE_ARG_PER] = elem->arg_per * 180. / PI;
   tarr[MONTE_ASC_NODE] = elem->asc_node * 180. / PI;

   if( !n_orbits)                /* initializing step */
      for( i = 0; i < MONTE_N_ENTRIES; i++)
         {
         offsets[i] = tarr[i];
         monte_data[i] = monte_data[i + MONTE_N_ENTRIES] = 0.;
         }
   else
      {
      for( i = 0; i < MONTE_N_ENTRIES; i++)
         {
         double delta = tarr[i] - offsets[i];

         if( i >= MONTE_INCL && i <= MONTE_ASC_NODE)
            if( delta > 180.)            /* keep angular arguments in the */
               delta -= 360.;            /* proper range,  not wrapping   */
            else if( delta < -180.)      /* around at +/- 180 degrees     */
               delta += 360.;
         monte_data[i] += delta;
         monte_data[i + MONTE_N_ENTRIES] += delta * delta;
         }
      }
}

void compute_monte_sigmas( double *sigmas, const double *monte_data,
                  const int n_orbits)
{
   int i;

   for( i = 0; i < MONTE_N_ENTRIES; i++)
      {
      const double avg_square = monte_data[i + MONTE_N_ENTRIES] / (double)n_orbits;
      const double avg_value = monte_data[i] / (double)n_orbits;

      sigmas[i] = sqrt( avg_square - avg_value * avg_value);
      }
}


/* Add some Gaussian noise to each RA/dec value.  Two Gaussian-distributed
random numbers are generated,  then added to the RA and dec,  scaled to
the noise_in_arcseconds.  The original RA/decs are stored in an array;
calling 'remove_gaussian_noise_from_obs()' restores them,  removing the
noise. */

double *add_gaussian_noise_to_obs( int n_obs, OBSERVE *obs,
                 const double noise_in_arcseconds)
{
   const double noise_in_radians = noise_in_arcseconds * PI / (180. * 3600.);
   double *stored_ra_decs = (double *)calloc( 2 * n_obs, sizeof( double));
   double *tptr = stored_ra_decs;

   while( n_obs--)
      {
      const double rt = log( ((double)rand( ) + .5) / ((double)RAND_MAX+1.));
      const double r = sqrt( -2. * rt);
      const double theta = 2. * PI * (double)rand( ) / (double)RAND_MAX;
      const double dx = r * cos( theta) * noise_in_radians;
      const double dy = r * sin( theta) * noise_in_radians;

      *tptr++ = obs->ra;
      *tptr++ = obs->dec;
      obs->ra += dx / cos( obs->dec);
      obs->dec += dy;
      obs++;
      }
   return( stored_ra_decs);
}

void remove_gaussian_noise_from_obs( int n_obs, OBSERVE *obs,
                           double *stored_ra_decs)
{
   double *tptr = stored_ra_decs;

   while( n_obs--)
      {
      obs->ra = *tptr++;
      obs->dec = *tptr++;
      obs++;
      }
   free( stored_ra_decs);
}
