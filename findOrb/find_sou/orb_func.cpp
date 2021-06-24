#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include "watdefs.h"
#include "comets.h"
#include "mpc_obs.h"
#include "lsquare.h"
#include "date.h"
#include "afuncs.h"
#ifndef _MSC_VER
#ifdef USE_MYCURSES
   #include "mycurses.h"
#else
#ifndef __WATCOMC__
#ifndef XCURSES
   #define PDC_DLL_BUILD
#endif
#endif
   #include "curses.h"
#endif
#endif

int perturbers = 0;
int integration_method = 0;
extern int debug_level;

#define AUTOMATIC_PERTURBERS  1
#define J2000 2451545.
#define JD_TO_YEAR( jd)  (2000. + ((jd) - J2000) / 365.25)
#define MAX_CONSTRAINTS 5
#define PI 3.141592653589793238462643383279502884197
#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)
#define SQRT_2 1.41421356
#define SRP1AU 2.3e-7
   /* "Solar radiation pressure at 1 AU",  in kg*AU^3 / (m^2*d^2) */
   /* from a private communication from Steve Chesley             */

int n_extra_params = 0, setting_outside_of_arc = 1;
double solar_pressure[3];

int debug_printf( const char *format, ...);
double initial_orbit( OBSERVE FAR *obs, int n_obs, double *orbit);
double compute_rms( const OBSERVE FAR *obs, int n_obs, int method);
int adjust_herget_results( OBSERVE FAR *obs, int n_obs, double *orbit);
int find_trial_orbit( double *orbit, OBSERVE FAR *obs, int n_obs,
             const double r1, const double angle_param);   /* orb_func.cpp */
int set_locs( const double *orbit, double t0, OBSERVE FAR *obs, int n_obs);
int find_best_fit_planet( const double jd, const double *ivect,
                                 double *rel_vect);         /* runge.cpp */
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
double convenient_gauss( const OBSERVE FAR *obs, int n_obs, double *orbit,
                  const double mu, const int desired_soln); /* gauss.cpp */
static int evaluate_limited_orbit( const double *orbit,
                    const int planet_orbiting, const double epoch,
                    const char *limited_orbit, double *constraints);
void remove_trailing_cr_lf( char *buff);      /* ephem0.cpp */
int find_relative_orbit( const double jd, const double *ivect,
               ELEMENTS *elements, double *rel_vect, const int ref_planet);
void format_dist_in_buff( char *buff, const double dist_in_au); /* ephem0.c */
static inline void look_for_best_subarc( const OBSERVE FAR *obs,
       const int n_obs, const double max_arc_len, int *start, int *end);
int check_for_perturbers( const double t_cen, const double *vect); /* sm_vsop*/
int get_idx1_and_idx2( const int n_obs, const OBSERVE FAR *obs,
                                int *idx1, int *idx2);      /* elem_out.c */

static void set_distance( OBSERVE FAR *obs, double r)
{
   int i;
   double d = 0.;

   obs->r = r;
   for( i = 0; i < 3; i++)
      {
      double p = obs->obs_posn[i] + r * obs->vect[i];

      obs->obj_posn[i] = p;
      d += p * p;
      }
   obs->solar_r = sqrt( d);
}

static double find_r_given_solar_r( const OBSERVE FAR *obs,
                                                     const double solar_r)
{
   double r_dot_v = 0., r_dot_r = 0., b, c, discr, rval = -1.;
   int i;

   for( i = 0; i < 3; i++)
      {
      r_dot_r += obs->obs_posn[i] * obs->obs_posn[i];
      r_dot_v += obs->obs_posn[i] * obs->vect[i];
      }
   b = 2. * r_dot_v;
   c = r_dot_r - solar_r * solar_r;
   discr = b * b - 4 * c;
   if( discr > 0.)
      rval = (-b + sqrt( discr)) / 2.;
   return( rval);
}

int calc_derivatives( const double jd, const double *ival, double *oval,
                           const int reference_planet);
double take_rk_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step);      /* runge.cpp */
double take_pd89_step( const double jd, ELEMENTS *ref_orbit,
                 const double *ival, double *ovals,
                 const int n_vals, const double step);      /* runge.cpp */
void compute_ref_state( ELEMENTS *ref_orbit, double *ref_state,
                                          const double jd);
int symplectic_6( double jd, ELEMENTS *ref_orbit, double *vect,
                                          const double dt);

double integration_tolerance = 1.e-11;

char *runtime_message;
int show_runtime_messages = 1;

static int reference_planet = 0;
static int perturbers_automatically_found;

#define STEP_INCREMENT 2
#define ENCKE_CHANGE_LIMIT .01

void integrate_orbit( double *orbit, const double t0, const double t1)
{
   const double fixed_step_size =
                        atof( get_environment_ptr( "FIXED_STEP_SIZE"));
   static double stepsize = 2.;
   const double min_stepsize = 1e-6;
   const double chicken = .9;
   extern int reset_of_elements_needed;
   const double step_increase = chicken * integration_tolerance
                 / pow( STEP_INCREMENT, (integration_method ? 9. : 5.));
   extern int use_cowell;
   double t = t0;
#ifndef _MSC_VER
   static time_t real_time = (time_t)0;
   double prev_t = t, last_err = 0.;
   int n_rejects = 0;
#endif
   int n_steps = 0, saved_perturbers = perturbers;
   static int n_changes;
   static ELEMENTS ref_orbit;

   reset_of_elements_needed = 1;
   if( fixed_step_size)
      stepsize = fixed_step_size;
   stepsize = fabs( stepsize);
   if( t1 < t0)
      stepsize = -stepsize;
   while( t != t1)
      {
      double delta_t, new_t = ceil( t / stepsize + .5) * stepsize;

      if( perturbers & AUTOMATIC_PERTURBERS)
         {
         const int perturbing_planet = check_for_perturbers(
                        (t - J2000) / 36525., orbit);

         perturbers = AUTOMATIC_PERTURBERS | (1 << perturbing_planet);
         if( perturbing_planet == 3)    /* add in the moon,  too: */
            perturbers |= (1 << 10);
         perturbers_automatically_found |= perturbers;
//       if( perturbing_planet)
//          debug_printf( "Perturber %d found\n", perturbing_planet);
         }
      if( reset_of_elements_needed || !(n_steps % 1))
         if( use_cowell != 1)
            {
            extern int best_fit_planet;

            find_relative_orbit( t, orbit, &ref_orbit, NULL, best_fit_planet);
            reset_of_elements_needed = 0;
            reference_planet = ref_orbit.central_obj;
            if( !perturbers && !use_cowell)  /* for unperturbed cases,  do  */
               {                    /* a two-body soln and go home */
               double ref_state[9];

               compute_ref_state( &ref_orbit, ref_state, t1);
               memcpy( orbit, ref_state, 6 * sizeof( double));
               return;
               }
            }
#ifdef CONTINUOUS_STEP
      new_t = t + stepsize;
#endif
      n_steps++;
#ifndef _MSC_VER
      if( time( NULL) != real_time && show_runtime_messages)
         {
         char buff[80];
         extern int best_fit_planet, n_posns_cached;
         extern double best_fit_planet_dist;
#ifdef TEST_PLANET_CACHING_HASH_FUNCTION
         extern long total_n_searches, total_n_probes, max_probes_required;
#endif

         real_time = time( NULL);
         if( runtime_message)
            mvaddnstr( 9, 10, runtime_message, -1);
         sprintf( buff, "t = %.5lf; %.5lf to %.5lf; step %.4e   ",
                 JD_TO_YEAR( t), JD_TO_YEAR( t0), JD_TO_YEAR( t1), stepsize);
         mvaddnstr( 10, 10, buff, -1);
         sprintf( buff, " %02ld:%02ld:%02ld; %lf; %d cached   ",
                     (real_time / 3600) % 24L,
                     (real_time / 60) % 60, real_time % 60, t - prev_t,
                     n_posns_cached);
         prev_t = t;
         mvaddnstr( 11, 10, buff, -1);
         sprintf( buff, "%d steps; %d rejected; center %d, ",
                           n_steps, n_rejects, best_fit_planet);
         format_dist_in_buff( buff + strlen( buff), best_fit_planet_dist);
         mvaddnstr( 12, 10, buff, -1);
         sprintf( buff, "last err: %.3e/%.3e  n changes: %d  ",
                        last_err, step_increase, n_changes);
         mvaddnstr( 13, 10, buff, -1);
         if( use_cowell != 1)
            {
            sprintf( buff, "e = %.5lf; q = ", ref_orbit.ecc);
            format_dist_in_buff( buff + strlen( buff), ref_orbit.q);
            strcat( buff, "     ");
            mvaddnstr( 18, 10, buff, -1);
            }
         sprintf( buff, "Pos: %11.6lf %11.6lf %11.6lf",
                     orbit[0], orbit[1], orbit[2]);
         mvaddnstr( 14, 10, buff, -1);
         sprintf( buff, "Vel: %11.6lf %11.6lf %11.6lf",
                     orbit[3], orbit[4], orbit[5]);
         mvaddnstr( 15, 10, buff, -1);
#ifdef TEST_PLANET_CACHING_HASH_FUNCTION
         if( total_n_searches)
            {
            sprintf( buff, "%ld searches; avg %.2lf max %ld   \n",
                            total_n_searches,
                            (double)total_n_probes / (double)total_n_searches,
                            max_probes_required);
            mvaddnstr( 16, 10, buff, -1);
            }
#endif
         refresh( );
         }
#endif

      if( t1 > t)             /* Make sure we don't step completely past */
         if( new_t > t1)      /* the time t1 we want to stop at!  If our */
            {                 /* step would do that,  cut it down to size. */
            delta_t = t1 - t;
            new_t = t1;
            }
         else
            delta_t = new_t - t;
      else               /* t1 >= t */
         if( new_t < t1)
            {
            delta_t = t1 - t;
            new_t = t1;
            }
         else
            delta_t = new_t - t;

      switch( integration_method)
         {
         case 1:
            symplectic_6( t, &ref_orbit, orbit, delta_t);
            break;
         default:
            {
            double new_vals[6];
            const double err = (integration_method ?
                   take_pd89_step( t, &ref_orbit, orbit, new_vals, 6, delta_t) :
                   take_rk_step( t, &ref_orbit, orbit, new_vals, 6, delta_t));
#ifdef CONTINUOUS_STEP
            const double new_step =
                      .9 * delta_t * pow( integration_tolerance / err, .2);
#endif

            if( !stepsize)
               exit( 0);
            if( fixed_step_size || err < integration_tolerance
                        || fabs( stepsize) < min_stepsize)  /* it's good! */
               {
               memcpy( orbit, new_vals, 6 * sizeof( double));
                  if( !fixed_step_size && err < step_increase)
                     if( fabs( delta_t - stepsize) < fabs( stepsize * .01))
                        {
                        n_changes++;
                        stepsize *= STEP_INCREMENT;
                        }
               }
            else           /* failed:  try again with a smaller step */
               {
#ifndef _MSC_VER
               n_rejects++;
#endif
               new_t = t;
               stepsize /= STEP_INCREMENT;
               reset_of_elements_needed = 1;
               }
#ifndef _MSC_VER
            last_err = err;
#endif
#ifdef CONTINUOUS_STEP
            stepsize = new_step;
#endif
            }
            break;
         }
      t = new_t;
      }
   perturbers = saved_perturbers;
}

