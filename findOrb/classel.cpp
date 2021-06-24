#include <math.h>
#include "watdefs.h"
#include "afuncs.h"
#include "comets.h"

#define PI 3.141592653589793238462643383279502884197
#define SQRT_2 1.41421356

/* calc_classical_elements( ) will take a given state vector r at a time t,
   for an object orbiting a mass gm;  and will compute the orbital elements
   and store them in the elem structure.  Normally,  ref=1.  You can set
   it to 0 if you don't care about the angular elements (inclination,
   longitude of ascending node,  argument of perihelion).

   There is also some code for ref=2,  which is to provide backward
   compatibility to some older software I wrote (which I hope to get rid
   of eventually).  So stick to ref=0 or ref=1.  */

int DLL_FUNC calc_classical_elements( ELEMENTS *elem, const double *r,
                             const double t, const int ref, const double gm)
{
   const double *v = r + 3;
   double dist, h0, n0, inv_major_axis;
   double h[3], e[3];
   double v2, ecc, r_dot_v, perihelion_speed, gm_over_h0;
   double v_cross_h_multiplier = 1. / gm;
   int i;

   dist = r[0] * r[0] + r[1] * r[1] + r[2] * r[2];
   dist = sqrt( dist);
   h[0] = r[1] * v[2] - r[2] * v[1];
   h[1] = r[2] * v[0] - r[0] * v[2];
   h[2] = r[0] * v[1] - r[1] * v[0];
   n0 = h[0] * h[0] + h[1] * h[1];
   h0 = n0 + h[2] * h[2];
   n0 = sqrt( n0);
   h0 = sqrt( h0);

                        /* See Danby,  p 204-206,  for much of this: */
   if( ref & 1)
      {
      elem->incl = asine( n0 / h0);
      elem->asc_node = atan2( h[0], -h[1]);
      }
   v2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
   if( ref & 2)                  /* still needed for PERTURB */
      v_cross_h_multiplier = 1.;
   e[0] = (v[1] * h[2] - v[2] * h[1]) * v_cross_h_multiplier - r[0] / dist;
   e[1] = (v[2] * h[0] - v[0] * h[2]) * v_cross_h_multiplier - r[1] / dist;
   e[2] = (v[0] * h[1] - v[1] * h[0]) * v_cross_h_multiplier - r[2] / dist;
   ecc = 0.;
   for( i = 0; i < 3; i++)
      ecc += e[i] * e[i];
   elem->minor_to_major = sqrt( fabs( 1. - ecc));
   ecc = elem->ecc = sqrt( ecc);
   for( i = 0; i < 3; i++)
      e[i] /= ecc;
   inv_major_axis = 2. / dist - v2 / gm;
   gm_over_h0 = gm / h0;
   perihelion_speed = gm_over_h0 + sqrt( gm_over_h0 * gm_over_h0
               - inv_major_axis * gm);
   elem->q = h0 / perihelion_speed;
   if( inv_major_axis)
      {
      elem->major_axis = 1. / inv_major_axis;
      elem->t0 = elem->major_axis * sqrt( fabs( elem->major_axis) / gm);
      }
   r_dot_v = r[0] * v[0] + r[1] * v[1] + r[2] * v[2];
   if( ref & 1)
      {
      elem->arg_per = (h[0] * e[1] - h[1] * e[0]) / n0;
      if( elem->arg_per >= 1. || elem->arg_per <= -1.)
         elem->arg_per = ( elem->arg_per > 0. ? 0. : PI);
      else
         elem->arg_per = acos( elem->arg_per);
      if( e[2] < 0.)
         elem->arg_per = PI + PI - elem->arg_per;
      }

   if( h[2] < 0.)                   /* retrograde orbit */
      elem->incl = PI - elem->incl;

   if( inv_major_axis > 0.)         /* elliptical case */
      {
      double e_cos_E = 1. - dist * inv_major_axis;
      double e_sin_E = r_dot_v / sqrt( gm * elem->major_axis);
      double ecc_anom = atan2( e_sin_E, e_cos_E);

      elem->mean_anomaly = ecc_anom - ecc * sin( ecc_anom);
/*    elem->t0 = elem->major_axis * sqrt( elem->major_axis / gm);   */
      elem->perih_time = t - elem->mean_anomaly * elem->t0;
      }
   else if( inv_major_axis < 0.)         /* hyperbolic case */
      {
      double z = (1 - dist * inv_major_axis) / ecc;
      double f = log( z + sqrt( z * z - 1.));

      if( r_dot_v < 0.)
         f = -f;
      elem->mean_anomaly = ecc * sinh( f) - f;
      elem->perih_time = t - elem->mean_anomaly * fabs( elem->t0);
      h0 = -h0;
      }
   else              /* parabolic case */
      {
      double tau;

      tau = sqrt( dist / elem->q - 1.);
      if( r_dot_v < 0.)
         tau = -tau;
      elem->w0 = (3. / SQRT_2) / (elem->q * sqrt( elem->q / gm));
/*    elem->perih_time = t - tau * (tau * tau / 3. + 1) *                   */
/*                                      elem->q * sqrt( 2. * elem->q / gm); */
      elem->perih_time = t - tau * (tau * tau / 3. + 1) * 3. / elem->w0;
      }

/* In the past,  these were scaled;  but now,  I'd prefer to have them */
/* as unit-length vectors.  This matches assumptions in ASTFUNCS.CPP.  */
#if 0
   elem->perih_vec[0] = e[0] * elem->major_axis;
   elem->perih_vec[1] = e[1] * elem->major_axis;
   elem->perih_vec[2] = e[2] * elem->major_axis;
   scale = elem->major_axis / h0;
   elem->sideways[0] = (e[2] * h[1] - e[1] * h[2]) * scale;
   elem->sideways[1] = (e[0] * h[2] - e[2] * h[0]) * scale;
   elem->sideways[2] = (e[1] * h[0] - e[0] * h[1]) * scale;
#endif
   for( i = 0; i < 3; i++)
      elem->perih_vec[i] = e[i];
   elem->sideways[0] = (e[2] * h[1] - e[1] * h[2]) / h0;
   elem->sideways[1] = (e[0] * h[2] - e[2] * h[0]) / h0;
   elem->sideways[2] = (e[1] * h[0] - e[0] * h[1]) / h0;
   elem->angular_momentum = h0;
   return( 0);
}
