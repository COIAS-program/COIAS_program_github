#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "watdefs.h"
#include "comets.h"
#include "mpc_obs.h"

#define PI 3.141592653589793238462643383279502884197169399375105

double evaluate_initial_orbit( const OBSERVE FAR *obs,   /* orb_func.cpp */
                              const int n_obs, const double *orbit);
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */

#define SIMPLEX struct simplex

SIMPLEX
   {
   double r1, r2, score;
   };

extern int debug_level;
int debug_printf( const char *format, ...);


static double try_simplex_reflection( OBSERVE FAR *obs, int n_obs,
               SIMPLEX simplex[3], const double reflect)
{
   double r1 = (simplex[0].r1 + simplex[1].r1) * (1. - reflect) / 2.
                     + reflect * simplex[2].r1;
   double r2 = (simplex[0].r2 + simplex[1].r2) * (1. - reflect) / 2.
                     + reflect * simplex[2].r2;
   double orbit[6], new_score;
   int i;

                   /* guard against negative/artificially low values */
   for( i = 0; i < 3; i++)
      {
      if( r1 < simplex[i].r1 / 2.)
         r1 = simplex[i].r1 / 2.;
      if( r2 < simplex[i].r2 / 2.)
         r2 = simplex[i].r2 / 2.;
      }

   herget_method( obs, n_obs, r1, r2, orbit, NULL, NULL, NULL);
   new_score = evaluate_initial_orbit( obs, n_obs, orbit);
   if( new_score <= simplex[2].score)         /* step is an improvement */
      {
      simplex[2].r1 = r1;
      simplex[2].r2 = r2;
      simplex[2].score = new_score;
      }
   return( new_score);
}

int simplex_method( OBSERVE FAR *obs, int n_obs, double *orbit,
               const double r1, const double r2)
{
   SIMPLEX simplex[3];
   int i, j, iter;
   int max_iter = atoi( get_environment_ptr( "SIMPLEX_ITER"));
   double temp_orbit[6];

   if( !max_iter)
      max_iter = 70;
   for( i = 0; i < 3; i++)
      {
      simplex[i].r1 = r1 * ((i & 1) ? 1. : 1.1);
      simplex[i].r2 = r2 * ((i & 2) ? 1. : 1.1);
      herget_method( obs, n_obs, simplex[i].r1, simplex[i].r2,
                                temp_orbit, NULL, NULL, NULL);
      simplex[i].score = evaluate_initial_orbit( obs, n_obs, temp_orbit);
      }
   for( iter = 0; iter < max_iter; iter++)
      {
      double new_score;

      for( i = 1; i < 3; i++)
         for( j = 0; j < i; j++)    /* sort so simplex[0] = lowest-score, */
            if( simplex[i].score < simplex[j].score)  /* simplex[2] = highest */
               {
               SIMPLEX temp_simp = simplex[i];

               simplex[i] = simplex[j];
               simplex[j] = temp_simp;
               }
      if( debug_level > 2)
         {
         double dot_prod = (simplex[1].r1 - simplex[0].r1) *
                           (simplex[2].r2 - simplex[0].r2) -
                           (simplex[2].r1 - simplex[0].r1) *
                           (simplex[1].r2 - simplex[0].r2);

         debug_printf( "Simplex %d: %lg\n", iter, dot_prod);
         for( i = 0; i < 3; i++)
            debug_printf( "   r1 = %lf, r2 = %lf: score %lf (%lf %lf)\n",
                        simplex[i].r1, simplex[i].r2, simplex[i].score,
                        simplex[i].r1 - simplex[0].r1,
                        simplex[i].r2 - simplex[0].r2);
         }
      new_score = try_simplex_reflection( obs, n_obs, simplex, -1.);
                  /* If step was a new 'best',  try doubling it: */
      if( new_score < simplex[0].score)
         {
         try_simplex_reflection( obs, n_obs, simplex, 2.);
         if( debug_level > 2)
            debug_printf( "Doubled\n");
         }
      else if( new_score > simplex[1].score)
         {
         const double contracted =
               try_simplex_reflection( obs, n_obs, simplex, .5);

         if( debug_level > 2)
            debug_printf( contracted > new_score ?
                              "Contracting\n" : "Half-con\n");
         if( contracted > new_score)   /* can't get rid of it;  try  */
            for( i = 1; i < 3; i++)     /* contracting around our best point */
               {
               simplex[i].r1 += .5 * (simplex[0].r1 - simplex[i].r1);
               simplex[i].r2 += .5 * (simplex[0].r2 - simplex[i].r2);
               herget_method( obs, n_obs, simplex[i].r1, simplex[i].r2,
                                temp_orbit, NULL, NULL, NULL);
               simplex[i].score = evaluate_initial_orbit( obs, n_obs, temp_orbit);
               }
         }
      else
         if( debug_level > 2)
            debug_printf( "Simple step\n");
      }
   herget_method( obs, n_obs, simplex[0].r1, simplex[0].r2,
                                orbit, NULL, NULL, NULL);
   return( iter);
}

#define SUPERPLEX struct superplex

SUPERPLEX
   {
   double orbit[6];
   double score;
   };

int set_locs( const double *orbit, double t0, OBSERVE FAR *obs, int n_obs);