static void light_time_lag( const double *orbit, const double *observer, double *result)
{
   double r = 0., delta, dt, solar_r2 = 0., afact;
   int i;

   for( i = 0; i < 3; i++)
      {
      delta = orbit[i] - observer[i];
      r += delta * delta;
      solar_r2 += orbit[i] * orbit[i];
      }
   r = sqrt( r);
   dt = -r / AU_PER_DAY;
   afact = 1. - SOLAR_GM * .5 * dt * dt / (sqrt( solar_r2) * solar_r2);
   for( i = 0; i < 3; i++)
      result[i] = afact * orbit[i] + dt * orbit[i + 3];
}

static void set_solar_r( OBSERVE FAR *ob)
{
   double r = 0.;
   int i;

   for( i = 0; i < 3; i++)
      r += ob->obj_posn[i] * ob->obj_posn[i];
   ob->solar_r = sqrt( r);
}

int set_locs( const double *orbit, const double t0, OBSERVE FAR *obs,
                       const int n_obs)
{
   int i, j;
   double curr_orbit[6], curr_t, tvals[6];

   for( i = 0; i < n_obs && obs[i].jd < t0; i++)
      ;

               /* integrate _forward_... */
   memcpy( curr_orbit, orbit, 6 * sizeof( double));
   curr_t = t0;
   for( j = i; j < n_obs; j++)
      {
      OBSERVE FAR *optr = obs + j;

      integrate_orbit( curr_orbit, curr_t, optr->jd);
      curr_t = optr->jd;
      FMEMCPY( tvals, optr->obs_posn, 3 * sizeof( double));
      light_time_lag( curr_orbit, tvals, tvals + 3);
      FMEMCPY( optr->obj_posn, tvals + 3, 3 * sizeof( double));
      FMEMCPY( optr->obj_vel, curr_orbit + 3, 3 * sizeof( double));
      }

               /* ...then integrate _backward_... */
   memcpy( curr_orbit, orbit, 6 * sizeof( double));
   curr_t = t0;
   for( j = i - 1; j >= 0; j--)
      {
      OBSERVE FAR *optr = obs + j;

      integrate_orbit( curr_orbit, curr_t, optr->jd);
      curr_t = optr->jd;
      FMEMCPY( tvals, optr->obs_posn, 3 * sizeof( double));
      light_time_lag( curr_orbit, tvals, tvals + 3);
      FMEMCPY( optr->obj_posn, tvals + 3, 3 * sizeof( double));
      FMEMCPY( optr->obj_vel, curr_orbit + 3, 3 * sizeof( double));
      }

   for( i = 0; i < n_obs; i++)
      {
      double loc[3], ra, dec, temp, r = 0.;
      static const double sin_obliq_2000 = .397777156;
      static const double cos_obliq_2000 = .917482062;

      for( j = 0; j < 3; j++)
         {
         loc[j] = obs[i].obj_posn[j] - obs[i].obs_posn[j];
         r += loc[j] * loc[j];
         }
      r = sqrt( r);
      obs[i].r = r;
      temp = loc[1] * cos_obliq_2000 - loc[2] * sin_obliq_2000;
      loc[2] = loc[2] * cos_obliq_2000 + loc[1] * sin_obliq_2000;
      loc[1] = temp;
      ra = atan2( loc[1], loc[0]);
      if( r > 100000. || r <= 0.)
         debug_printf( "???? bad r: %lf %lf %lf\n",
                  loc[0], loc[1], loc[2]);
      if( r)
         dec = asine( loc[2] / r);
      else
         dec = 0.;
      while( ra - obs[i].ra > PI)
         ra -= 2. * PI;
      while( ra - obs[i].ra < -PI)
         ra += 2. * PI;
      obs[i].computed_ra = ra;
      obs[i].computed_dec = dec;
      set_solar_r( obs + i);
      }
   return( 0);
}

double compute_rms( const OBSERVE FAR *obs, int n_obs, int method)
{
   double rval = 0., d2;
   int i, n_included = 0;

   for( i = n_obs; i; i--, obs++)
      if( obs->is_included)
         {
         double d_ra  = obs->computed_ra  - obs->ra;
         double d_dec = obs->computed_dec - obs->dec;

         d_ra *= cos( obs->computed_dec);
         d2 = d_dec * d_dec + d_ra * d_ra;
         if( method == 1)      /* computing root-mean-square error */
            rval += d2;
         if( method == 2)      /* computing mean error */
            rval += sqrt( d2);
         n_included++;
         }
   rval /= (double)n_included;
   if( method == 1)
      rval = sqrt( rval);
   return( 3600. * (180. / PI) * rval);
}

static double eval_3x3_determinant( const double *a, const double *b,
                         const double *c)
{
   return( a[0] * (b[1] * c[2] - c[1] * b[2])
         + b[0] * (c[1] * a[2] - a[1] * c[2])
         + c[0] * (a[1] * b[2] - b[1] * a[2]));
}

/* 'find_transfer_orbit' finds the state vector that can get an object
from the location/time described at 'obs1' to that described at 'obs2'.
It does this with the logic given in 'herget.htm#sund_xplns'. */
/* 24 Jun 2007:  realized 'accel0' wasn't used any more and removed it. */

