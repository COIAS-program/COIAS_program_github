#include <stdio.h>
#include <stdlib.h>
#include <math.h>

      /* "normal_vector" takes a vector in ecliptic J2000 coordinates and */
      /* returns a vector rotated to _equatorial_ J2000. */
static void normal_vect( double *ival)
{
   static const double sin_obliq_2000 = .397777156;
   static const double cos_obliq_2000 = .917482062;
   double tval;

   tval = ival[1] * cos_obliq_2000 - ival[2] * sin_obliq_2000;
   ival[2] = ival[2] * cos_obliq_2000 + ival[1] * sin_obliq_2000;
   ival[1] = tval;
}

void main( int argc, char **argv)
{
   const double pi = 3.1415926535897932384626433;
   double omega = atof( argv[1]) * pi / 180.;
   double Omega = atof( argv[2]) * pi / 180.;
   double incl  = atof( argv[3]) * pi / 180.;
   double lon_per = Omega + atan2( sin( omega) * cos( incl), cos( omega));
   double vec[3];
   double vec_len;
   int i;

   vec[0] = cos( lon_per);
   vec[1] = sin( lon_per);
   vec[2] = tan( incl) * sin( lon_per - Omega);
   vec_len = sqrt( 1. + vec[2] * vec[2]);
   for( i = 0; i < 3; i++)
      vec[i] /= vec_len;
   normal_vect( vec);
   printf( "%lf %lf %lf\n", vec[0], vec[1], vec[2]);
}
