#include <math.h>
#include "watdefs.h"
#include "lunar.h"
#include "afuncs.h"

#define J2000  2451545.
#define PI 3.141592653589793238462643383279502884197

/* For the following,  see p 373 of the _Explanatory Supplement_ */

static void calc_triton_loc( const double jd, double *vect)
{
   const double t_cent = (jd - J2000) / 36525.;
   const double n = (359.28 + 54.308 * t_cent) * (PI / 180.);
   const double t0 = 2433282.5;
   const double theta = (151.401 + .57806 * (jd - t0) / 365.25) * (PI / 180.);
            /* Semimajor axis is 488.49 arcseconds at one AU: */
   const double semimajor = 488.49 * (PI / 180.) / 3600.;
   const double longitude =
               (200.913 + 61.2588532 * (jd - t0)) * (PI / 180.);
   const double gamma = 158.996 * (PI / 180.);

         /* Calculate longitude and latitude on invariable plane: */
   const double lon_on_ip = theta + atan2( sin( longitude) * cos( gamma),
                                     cos( longitude));
   const double lat_on_ip = asin( sin( longitude) * sin( gamma));
         /* Vectors defining invariable plane,  expressed in B1950: */
   double x_axis[3], y_axis[3], z_axis[3];
         /* Vector defining Triton position in invariable plane space: */
   double triton[3];
         /* RA/dec of the pole: */
   double ra_dec_p[2];
   double matrix[9];
   double vect_1950[3];
   int i;

   polar3_to_cartesian( triton, lon_on_ip, lat_on_ip);

   ra_dec_p[0] = (298.72 * PI / 180.) + (2.58 * PI / 180.) * sin( n)
                     - (0.04 * PI / 180.) * sin( n + n);
   ra_dec_p[1] = (42.63 * PI / 180.) - (1.90 * PI / 180.) * cos( n)
                     + (0.01 * PI / 180.) * cos( n + n);
   setup_precession( matrix, 1950., 2000.);
   precess_ra_dec( matrix, ra_dec_p, ra_dec_p, 1);
   polar3_to_cartesian( x_axis, ra_dec_p[0] + PI / 2., 0.);
   polar3_to_cartesian( y_axis, ra_dec_p[0] + PI, PI / 2. - ra_dec_p[1]);
   polar3_to_cartesian( z_axis, ra_dec_p[0], ra_dec_p[1]);

   for( i = 0; i < 3; i++)
      vect_1950[i] = semimajor * (x_axis[i] * triton[0] +
                      y_axis[i] * triton[1] + z_axis[i] * triton[2]);
   precess_vector( matrix, vect_1950, vect);
}

const static long mars_uranus_satellite_elements[7 * 5] = {

/* Start ang  Orbital per   RA0      dec0     radius
 (microrads)  (10^-6 d)  (microrad) (microrad) (nanoAU)     */

  3544712L,  252037905L, 4491693L, -264911L, 1276396L,  /* U-I = Ariel */
  4385820L,  414417646L, 4491952L, -264063L, 1778097L,  /* U-V = Umbriel */
  4915258L,  870586694L, 4490679L, -263051L, 2916489L,  /* U-III = Titania */
  6153269L, 1346323420L, 4493030L, -262184L, 3900606L,  /* U-IV = Oberon */
  5755932L,  141347941L, 4447133L, -327298L,  868146L,  /* U-V = Miranda */
  5666745L,  -31891023L, 5522345L,  917807L,   62687L,   /* Phobos */
  4944714L, -126244070L, 5579507L,  933753L,  156811L }; /* Deimos */

/*
Code to compute approximate positions for five major satellites of
Uranus and two of Mars.  I couldn't find good theories for any of
these objects,  but I did find astrometry on the ADC and BDL Web
sites.  I wrote a little program to do a least-squares fit of circular
orbits for each of them,  and found (somewhat to my surprise) that
such orbits fit the astrometry quite nicely.

Satell_no is 0=Ariel,  1=Umbriel,  2=Titania,  3=Oberon,  4=Miranda,
5=Phobos,  6=Deimos,  7 = Triton.  The resulting vector is a J2000
equatorial planetocentric position,  in AU.  The above coefficients
for each satellite give,  in order,  the position of the object
along that circular orbit at the instant J2000;  the period of the
orbit in units of 10^-6 day;  the RA and dec of the axis of that
circular orbit;  and a radius,  in units of 10^-9 AU (about .15
km).          */

#define SATELL_NUM_TRITON         7
#define SATELL_NUM_CHARON         8
#define SATELL_NUM_S2005_P_1      9
#define SATELL_NUM_S2005_P_2     10

void DLL_FUNC calc_mars_uranus_satell_loc( const int satell_no,
                                          const double jd, double *vect)
{
   const long *sdata = mars_uranus_satellite_elements + satell_no * 5;
   int i;
   double ang, r_cos_ang, r_sin_ang;
   double sat_data[5];
   double left[3], up[3];

   if( satell_no == SATELL_NUM_TRITON)
      {
      calc_triton_loc( jd, vect);
      return;
      }

               /* For Charon (satell_no = 8), S/2005 P 1 (satell_no = 9), */
               /* and S/2005 P 2 (satell_no = 10),  we can cheat.  Charon */
               /* is in synchronous rotation with Pluto,  so we can use   */
               /* Charon's COSPAR rotation model to get the position for  */
               /* us.  The others are computed assuming 4:1 and 6:1 ratios */
               /* with Charon.         */

   if( satell_no >= SATELL_NUM_CHARON && satell_no <= SATELL_NUM_S2005_P_2)
      {
      double r0, jd_to_use = jd;
      double matrix[9];

      switch( satell_no)
         {
         case SATELL_NUM_CHARON:
            r0 = 19405. / AU_IN_KM;
            break;
         case SATELL_NUM_S2005_P_1:
            r0 = 64700. / AU_IN_KM;
            jd_to_use -= 10.;
            jd_to_use /= 6.;
            break;
         case SATELL_NUM_S2005_P_2:
            r0 = 49400. / AU_IN_KM;
            jd_to_use -= 13.3;
            jd_to_use /= 4.;
            break;
         }

      calc_planet_orientation( 31, 0, jd_to_use, matrix);
      for( i = 0; i < 3; i++)
         vect[i] = -r0 * matrix[i];
      return;
      }

   for( i = 0; i < 5; i++)
      sat_data[i] = (double)sdata[i] * 1.e-6;
   sat_data[1] /= 100.;
   sat_data[4] /= 1000.;
   ang = sat_data[0] + (jd - J2000) * PI * 2. / sat_data[1];
   r_cos_ang = sat_data[4] * cos( ang);
   r_sin_ang = sat_data[4] * sin( ang);


   left[0] = sin( sat_data[2]);
   left[1] = -cos( sat_data[2]);
   left[2] = 0.;
   up[0] =  -cos( sat_data[2]) * sin( sat_data[3]);
   up[1] =  -sin( sat_data[2]) * sin( sat_data[3]);
   up[2] =                       cos( sat_data[3]);
#ifdef DOESNT_WORK
   polar3_to_cartesian( left, sat_data[2] - PI / 2., 0.);
   polar3_to_cartesian( up, sat_data[2] + PI, sat_data[3]);
#endif
   for( i = 0; i < 3; i++)
      vect[i] = r_cos_ang * left[i] + r_sin_ang * up[i];
}