static int find_transfer_orbit( double *orbit, OBSERVE FAR *obs1,
                                    OBSERVE FAR *obs2)
{
   double r = 0., delta_t = obs2->jd - obs1->jd;
   double deriv[6], speed_squared = 0., speed;
   double diff_squared = 999.;
   int i, max_iterations = 10;

   set_distance( obs1, obs1->r);
   set_distance( obs2, obs2->r);

   for( i = 0; i < 3; i++)
      {
                  /* find midpoint between obs1 and obs2... */
      orbit[i] = (obs2->obj_posn[i] + obs1->obj_posn[i]) / 2.;
                  /* and the average velocity connecting them: */
      orbit[i + 3] = (obs2->obj_posn[i] - obs1->obj_posn[i]) / delta_t;
      speed_squared += orbit[i + 3] * orbit[i + 3];
      }

                  /* speed_squared is in AU/day, speed in km/second: */
   speed = sqrt( speed_squared) * AU_IN_KM / 86400.;
   if( debug_level > 5)
      debug_printf( "Speed = %lf km/s\n", speed);
   if( speed > 5000.)
      return( -2);
   calc_derivatives( (obs1->jd + obs2->jd) / 2., orbit, deriv, -1);
   for( i = 0; i < 3; i++)
      {
      orbit[i] = obs1->obj_posn[i];
      orbit[3 + i] -= deriv[i + 3] * delta_t / 2.;
      }

            /* Iterate until the error is less than 1e-8 of the object */
            /* distance.  This corresponds to an error of about .002 arcsec */
            /* in the actual position (with the '+ .01' allowing for */
            /* some margin for very close objects,  such as artsats). */
            /*   Assume a maximum of ten iterations,  just to be safe */
   while( sqrt( diff_squared) > 1.e-8 * (obs2->r + .01) && max_iterations--)
      {
      double delta[4][3], discr;
      int pass;

      for( pass = 0; pass < 4; pass++)
         {
         double orbit2[6];
         const double h = 1.e-5;

         memcpy( orbit2, orbit, 6 * sizeof( double));
         if( pass)
            orbit2[(pass - 1) + 3] += h;
         integrate_orbit( orbit2, obs1->jd - obs1->r / AU_PER_DAY,
                                  obs2->jd - obs2->r / AU_PER_DAY);
         for( i = 0; i < 3; i++)
            orbit2[i] -= obs2->obj_posn[i];
         memcpy( delta[pass], orbit2, 3 * sizeof( double));
         if( pass)
            for( i = 0; i < 3; i++)
               delta[pass][i] = (delta[pass][i] - delta[0][i]) / h;
         }
      discr = eval_3x3_determinant( delta[1], delta[2], delta[3]);
      orbit[3] -= eval_3x3_determinant( delta[0], delta[2], delta[3]) / discr;
      orbit[4] -= eval_3x3_determinant( delta[1], delta[0], delta[3]) / discr;
      orbit[5] -= eval_3x3_determinant( delta[1], delta[2], delta[0]) / discr;
      diff_squared = 0.;
      for( i = 0; i < 3; i++)
         diff_squared += delta[0][i] * delta[0][i];
      if( debug_level > 3)
         debug_printf( "Transfer orbit: %d, %.3lg\n", max_iterations,
                        diff_squared);
      }
   if( max_iterations <= 0)
      return( -1);
               /* adjust for light-time lag: */
   r = -SOLAR_GM / (obs1->solar_r * obs1->solar_r * obs1->solar_r);
   for( i = 0; i < 3; i++)
      {
      const double time_lag = obs1->r / AU_PER_DAY;

      orbit[i] += time_lag * (orbit[3 + i] + orbit[i] * r * time_lag / 2.);
      orbit[i + 3] += orbit[i] * r * time_lag;
      }
   return( max_iterations <= 0 ? -1 : 0);
}

/* 'find_trial_orbit' tries to find an orbit linking the first and last
(included) observations in 'obs',  with the distance to the first object
being r1 AU and a radial velocity defined by 'angle_param'.

   First,  excluded observations at the beginning and end are skipped over
by advancing the obs pointer and/or decrementing n_obs.  If there are at
least two observations remaining,  we set the first observation to be at
distance r1.  Next,  we compute the distance in space between that point
and the ray defined by the second observation,  and we also compute the
maximum distance the object could go (assuming a parabolic orbit with
the object at escape velocity) during the time 'dt' between the two
observations.

   If the object can't get to the ray from the first observation without
going faster than escape velocity,  then we return an error code of -2.
This basically says,  "There are no non-hyperbolic orbits that satisfy
these two observations with the value you gave for r1.  Sorry."

   If the object _can_ get there,  we compute an orbit with an assumed
radial velocity linking the two observations.  If angle_param == -1,
the orbit will be one in which the object is at escape speed,  going
_toward_ us.  If angle_param == 1,  it'll be at escape speed,  going
_away_ from us.  In between,  you'll get assorted elliptical orbits.
(If angle_param > 1 or less than -1,  you'll get an hyperbolic orbit.)
*/

int find_sr_ranges( double *ranges, const double *q1, const double *p1,
                                    const double *q2, const double *p2,
                                    const double gm, const double dt);

int find_trial_orbit( double *orbit, OBSERVE FAR *obs, int n_obs,
                 const double r1, const double angle_param)
{
   int i, rval = 0, n_roots;
   double roots[10];

   while( n_obs && !obs->is_included)     /* skip excluded obs at */
      {                                   /* start of arc */
      n_obs--;
      obs++;
      }
   while( n_obs && !obs[n_obs - 1].is_included)    /* skip excluded obs at */
      n_obs--;                                     /* end of arc */
   n_roots = find_sr_ranges( roots,
                     obs[n_obs - 1].obs_posn, obs[n_obs - 1].vect,
                     obs[    0    ].obs_posn, obs[    0    ].vect,
                     SOLAR_GM, obs->jd - obs[n_obs - 1].jd);
#if 0
   n_roots = find_sr_ranges( roots, obs->obs_posn, obs->vect,
                     obs[n_obs - 1].obs_posn, obs[n_obs - 1].vect,
                     SOLAR_GM, obs[n_obs - 1].jd - obs->jd);
#endif
   debug_printf( "%d ranges\n", n_roots);
   for( i = 0; i < n_roots * 2; i++)
      debug_printf( "Root %d: %lf\n", i, roots[i]);
   if( n_obs < 2)
      rval = -1;
   else
      {
      double r2 = 0., dist2 = 0., escape_dist2;
      int i;
      OBSERVE FAR *endptr = obs + n_obs - 1;
      const double dt = endptr->jd - obs->jd;

      set_distance( obs, r1);
      for( i = 0; i < 3; i++)
         r2 += (obs->obj_posn[i] - endptr->obs_posn[i]) * endptr->vect[i];
      set_distance( endptr, r2);
      for( i = 0; i < 3; i++)
         {
         const double delta = endptr->obj_posn[i] - obs->obj_posn[i];

         dist2 += delta * delta;
         }
               /* Escape velocity for an object r AU from the sun would be */
               /* sqrt( 2 * SOLAR_GM / r).  We'll use the square of this:  */
      escape_dist2 = 2. * SOLAR_GM / obs->solar_r;
               /* ...and multiply by dt squared to get the square of the   */
               /* distance the object would travel if it's at the esc speed: */
      escape_dist2 *= dt * dt;
      if( escape_dist2 < dist2)     /* only hyperbolic orbits exist */
         rval = -2;
      else
         {
         set_distance( endptr, r2 + angle_param * sqrt( escape_dist2 - dist2));
         find_transfer_orbit( orbit, obs, endptr);
         set_locs( orbit, obs->jd, obs, n_obs);
         if( n_obs > 2)
            adjust_herget_results( obs, n_obs, orbit);
         }
      }
   return( rval);
}

#define RAD2SEC (180. * 3600. / PI)

void set_obs_vect( OBSERVE FAR *obs);        /* mpc_obs.h */