static double try_superplex_reflection( OBSERVE FAR *obs, int n_obs,
               SUPERPLEX superplex[7], const double reflect)
{
   double orbit[6], new_score;
   int i, j;
   const int n_reflect = 6;

   for( i = 0; i < 6; i++)
      {
      orbit[i] = superplex[6].orbit[i] * reflect;
      for( j = 0; j < n_reflect; j++)
         orbit[i] += (1. - reflect) * superplex[j].orbit[i] / (double)n_reflect;
      }

   set_locs( orbit, obs[0].jd, obs, n_obs);
   new_score = evaluate_initial_orbit( obs, n_obs, orbit);
   if( new_score <= superplex[6].score)         /* step is an improvement */
      {
      memcpy( superplex[6].orbit, orbit, 6 * sizeof( double));
      superplex[6].score = new_score;
      }
   return( new_score);
}

extern int debug_level;
int debug_printf( const char *format, ...);

int superplex_method( OBSERVE FAR *obs, int n_obs, double *orbit)
{
   SUPERPLEX superplex[7];
   int iter, i, j;
   int max_iter = atoi( get_environment_ptr( "SUPERPLEX_ITER"));

   if( !max_iter)
      max_iter = 70;
   while( n_obs && !obs[n_obs - 1].is_included)
      n_obs--;
   for( i = 0; i < 7; i++)
      {
      memcpy( superplex[i].orbit, orbit, 6 * sizeof( double));
      if( i < 6)
         superplex[i].orbit[i] *= .9999;
      set_locs( superplex[i].orbit, obs[0].jd, obs, n_obs);
      superplex[i].score = evaluate_initial_orbit( obs, n_obs,
                                  superplex[i].orbit);
      }
   for( iter = 0; iter < max_iter; iter++)
      {
      double new_score;

      for( i = 1; i < 7; i++)       /* sort in increasing order of score */
         {
         for( j = i; j && superplex[j - 1].score > superplex[i].score;
                              j--)
            ;
         if( j != i)
            {
            SUPERPLEX temp_simp = superplex[i];

            memmove( superplex + j + 1, superplex + j,
                        (i - j) * sizeof( SUPERPLEX));
            superplex[j] = temp_simp;
            }
         }
      new_score = try_superplex_reflection( obs, n_obs, superplex, -1.);
      if( debug_level > 2)
         debug_printf( "Iter %d: score %lf\n", iter, superplex[6].score);
      if( debug_level > 3)
         for( i = 0; i < 7; i++)
            {
            int j;

            debug_printf( "%d (%lf): ", i, superplex[i].score);
            for( j = 0; j < 6; j++)
               debug_printf( "%11.6lf", superplex[i].orbit[j]);
            debug_printf( "\n");
            }
                  /* If step was a new 'best',  try doubling it: */
      if( new_score < superplex[0].score)
         {
         try_superplex_reflection( obs, n_obs, superplex, 2.);
         if( debug_level > 2)
            debug_printf( "Doubled\n");
         }
      else if( new_score >= superplex[5].score)
         {
         const double contracted =
               try_superplex_reflection( obs, n_obs, superplex, .5);

         if( debug_level > 2)
            debug_printf( contracted > new_score ?
                              "Contracting\n" : "Half-con\n");
         if( contracted > new_score)   /* can't get rid of it;  try  */
            for( i = 1; i < 6; i++)     /* contracting around our best point */
               {
               int j;

               for( j = 0; j < 6; j++)
                  superplex[i].orbit[j] =
                        (superplex[i].orbit[j] + superplex[0].orbit[j]) * .5;
               set_locs( superplex[i].orbit, obs[0].jd, obs, n_obs);
               superplex[i].score = evaluate_initial_orbit( obs, n_obs,
                                  superplex[i].orbit);
               }
         }
      else
         if( debug_level > 2)
            debug_printf( "Simple step\n");
      }
   memcpy( orbit, superplex[0].orbit, 6 * sizeof( double));
   set_locs( superplex[0].orbit, obs[0].jd, obs, n_obs);
   return( iter);
}

 /* For filtering to work,  you need at least three observations with */
 /* residuals inside the desired max_residual limit.  We do one pass  */
 /* just to make sure there are at least three observations that'll   */
 /* still be active when the filtering is done.  If not,  we make     */
 /* no changes and return FILTERING_FAILED.                           */

#define FILTERING_CHANGES_MADE            1
#define FILTERING_NO_CHANGES_MADE         2
#define FILTERING_FAILED                  3

int filter_obs( OBSERVE FAR *obs, const int n_obs,
                  const double max_residual_in_arcseconds)
{
   const double max_resid =            /* cvt arcseconds to radians */
                   max_residual_in_arcseconds * PI / (180. * 3600.);
   int i, pass, n_active = 0, rval = FILTERING_NO_CHANGES_MADE;

   for( pass = 0; pass < 2; pass++)
      {
      for( i = 0; i < n_obs && rval != FILTERING_FAILED; i++)
         {
         const double dy = obs[i].dec - obs[i].computed_dec;
         const double dx = (obs[i].ra - obs[i].computed_ra) * cos( obs[i].dec);
         const int is_okay = (dx * dx + dy * dy < max_resid * max_resid);

         if( !pass && is_okay)
            {
            n_active++;
            if( n_active == 3)      /* found enough;  break out of loop */
               i = n_obs;
            }
         if( pass && is_okay != obs[i].is_included)
            {
            obs[i].is_included ^= 1;
            rval = FILTERING_CHANGES_MADE;
            }
         }
      if( n_active < 3)
         rval = FILTERING_FAILED;
      }
   return( rval);
}
