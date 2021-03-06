#include <math.h>
#include <stdio.h>
#ifdef _MSC_VER            /* Microsoft Visual C/C++ lacks a 'stdint.h'; */
#include "stdintvc.h"      /* 'stdintvc.h' is a replacement version      */
#else
#include <stdint.h>
#endif
#include "watdefs.h"
#include "lunar.h"

#define PI 3.141592653589793238462643383279502884197169399375105
#define TWO_PI (PI + PI)

/* This function,  given a pointer to a buffer containing the data from
VSOP.BIN,  can compute planetary positions in heliocentric ecliptic
coordinates.  'planet' can run from 0=sun,  1=mercury,  ... 8=neptune.
(VSOP doesn't handle the moon or Pluto.)  'value' can be either
0=ecliptic longitude, 1=ecliptic latitude, 2=distance from sun.
(These are ecliptic coordinates _of date_,  by the way!)

   t = (JD - 2451545.) / 36525. = difference from J2000,  in Julian
centuries. 'prec' ('precision') can be used to tell the code to ignore
small terms in the VSOP expansion.  Once upon a time,  when math
coprocessors were rare,  I occasionally made use of this fact.  Nowadays,
almost all my code sets prec=0 (i.e.,  include all terms.)                 */

double DLL_FUNC calc_vsop_loc( const void FAR *data, const int planet,
                          const int value, double t, double prec)
{
   int16_t FAR *loc;
   int i, j;
   double sum, rval = 0., power = 1.;
   double FAR *tptr;

   if( !planet)
      return( 0.);       /* the sun */

   t /= 10.;         /* convert to julian millenia */
   loc = (int16_t FAR *)data + (planet - 1) * 18 + value * 6;
   for( i = 6; i; i--, loc++)
      {
      sum = 0.;
      if( prec < 0.)
         prec = -prec;
      tptr = (double FAR *)((int16_t FAR *)data + 8 * 18 + 1) + (unsigned)*loc * 3U;
      for( j = loc[1] - loc[0]; j; j--, tptr += 3)
         if( tptr[0] > prec || tptr[0] < -prec)
            {
            double argument = tptr[1] + tptr[2] * t;

            sum += tptr[0] * cos( argument);
            }
      rval += sum * power;
      power *= t;
      if( t)
         prec /= t;
      }

   if( ((char FAR *)data)[2] == 38)
      rval *= 1.e-8;
   if( value == 0)   /* ensure 0 < lon < 2 * pi  */
      {
      rval = fmod( rval, TWO_PI);
      if( rval < 0.)
         rval += TWO_PI;
      }
   return( rval);
}