int adjust_herget_results( OBSERVE FAR *obs, int n_obs, double *orbit)
{
   int i, n_found = 0, rval = -1, idx1, idx2;
   double avg_x2 = 0., avg_x = 0., avg_xt = 0., avg_t = 0.;
   double avg_y2 = 0., avg_y = 0., avg_yt = 0., avg_t2 = 0.;
// FILE *debug_file = fopen( "debug.dat", "wb");

   if( get_idx1_and_idx2( n_obs, obs, &idx1, &idx2) < 3)
      return( -2);
   obs += idx1;
   n_obs = idx2 - idx1 + 1;
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         double dx = obs[i].computed_ra - obs[i].ra;
         double dy = obs[i].computed_dec - obs[i].dec;
         double dt = obs[i].jd - obs[0].jd;

         avg_x2 += dx * dx;
         avg_y2 += dy * dy;
         avg_xt += dx * dt;
         avg_yt += dy * dt;
         avg_x += dx;
         avg_y += dy;
         avg_t += dt;
         avg_t2 += dt * dt;
         n_found++;
         }

   if( n_found)
      {
      double determ;

      avg_x2 /= (double)n_found;
      avg_y2 /= (double)n_found;
      avg_xt /= (double)n_found;
      avg_yt /= (double)n_found;
      avg_x /= (double)n_found;
      avg_y /= (double)n_found;
      avg_t /= (double)n_found;
      avg_t2 /= (double)n_found;
//    fprintf( debug_file, "avg_x2 = %lf   avg_y2 = %lf\n",
//                avg_x2 * RAD2SEC * RAD2SEC, avg_y2 * RAD2SEC * RAD2SEC);
//    fprintf( debug_file, "avg_x = %lf   avg_y = %lf\n",
//                avg_x * RAD2SEC, avg_y * RAD2SEC);
      determ = avg_t2 - avg_t * avg_t;
      if( determ)
         {
         double ax = (avg_xt - avg_x * avg_t) / determ;
         double bx = (avg_t2 * avg_x - avg_t * avg_xt) / determ;
         double ay = (avg_yt - avg_y * avg_t) / determ;
         double by = (avg_t2 * avg_y - avg_t * avg_yt) / determ;
         OBSERVE start = obs[0];
         OBSERVE end = obs[n_obs - 1];

         start.ra  = start.computed_ra - bx;
         end.ra    = end.computed_ra - (bx + (end.jd - start.jd) * ax);
         start.dec = start.computed_dec - by;
         end.dec   = end.computed_dec - (by + (end.jd - start.jd) * ay);
//       fprintf( debug_file, "Shift at start: %lf, %lf\n",
//                bx * RAD2SEC, by * RAD2SEC);
//       fprintf( debug_file, "Shift at end: %lf, %lf\n",
//                (bx + (end.jd - start.jd) * ax) * RAD2SEC,
//                (by + (end.jd - start.jd) * ay) * RAD2SEC);
         set_obs_vect( &start);
         set_obs_vect( &end);
         set_distance( &start, start.r);
         set_distance( &end, end.r);
         find_transfer_orbit( orbit, &start, &end);
         set_locs( orbit, start.jd, obs, n_obs);
         rval = 0;
         }
      }
// fclose( debug_file);
   return( rval);
}

         /* Don't attempt to use the Herget method over a time span  */
         /* greater than 100 days... a somewhat arbitrary limit;  it */
         /* really ought to be lower for orbits closer to the sun,   */
         /* larger for Centaur/TNO-type objects                      */

int herget_method( OBSERVE FAR *obs, int n_obs, double r1, double r2,
         double *orbit, double *d_r1, double *d_r2, const char *limited_orbit)
{
   double *xresid, *yresid, *dx_dr1, *dx_dr2, *dy_dr1, *dy_dr2;
   double delta, a = 0., b = 0., c = 0., e = 0., f = 0., determ;
   int i, n_real_obs, using_pseudo_vaisala = (r1 < 0.);
   double orbit2[6];
   double orbit_offset[6], *constraint;
   int planet_orbiting, n_constraints = 0, idx1, idx2;
   char tstr[80];

   if( limited_orbit && !*limited_orbit)
      limited_orbit = NULL;

   n_real_obs = get_idx1_and_idx2( n_obs, obs, &idx1, &idx2);
   if( n_real_obs < 2)        /* should never happen */
      {
      debug_printf( "??? n_obs %d, idx1 %d, idx2 %d, n_real_obs = %d\n",
                     n_obs, idx1, idx2, n_real_obs);
      return( -1);
      }
   obs += idx1;
   n_obs = idx2 - idx1 + 1;

   if( using_pseudo_vaisala)
      {
      r2 = find_r_given_solar_r( obs + n_obs - 1, -r1);
      r1 = find_r_given_solar_r( obs, -r1);
      if( debug_level > 7)
         debug_printf( "r1 = %lf; r2 = %lf\n", r1, r2);
      if( r1 < 0. || r2 < 0.)
         return( 1);
      if( d_r1)
         *d_r1 = r1;
      if( d_r2)
         *d_r2 = r2;
      }
   set_distance( obs, r1);
   set_distance( obs + n_obs - 1, r2);
   runtime_message = tstr;
   strcpy( tstr, "H/xfer orbit (1)");
   if( find_transfer_orbit( orbit, obs, obs + n_obs - 1))
      {
      runtime_message = NULL;
      return( -2);
      }
   strcpy( tstr, "H/set_locs (1)");
   set_locs( orbit, obs[0].jd, obs, n_obs);
   runtime_message = NULL;
   if( !d_r1 || !d_r2 || using_pseudo_vaisala)
      return( 0);

   *d_r1 = *d_r2 = 0.;
   if( n_real_obs == 2)
      return( 0);       /* good as done... */

   xresid = (double *)calloc( 6 * (n_obs + MAX_CONSTRAINTS), sizeof( double));
   if( !xresid)
      return( -3);
   yresid = xresid + n_obs + MAX_CONSTRAINTS;
   dx_dr1 = yresid + n_obs + MAX_CONSTRAINTS;
   dx_dr2 = dx_dr1 + n_obs + MAX_CONSTRAINTS;
   dy_dr1 = dx_dr2 + n_obs + MAX_CONSTRAINTS;
   dy_dr2 = dy_dr1 + n_obs + MAX_CONSTRAINTS;

   if( limited_orbit)
      {
      planet_orbiting = find_best_fit_planet( obs->jd, orbit, orbit2);
      for( i = 0; i < 6; i++)
         orbit_offset[i] = orbit[i] - orbit2[i];
      constraint = xresid + n_obs;
      n_constraints = evaluate_limited_orbit( orbit2, planet_orbiting,
                                       obs->jd, limited_orbit, constraint);
      }

   for( i = 0; i < n_obs; i++)
      {
      xresid[i] = obs[i].computed_ra - obs[i].ra;
      yresid[i] = obs[i].computed_dec - obs[i].dec;
      }

   delta = r1 / 10000.;
   if( delta > .1) delta = .1;
   set_distance( obs, r1 + delta);
   runtime_message = tstr;
   strcpy( tstr, "H/xfer orbit (2)");
   find_transfer_orbit( orbit2, obs, obs + n_obs - 1);
   strcpy( tstr, "H/set_locs (2)");
   set_locs( orbit2, obs[0].jd, obs, n_obs);
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         double dx = obs[i].computed_ra - obs[i].ra;
         double dy = obs[i].computed_dec - obs[i].dec;

         dx_dr1[i] = (dx - xresid[i]) / delta;
         dy_dr1[i] = (dy - yresid[i]) / delta;
         }

   if( limited_orbit)
      {
      double constraint2[MAX_CONSTRAINTS];

      for( i = 0; i < 6; i++)
         orbit2[i] -= orbit_offset[i];
      evaluate_limited_orbit( orbit2, planet_orbiting, obs->jd,
                                limited_orbit, constraint2);
      for( i = 0; i < n_constraints; i++)
         {
         dx_dr1[n_obs + i] = (constraint2[i] - constraint[i]) / delta;
         dy_dr1[n_obs + i] = 0.;
         }
      }

   delta = r2 / 10000.;
   if( delta > .1) delta = .1;
   set_distance( obs, r1);
   set_distance( obs + n_obs - 1, r2 + delta);
   strcpy( tstr, "H/xfer orbit (3)");
   find_transfer_orbit( orbit2, obs, obs + n_obs - 1);
   strcpy( tstr, "H/set_locs (3)");
   set_locs( orbit2, obs[0].jd, obs, n_obs);
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         double dx = obs[i].computed_ra - obs[i].ra;
         double dy = obs[i].computed_dec - obs[i].dec;

         dx_dr2[i] = (dx - xresid[i]) / delta;
         dy_dr2[i] = (dy - yresid[i]) / delta;
         }

   if( limited_orbit)
      {
      double constraint2[MAX_CONSTRAINTS];

      for( i = 0; i < 6; i++)
         orbit2[i] -= orbit_offset[i];
      evaluate_limited_orbit( orbit2, planet_orbiting, obs->jd,
                                limited_orbit, constraint2);
      for( i = 0; i < n_constraints; i++)
         {
         dx_dr2[n_obs + i] = (constraint2[i] - constraint[i]) / delta;
         dy_dr2[n_obs + i] = 0.;
         }
      }

                    /* OK,  we now have all values & derivatives needed... */
   for( i = 0; i < n_obs + n_constraints; i++)
      if( obs[i].is_included || i >= n_obs)
         {
         c += xresid[i] * dx_dr1[i] + yresid[i] * dy_dr1[i];
         a += dx_dr1[i] * dx_dr1[i] + dy_dr1[i] * dy_dr1[i];
         b += dx_dr1[i] * dx_dr2[i] + dy_dr1[i] * dy_dr2[i];

         f += xresid[i] * dx_dr2[i] + yresid[i] * dy_dr2[i];
         /*  d = b;  */
         e += dx_dr2[i] * dx_dr2[i] + dy_dr2[i] * dy_dr2[i];
         }

   free( xresid);
   determ = a * e - b * b;
   *d_r1 = -(e * c - b * f) / determ;
   *d_r2 = -(a * f - c * b) / determ;
   if( *d_r1 > r1 / 3.) *d_r1 = r1 / 3.;
   if( *d_r1 <-r1 / 3.) *d_r1 = -r1 / 3.;
   if( *d_r2 > r2 / 3.) *d_r2 = r2 / 3.;
   if( *d_r2 <-r2 / 3.) *d_r2 = -r2 / 3.;
   runtime_message = NULL;
   return( 0);
}

static int setup_parabolic( const double *iparams, double *orbit)
{
   double r = 0., escape_vel;
   int i;

   for( i = 0; i < 3; i++)
      {
      orbit[i] = iparams[i];
      r += iparams[i] * iparams[i];
      }
   r = sqrt( r);
   escape_vel = SQRT_2 * GAUSS_K / sqrt( r);
   orbit[3] = escape_vel * cos( iparams[3]) * cos( iparams[4]);
   orbit[4] = escape_vel * sin( iparams[3]) * cos( iparams[4]);
   orbit[5] = escape_vel *                    sin( iparams[4]);
   return( 0);
}

void improve_parabolic( OBSERVE FAR *obs, int n_obs, double *orbit,
                                                              double epoch)
{
   void *lsquare = lsquare_init( 5);
   double *xresids = (double *)calloc( 2 * n_obs + 10 * n_obs, sizeof( double));
   double *yresids = xresids + n_obs;
   double *slopes = yresids + n_obs;
   double params2[5], params[5], differences[5];
   const double delta_val = .0001;
   double v2 = 0.;
   int i, j;

   memcpy( params, orbit, 3 * sizeof( double));
   params[3] = atan2( orbit[4], orbit[3]);
   for( i = 3; i < 6; i++)
      v2 += orbit[i] * orbit[i];
   params[4] = asin( orbit[5] / sqrt( v2));
   setup_parabolic( params, orbit);

   set_locs( orbit, epoch, obs, n_obs);
   for( i = 0; i < n_obs; i++)
      {
      xresids[i] = obs[i].computed_ra - obs[i].ra;
      yresids[i] = obs[i].computed_dec - obs[i].dec;
      }

   for( i = 0; i < 5; i++)
      {
      memcpy( params2, params, 5 * sizeof( double));
      params2[i] = params[i] - delta_val;
      setup_parabolic( params2, orbit);
      set_locs( orbit, epoch, obs, n_obs);
      for( j = 0; j < n_obs; j++)
         {
         slopes[i + j * 10] = obs[j].computed_ra;
         slopes[i + j * 10 + 5] = obs[j].computed_dec;
         }

      params2[i] = params[i] + delta_val;
      setup_parabolic( params2, orbit);
      set_locs( orbit, epoch, obs, n_obs);
      for( j = 0; j < n_obs; j++)
         {
         slopes[i + j * 10] -= obs[j].computed_ra;
         slopes[i + j * 10 + 5] -= obs[j].computed_dec;
         slopes[i + j * 10] /= 2. * delta_val;
         slopes[i + j * 10 + 5] /= 2. * delta_val;
         }
      }

   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         lsquare_add_observation( lsquare, xresids[i], 1., slopes + i * 10);
         lsquare_add_observation( lsquare, yresids[i], 1., slopes + i * 10 + 5);
         }

   free( xresids);
   lsquare_solve( lsquare, differences);
   lsquare_free( lsquare);

   for( i = 0; i < 5; i++)
      params[i] += differences[i];
   setup_parabolic( params, orbit);
   set_locs( orbit, epoch, obs, n_obs);
}

static int evaluate_limited_orbit( const double *orbit,
                    const int planet_orbiting, const double epoch,
                    const char *limited_orbit, double *constraints)
{
   int rval = 0;

   if( limited_orbit)
      {
      ELEMENTS elem;
      extern double planet_mass[];

      calc_classical_elements( &elem, orbit, epoch, 1,
                              SOLAR_GM * planet_mass[planet_orbiting]);
      while( *limited_orbit && limited_orbit[1] == '=')
         {
         double value = atof( limited_orbit + 2);
         char variable = *limited_orbit;

         while( *limited_orbit && *limited_orbit != ',')
            limited_orbit++;
         if( limited_orbit[-1] == 'k')
            value /= AU_IN_KM;
         switch( variable)
            {
            case 'q':
               constraints[rval] = elem.major_axis * (1. - elem.ecc) - value;
               rval++;
               break;
            case 'Q':
               constraints[rval] = elem.major_axis * (1. + elem.ecc) - value;
               rval++;
               break;
            case 'e':
               if( value)
                  constraints[rval++] = elem.ecc - value;
               else        /* handle e=0 (circular) orbits separately: */
                  {
                  constraints[rval++] = orbit[0] * orbit[3] +
                              orbit[1] * orbit[4] + orbit[2] * orbit[5];
                  constraints[rval++] = sqrt( orbit[0] * orbit[0] +
                               orbit[1] * orbit[1] + orbit[2] * orbit[2])
                               - elem.major_axis;
                  }
               break;
            case 'i':
               constraints[rval++] = elem.incl * 180. / PI - value;
               break;
            case 'P':         /* convert to a major axis */
               if( limited_orbit[-1] == 'd')    /* convert from days to yrs */
                  value /= 365.25;
               if( limited_orbit[-1] == 'h')    /* convert from hrs to yrs */
                  value /= 365.25 * 24.;
               if( limited_orbit[-1] == 'm')    /* convert from mins to yrs */
                  value /= 365.25 * 1440.;
               value = pow( value * sqrt( planet_mass[planet_orbiting]),
                                                     2. / 3.);
                           /* then _don't_ break; just fall through to the */
                           /* major axis code:                             */
            case 'a':
               constraints[rval++] = 1. / elem.major_axis - 1. / value;
               break;
            case 'n':
               value = 360. / value;         /* now value = period in days */
               value /= 365.25;              /* now value = period in years */
               value = pow( value * sqrt( planet_mass[planet_orbiting]),
                                                     2. / 3.);
               constraints[rval++] = 1. / elem.major_axis - 1. / value;
               break;
            case 'A':            /* area/mass ratio */
               if( n_extra_params == 1)
                  constraints[rval++] =
                             solar_pressure[0] * SOLAR_GM / SRP1AU - value;
               break;
            case 'K':
               {
               extern double comet_magnitude_slope_param;

               comet_magnitude_slope_param = value;
               }
               break;
            case 'G':
               {
               extern double asteroid_magnitude_slope_param;

               asteroid_magnitude_slope_param = value;
               }
               break;
            }
         if( *limited_orbit == ',')
            limited_orbit++;
         }
      }
   return( rval);
}

static void compute_unit_vectors( const double *velocity,
         double *forward, double *sideways, double *up)
{
   const double speed0 = sqrt( velocity[0] * velocity[0]
                             + velocity[1] * velocity[1]);
   const double speed = sqrt( speed0 * speed0
                             + velocity[2] * velocity[2]);
   int i;

   for( i = 0; i < 3; i++)
      forward[i] = velocity[i] / speed;
   sideways[0] = -velocity[1] / speed0;
   sideways[1] =  velocity[0] / speed0;
   sideways[2] = 0.;
   up[0] = forward[1] * sideways[2] - forward[2] * sideways[1];
   up[1] = forward[2] * sideways[0] - forward[0] * sideways[2];
   up[2] = forward[0] * sideways[1] - forward[1] * sideways[0];
}

#define MAX_N_PARAMS 9


int full_improvement( OBSERVE FAR *obs, int n_obs, double *orbit,
                 const double epoch, const char *limited_orbit)
{
   const int n_params = 6 + n_extra_params;
   void *lsquare = lsquare_init( n_params);
   double FAR *xresids;
   double FAR *yresids;
   double FAR *slopes;
   double constraint_slope[MAX_CONSTRAINTS * MAX_N_PARAMS];
   double orbit2[6], differences[10];
   double orbit_offset[6], working_epoch;
   double unit_vectors[3][3];
   double constraint[MAX_CONSTRAINTS];
   int planet_orbiting, n_constraints = 0;
   int i, j, n_skipped_obs = 0;
   const int n_total_obs = n_obs;
   const char *covariance_filename = "covar.txt";
   char tstr[80];
   const int use_symmetric_derivatives =
                      atoi( get_environment_ptr( "SYMMETRIC"));
   const int showing_deltas_in_debug_file =
                      atoi( get_environment_ptr( "DEBUG_DELTAS"));

   if( get_idx1_and_idx2( n_obs, obs, &i, &j) < 3)
      return( -1);

   sprintf( tstr, "full improvement: %lf  ", JD_TO_YEAR( epoch));
   runtime_message = tstr;
   compute_unit_vectors( orbit + 3, unit_vectors[0],
                                    unit_vectors[1], unit_vectors[2]);
   for( i = 0; i < n_obs; i++)
      {
      obs[i].computed_ra  = obs[i].ra;
      obs[i].computed_dec = obs[i].dec;
      }

               /* Drop unincluded observations from the start of the arc: */
   while( n_obs && !obs->is_included)
      {
      obs++;
      n_obs--;
      n_skipped_obs++;
      }
               /* ... and then from the end of the arc: */
   while( n_obs && !obs[n_obs - 1].is_included)
      n_obs--;
               /* We can minimize roundoff errors by using a "working  */
               /* epoch" at the center of the arc,  if there are no    */
               /* constraints.  If there are,  we might be constraining */
               /* (say) e=.8 at the working epoch,  instead of the one  */
               /* we really want. */
   if( limited_orbit && !*limited_orbit)
      limited_orbit = NULL;

   if( limited_orbit)
      working_epoch = epoch;
   else
      working_epoch = (obs[0].jd + obs[n_obs - 1].jd) / 2.;
   integrate_orbit( orbit, epoch, working_epoch);
   if( n_obs < 3)
      ;

   if( limited_orbit)
      {
      planet_orbiting = find_best_fit_planet( working_epoch, orbit, orbit2);
      for( i = 0; i < 6; i++)
         orbit_offset[i] = orbit[i] - orbit2[i];
      n_constraints = evaluate_limited_orbit( orbit2, planet_orbiting,
                               working_epoch, limited_orbit, constraint);
      }

   xresids = (double FAR *)FCALLOC( (2 + 2 * n_params) * n_obs + n_params, sizeof( double));
   yresids = xresids + n_obs;
   slopes = yresids + n_obs;

   sprintf( tstr, "fi/setting locs: %lf  ", JD_TO_YEAR( working_epoch));
   set_locs( orbit, working_epoch, obs, n_obs);
   sprintf( tstr, "fi/locs set: %lf  ", JD_TO_YEAR( working_epoch));
   for( i = 0; i < n_obs; i++)
      {
      xresids[i] = obs[i].computed_ra - obs[i].ra;
      yresids[i] = obs[i].computed_dec - obs[i].dec;
      }

   for( i = 0; i < n_params; i++)
      {
      static double delta_vals[9] =
                 { 1e-8, 1e-8, 1e-8, 1e-10, 1e-10, 1e-10, .0001, .001, .001 };
      const double delta_val = delta_vals[i];
      double worst_error_squared = 0, worst_error_in_arcseconds;

      memcpy( orbit2, orbit, 6 * sizeof( double));
      if( i < 3)
         for( j = 0; j < 3; j++)
            orbit2[j] -= unit_vectors[i][j] * delta_val;
      else if( i < 6)
         for( j = 0; j < 3; j++)
            orbit2[j + 3] -= unit_vectors[i - 3][j] * delta_val;
      if( i >= 6)
         solar_pressure[i - 6] -= delta_val;
      sprintf( tstr, "Evaluating %d of %d    ", i + 1, n_params);
      set_locs( orbit2, working_epoch, obs, n_obs);
      for( j = 0; j < n_obs; j++)
         {
         slopes[i +   2 * j     * n_params] = obs[j].computed_ra;
         slopes[i + (2 * j + 1) * n_params] = obs[j].computed_dec;
         }

      for( j = 0; j < 6; j++)
         orbit2[j] = 2. * orbit[j] - orbit2[j];
      if( i >= 6)
         solar_pressure[i - 6] += 2. * delta_val;
      if( use_symmetric_derivatives)
         {
         sprintf( tstr, "Evaluating %d of %d rev   ", i + 1, n_params);
         set_locs( orbit2, working_epoch, obs, n_obs);
         }
      else
         for( j = 0; j < n_obs; j++)
            {
            const double orig_computed_ra  = obs[j].ra  + xresids[j];
            const double orig_computed_dec = obs[j].dec + yresids[j];

            obs[j].computed_ra  = 2. * orig_computed_ra  - obs[j].computed_ra;
            obs[j].computed_dec = 2. * orig_computed_dec - obs[j].computed_dec;
            }

      for( j = 0; j < n_obs; j++)
         {
         double *slope_ptr = slopes + i + 2 * j * n_params;
         double error_squared;

         slope_ptr[0]        -= obs[j].computed_ra;
         if( slope_ptr[0] > PI)
            slope_ptr[0] -= PI + PI;
         if( slope_ptr[0] < -PI)
            slope_ptr[0] += PI + PI;
         slope_ptr[n_params] -= obs[j].computed_dec;
         error_squared = slope_ptr[0] * slope_ptr[0] +
                     slope_ptr[n_params] * slope_ptr[n_params];
         if( worst_error_squared < error_squared)
            worst_error_squared = error_squared;
         slope_ptr[0]        /= 2. * delta_val;
         slope_ptr[n_params] /= 2. * delta_val;
         }
      worst_error_in_arcseconds =
                 sqrt( worst_error_squared) * 3600. * (180. / PI);
      if( showing_deltas_in_debug_file)
         debug_printf( "Total change on param %d: %lf arcseconds; delta %.3e\n",
            i, worst_error_in_arcseconds, delta_val);
                     /* Attempt to keep the error at 1.5 arcsecs: */
      delta_vals[i] *= 1.5 / worst_error_in_arcseconds;
      if( limited_orbit)
         {
         double constraint2[MAX_CONSTRAINTS];

         for( j = 0; j < 6; j++)
            orbit2[j] -= orbit_offset[j];
         evaluate_limited_orbit( orbit2, planet_orbiting, working_epoch,
                                   limited_orbit, constraint2);
         for( j = 0; j < n_constraints; j++)
            constraint_slope[i + j * n_params] =
                     (constraint[j] - constraint2[j]) / delta_val;
         }
      if( i >= 6)         /* put solar pressure back where it was: */
         solar_pressure[i - 6] -= delta_val;
      }

// runtime_message = NULL;
   for( i = 0; i < n_obs; i++)
      if( obs[i].is_included)
         {
         double loc_vals[22];

         FMEMCPY( loc_vals, slopes + i * 2 * n_params,
                                         2 * n_params * sizeof( double));
         lsquare_add_observation( lsquare, xresids[i],
                                          obs[i].weight, loc_vals);
         lsquare_add_observation( lsquare, yresids[i],
                                          obs[i].weight, loc_vals + n_params);
         }

   if( limited_orbit)
      for( j = 0; j < n_constraints; j++)
         lsquare_add_observation( lsquare, constraint[j], 1.,
                                            constraint_slope + j * n_params);

   FFREE( xresids);
   if( *covariance_filename)
      {
      FILE *ofile = fopen( covariance_filename, "wb");
      double *matrix = lsquare_covariance_matrix( lsquare);
      double eigen[10];
      int pass;

      for( pass = 0; pass < 2; pass++)
         {
         fprintf( ofile, pass ? "Correlation:\n" : "Covariance:\n");
         for( i = 0; i < n_params; i++)
            {
            for( j = 0; j < n_params; j++)
               {
               double oval = matrix[i + j * n_params];

               if( pass)
                  oval /= sqrt( matrix[i * (n_params + 1)] * matrix[j * (n_params + 1)]);
               fprintf( ofile, pass ? "%10.7lf " : "%12.3lg", oval);
               }
            fprintf( ofile, "\n");
            }
         }
      eigen[0] = 1.;
      for( i = 1; i < n_params; i++)
         eigen[i] = 0.;
      for( pass = 0; pass < 10; pass++)
         {
         double eigen2[10], len2 = 0., len, delta2 = 0.;

         for( i = 0; i < n_params; i++)
            {
            eigen2[i] = 0.;
            for( j = 0; j < n_params; j++)
               eigen2[i] += eigen[j] * matrix[j + i * n_params];
            len2 += eigen2[i] * eigen2[i];
            }
         len = sqrt( len2);
         fprintf( ofile, "\n");
         for( i = 0; i < n_params; i++)
            {
            const double new_val = eigen2[i] / len;

            delta2 += (eigen[i] - new_val) * (eigen[i] - new_val);
            eigen[i] =  new_val;
            fprintf( ofile, "%13.7lg", eigen[i]);
            }
         fprintf( ofile, "\nLen = %.3lg; Delta = %.3lg",
                                       len, sqrt( delta2));
         if( delta2 < 1.e-16)    /* i.e.,  delta < 1.e-8                */
            {
            pass = 10;           /* time to break out;  we've converged */
            fprintf( ofile, "\n");
            for( i = 0; i < 6; i++)
               fprintf( ofile, "%13.7lg", orbit[i]);
            }
         }
      fclose( ofile);
      free( matrix);
      }
   lsquare_solve( lsquare, differences);
   lsquare_free( lsquare);
   for( i = 0; i < n_params; i++)
      {
      const double max_difference = (obs->r > 1. ? .1 : obs->r * .1);

      if( differences[i] > max_difference)
         differences[i] = max_difference;
      if( differences[i] < -max_difference)
         differences[i] = -max_difference;
      if( i < 3)
         for( j = 0; j < 3; j++)
            orbit[j] += unit_vectors[i][j] * differences[i];
      else if( i < 6)
         for( j = 0; j < 3; j++)
            orbit[j + 3] += unit_vectors[i - 3][j] * differences[i];
      if( i >= 6)
         solar_pressure[i - 6] += differences[i];
      }

   sprintf( tstr, "Final setting of orbit    ");
   if( setting_outside_of_arc)
      set_locs( orbit, working_epoch, obs - n_skipped_obs, n_total_obs);
   else
      set_locs( orbit, working_epoch, obs, n_obs);
   strcpy( tstr, "Return to correct epoch    ");
   integrate_orbit( orbit, working_epoch, epoch);
   runtime_message = NULL;
   return( 0);
}

#define MAX_INITIAL_SPAN 150.

static inline double dot_product( const double *a, const double *b)
{
   return( a[0] * b[0] + a[1] * b[1] + a[2] * b[2]);
}

/* 'score_orbit_arc' basically looks at a series of observations and
assigns a 'score',  in which having a long arc and no really long gaps
in it results in a higher (better) score.  It used to just look at how
long the arc was.  But having decent "fill" during the arc is important,
too.  If you're given two observations mere seconds apart,  plus one a week
later,  that's not as good as having three spaced a day apart each.  There
are other considerations,  too,  such as how much angle the observations
span,  and they really ought to be included.  But at least right now,
they aren't.  */

static inline double score_orbit_arc( const OBSERVE FAR *obs, const int n_obs)
{
   double longest_omission = 0.;
   double arc_length = obs[n_obs - 1].jd - obs[0].jd;
   int i, j;

   for( i = 0; i < n_obs - 1; i++)
      if( obs[i].is_included)
         {
         for( j = i + 1; j < n_obs && !obs[j].is_included; j++)
            ;
         if( j < n_obs)
            if( longest_omission < obs[j].jd - obs[i].jd)
               longest_omission = obs[j].jd - obs[i].jd;
         }
   return( arc_length - longest_omission * .9999);
}

/* When looking for subarcs,  we want to look just for those that are less
than 30 degrees long.  Longer than that,  and the usual initial orbit
methods (Gauss,  Herget) may diverge.  (Not necessarily -- in fact,
they'll often still work with much longer arcs -- but 30 degrees means
you can be pretty confident that a decent orbit will be found.)  A quick
dot-product of the unit vectors,  compared to cos(30 degrees) =
sqrt(3) / 2.,  suffices to check the arc length. */

static inline void look_for_best_subarc( const OBSERVE FAR *obs,
       const int n_obs, const double max_arc_len, int *start, int *end)
{
   double best_score = 0., score;
   const double cos_30_deg = 1.7320508 / 2.;
   int i, j;

   for( i = j = 0; i < n_obs - 1; i++)
      {
      while( j < n_obs - 1 && obs[j + 1].jd - obs[i].jd < max_arc_len
                  && dot_product( obs[i].vect, obs[j + 1].vect) > cos_30_deg)
         j++;
      score = score_orbit_arc( obs + i, j - i + 1);
      if( score > best_score)
         {
         best_score = score;
         *start = i;
         *end = j;
         }
      }
}

/* The following was created by plotting semimajor axes versus
inclinations as a scatterplot,  from the recent 'mpcorb.dat' file.
The result is a 30x60 graph,  with 30 vertical bins representing
2 degrees each in inclination (from incl=0 at the top to incl=60
at the bottom),  and 60 bins across representing .1 AU in semimajor
axis (from 0 AU to 6 AU).  The natural logarithm of the counts in
each bin are shown;  those ranged from zero to 9,  so I didn't
need to do any scaling.  This basically reflects the scatterplot
provided by MPC at http://www.cfa.harvard.edu/iau/plot/OrbEls51.gif
(except that the vertical axis is flipped).   */

/*           0 AU      1         2         3         4         5         6 */
static const char *incl_vs_a_scattergram[30] = {
/* incl=0*/ "000000012222232223333778877777776331002520000000001332000000",
            "000000112333233333334789988888886331202630100000002442000000",
            "000000112223333233334799888876776332111520000000002442000000",
            "000000022233333333333699888876776342111520010000002442000000",
            "000000011222233233333577787877886443011510000000002442000000",
/* 10 deg*/ "000000011222223323332357678868886443101410000010001442000000",
            "000000012223332232222246689866776331000410000000002441000000",
            "000000012222323222332124688766776331100310000000001340000000",
            "000000002222222223462222466655786331011200000000001341000000",
            "000000012122223223562233355544675332000100000000000431000000",
/* 20 deg*/ "000000011122232223562255456433565210010100000000001331000000",
            "000000111222222123662366555423565210100100000000000331000000",
            "000000011122223222562356444533464100000000000000001330000000",
            "000000012112212222442244355422464100000000000000000321000000",
            "000000011112122122231222156421353110000000000000000321000000",
/* 30 deg*/ "000000011112111122221111245410132000000000000000000230000000",
            "000000011110011212211111135410122000000000000000000220000000",
            "000000001111211221221120033320011100000000000000000120000000",
            "000000000112111211201110122310000000000000000000000110000000",
            "000000000011122212201110111110000000000000000000000000000000",
/* 40 deg*/ "000000001101111121111110101100001000000000000000000000000000",
            "000000000011010001101110000001000000000000000000000000000000",
            "000000000001100001101010010100000000000000000000000000000000",
            "000000000000011011100110010000000000000000000000000000000000",
            "000000000100100000000000000000000000000000000000000000000000",
/* 50 deg*/ "000000001000100100100000000000000000000000000000000000000000",
            "000000000000100011010100000000000000000000000000000000000000",
            "000000000000011000110000000000000000000000000000000000000000",
            "000000000000010000000011000000000000000000000000000000000000",
            "000000000000000000000000000000000000000000000000000000000000" };

/* evaluate_initial_orbit( ) is supposed to give a "score" of sorts,      */
/* describing just how likely this orbit seems to be,  given its rms      */
/* errors (lower is better);  eccentricity (same,  with highly hyperbolic */
/* solutions considered very unlikely and therefore bumping up the return */
/* value);  inclination (anything above .5 radians,  or about 30 degrees, */
/* is considered unlikely).  Also,  main-belt objects (based on a) are    */
/* slightly encouraged.                                                   */

double evaluate_initial_orbit( const OBSERVE FAR *obs,
                              const int n_obs, const double *orbit)
{
   extern double planet_mass[];
   double rms_err = compute_rms( obs, n_obs, 1), rval, rel_orbit[6];
   ELEMENTS elem;
   int planet_orbiting = find_best_fit_planet( obs->jd,
                                  orbit, rel_orbit);

   calc_classical_elements( &elem, rel_orbit, obs[0].jd, 1,
                              SOLAR_GM * planet_mass[planet_orbiting]);
   rval = rms_err + elem.ecc / 2.;
   if( !planet_orbiting)                  /* for heliocentric orbits... */
      {
      const int xbin = (int)( elem.major_axis * 10.);
      const int ybin = (int)( elem.incl * (180. / PI) / 2.);

//    if( elem.ecc > .5)                     /* discourage eccentric orbits */
//       rval += (elem.ecc - .5) * 2.;
      if( elem.ecc > 1.01)                /* _strongly_ discourage hyperbolics */
         rval += (elem.ecc - 1.01) * 1000.;
      if( elem.incl > .5)                 /* gently discourage high-incl and */
         rval += (elem.incl - .5) * .2;   /* retrograde orbits */
      if( xbin >= 0 && ybin >= 0 && xbin < 60 && ybin < 30)
         rval -= (double)( incl_vs_a_scattergram[ybin][xbin] - '0') * .1;
      }
   return( rval);
}

#if 0
double evaluate_initial_limited_orbit( const OBSERVE FAR *obs,
                              const int n_obs, const double *orbit,
                              const int planet_orbiting,
                              const char *limited_orbit)
{
}
#endif


#define EARTH_CLOSE_APPROACH .01

double initial_orbit( OBSERVE FAR *obs, int n_obs, double *orbit)
{
   int i, start, end, quit, rval = -3;
   int old_perturbers;
   double best_score = 0., score;
#ifndef _MSC_VER
   char msg_buff[80];
#endif

   for( i = 0; i < n_obs; i++)
      {
      obs[i].computed_ra  = obs[i].ra;
      obs[i].computed_dec = obs[i].dec;
      }

   while( n_obs && !obs->is_included)
      {
      obs++;
      n_obs--;
      }
   while( n_obs && !obs[n_obs - 1].is_included)
      n_obs--;
   if( n_obs < 2)
      return( -1);
   look_for_best_subarc( obs, n_obs, MAX_INITIAL_SPAN,
                     &start, &end);
   debug_printf( "Best arc: %d to %d\n", start, end);
   for( i = 0; i < start; i++)
      obs[i].is_included = 0;
   for( i = end + 1; i < n_obs; i++)
      obs[i].is_included = 0;
   obs += start;
   n_obs = end - start + 1;
   if( !orbit)                /* just setting the right arc length */
      return( 0);
   for( i = 0; i < n_obs; i++)      /* solely to ensure a non-zero r */
      obs[i].r = 1.;

   best_score = 1e+47;
   quit = 0;
   old_perturbers = perturbers;      /* temporarily switch to auto-perturb */
   perturbers = AUTOMATIC_PERTURBERS;
   if( n_obs >= 2)       /* default:  do things 'normally' */
      {
      double gauss_epoch, temp_orbit[6];
      int gauss_soln_used = 0;

#ifndef _MSC_VER
      if( show_runtime_messages)
         mvaddnstr( 14, 10, "In Gauss solution", -1);
#endif
      for( i = 0; i < 3; i++)
         {
         const double t_gauss_epoch =
                        convenient_gauss( obs, n_obs, temp_orbit, 1., i);

         if( debug_level)
            debug_printf( "Gauss epoch: JD %lf\n", t_gauss_epoch);
         if( t_gauss_epoch)
            {
            set_locs( temp_orbit, t_gauss_epoch, obs, n_obs);
            score = evaluate_initial_orbit( obs, n_obs, temp_orbit);
            if( debug_level > 2)
               debug_printf( "   Gauss score: %lf\n", score);
            if( score < best_score)
               {
               memcpy( orbit, temp_orbit, 6 * sizeof( double));
               rval = 0;
               best_score = score;
               gauss_soln_used = 1;
               gauss_epoch = t_gauss_epoch;
               }
            }
         }
#ifndef _MSC_VER
      if( show_runtime_messages)
         mvaddnstr( 14, 10, "Gauss done", -1);
#endif
      for( i = 0; i < 2 && !quit; i++)
         {
         int orbit_looks_reasonable = 1;
         double pseudo_r;

         if( i)          /* dist from observer (second) pass:  some ad hoc */
            {            /* code that says,  "for long arcs,  start farther */
                         /* from the observer".                             */
            pseudo_r = (obs[n_obs - 1].jd - obs[0].jd) / 500.;
            if( pseudo_r < .00001)     /* 1e-5 AU = 1490 km */
               pseudo_r = .00001;
            }
         else                  /* (first) Vaisala pass */
            pseudo_r = .05;

         while( pseudo_r < (i ? 5. : 100.) && orbit_looks_reasonable)
            {
            double pseudo_r_to_use;
            int herget_rval;

            if( i)                          /* 2nd pass, dist from observer */
               pseudo_r_to_use = pseudo_r;
            else                            /* 1st pass, dist from sun */
               pseudo_r_to_use = -(1. + pseudo_r);
            herget_rval = herget_method( obs, n_obs, pseudo_r_to_use,
                                 pseudo_r_to_use,
                                temp_orbit, NULL, NULL, NULL);
            if( herget_rval < 0)    /* herget method failed */
               score = 1.e+7;
            else if( herget_rval > 0)        /* vaisala method failed, */
               score = 9e+5;                 /* but we should keep trying */
            else
               score = evaluate_initial_orbit( obs, n_obs, temp_orbit);
            if( debug_level > 2)
               debug_printf( "%d, pseudo-r %lf: score %lf, herget rval %d\n",
                      i, pseudo_r, score, herget_rval);
            if( score < best_score)
               {
               memcpy( orbit, temp_orbit, 6 * sizeof( double));
               rval = 0;
               best_score = score;
               gauss_soln_used = 0;
               }
#ifndef _MSC_VER
            if( show_runtime_messages)
               {
               sprintf( msg_buff, "Method %d, r=%.4lf", i, pseudo_r);
               mvaddnstr( 14, 10, msg_buff, -1);
               }
#endif
            if( score > 1e+6)   /* usually means eccentricity > 100! */
               {
               orbit_looks_reasonable = 0;      /* should stop looking */
               if( debug_level > 2)
                  debug_printf( "%d: Flipped out at %lf\n", i, pseudo_r);
               }
            pseudo_r *= 1.2;
            }
         }
      if( gauss_soln_used)
         integrate_orbit( orbit, gauss_epoch, obs[0].jd);

      perturbers_automatically_found = 0;
      if( !rval && n_obs > 2)  /* see if an Herget step or two will help: */
         {
         int method;
         double curr_score;

#ifndef _MSC_VER
         if( show_runtime_messages)
            mvaddnstr( 14, 10, "Improving solution...        ", -1);
#endif
         set_locs( orbit, obs[0].jd, obs, n_obs);
                  /* perhaps the earth and moon should be included?  */
                  /* Just how close does this object come to us?     */
         curr_score = evaluate_initial_orbit( obs, n_obs, orbit);
         for( method = 0; method < 2; method++)
            {
            int significant_improvement_occurred = 1;
            int iter = 0;
            int max_iter = 5;

                        /* We're willing to try the Herget,  then full  */
                        /* step methods, five times... _if_ they result */
                        /* in real improvement,  and we mandate two     */
                        /* tries with both Herget and full step  */
            while( significant_improvement_occurred && iter++ < max_iter)
               {
               memcpy( temp_orbit, orbit, 6 * sizeof( double));
#ifndef _MSC_VER
               if( show_runtime_messages)
                  {
                  sprintf( msg_buff, "%d %s step: radii %lf, %lf",
                           i + 1, (method ? "full" : "Herget"),
                           obs[0].r, obs[n_obs - 1].r);
                  mvaddnstr( 14, 10, msg_buff, -1);
                  }
#endif
               if( !method)         /* doing an Herget step */
                  {
                  double r1 = obs[0].r, r2 = obs[n_obs - 1].r;
                  double d_r1, d_r2;

                  herget_method( obs, n_obs, r1, r2, temp_orbit, &d_r1, &d_r2, NULL);
                  r1 += d_r1;
                  r2 += d_r2;
                  herget_method( obs, n_obs, r1, r2, temp_orbit, NULL, NULL, NULL);
                  adjust_herget_results( obs, n_obs, temp_orbit);
                  }
               else        /* doing a full step */
                  full_improvement( obs, n_obs, temp_orbit, obs[0].jd, NULL);

               score = evaluate_initial_orbit( obs, n_obs, temp_orbit);
               if( debug_level > 2)
                  debug_printf( "Method %d, run %d: score %lf\n",
                                       method, iter, score);
                     /* If we didn't improve things by a score of .1, */
                     /* we might as well stop:                        */
               if( score > curr_score - .1 && iter > 2)
                  significant_improvement_occurred = 0;
               if( score < curr_score)
                  {
                  memcpy( orbit, temp_orbit, 6 * sizeof( double));
                  curr_score = score;
                  }
               }
            }
         }

      if( rval)
         herget_method( obs, n_obs, 1., 1., orbit, NULL, NULL, NULL);
      set_locs( orbit, obs[0].jd, obs, n_obs);
      }
// perturbers = old_perturbers;        /* restore perturbers, if any */
   perturbers = perturbers_automatically_found;
   return( obs[0].jd);    /* ...and return epoch = JD of first observation */
}
