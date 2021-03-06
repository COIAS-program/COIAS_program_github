#include "colors.h"

/*
Code to do assorted rough transformations between color systems,
such as getting a B-V value given a V-I color.  I started out with
FORTRAN code supplied by Brian Skiff,  converted it to C,  and added
some inverse transformations not previously available.  Note that these
are _extremely_ rocky,  because they happen when one color doesn't
vary much with respect to another color.  They should not be taken
too seriously.  Brian comments:

   "High-order polynomials for transforming amongst colors are given
by Caldwell et al.:

1993SAAOC..15....1C
  CALDWELL J.A.R., COUSINS A.W.J., AHLERS C.C., VAN WAMELEN P., MARITZ E.J.
  South African Astron. Obs. Circ., 15, 1-29 (1993)
  Statistical relations between photometric colours of common types of stars in
    the UBV (RI)c, JHK and uvby systems."

   You'll see three separate test main( ) functions at the bottom,
originally used in testing these functions and now possibly helpful in
showing how they are used.  If you define LONEOS_PHOT (the last test
main( )),  you'll get a program to read loneos.phot and add colors
where no colors were previously available,  flagged so you can know
where they came from.
*/

#define COLOR_ORDER 13

static double compute_color_polynomial( const double ival,
              const double *coeffs, const double low_limit,
              const double high_limit)
{
   double rval = 0., power = 1.;
   int order = COLOR_ORDER;

   if( ival < low_limit || ival > high_limit)
      rval = 99.;
   else while( order--)
      {
      rval += (*coeffs++) * power;
      power *= ival - 1.;
      }
   return( rval + 1.);
}

static double compute_inverse_color_polynomial( const double ival,
              const double *coeffs, double ilow_limit, double ihigh_limit)
{
   double color_low, color_high, rval, color_rval;
   double high_limit = ihigh_limit;
   double low_limit = ilow_limit;
   int max_iterations = 100;

   color_low = compute_color_polynomial( ilow_limit, coeffs,
                        low_limit, high_limit);
   color_high = compute_color_polynomial( ihigh_limit, coeffs,
                        low_limit, high_limit);
   if( ival < color_low || ival > color_high)
      rval = 99.;
   else
      while( color_high - color_low > 1.e-6 && max_iterations)
         {
         rval = (ival - color_low) / ( color_high - color_low);
         rval += rval * (rval -.5) * (rval - 1.);
         rval = low_limit + (high_limit - low_limit) * rval;
         color_rval = compute_color_polynomial( rval, coeffs,
                        ilow_limit, ihigh_limit);
         if( color_rval < ival)
            {
            low_limit = rval;
            color_low = color_rval;
            }
         else
            {
            high_limit = rval;
            color_high = color_rval;
            }
         max_iterations--;
         }

   if( !max_iterations)       /* didn't converge on an answer */
      rval = 99.;
   return( rval);
}

static const double coeffs_vi_to_bv[COLOR_ORDER] = {
    -0.6865072E-01,  0.8837997E+00,   -0.3889774E+00,
    -0.4998126E-02,  0.3867544E+00,   -0.5422331E+00,
    -0.8926476E-01,  0.5194797E+00,   -0.2044681E+00,
    -0.1009025E+00,  0.9543256E-01,   -0.2567529E-01,
     0.2393742E-02 };

double v_minus_i_to_b_minus_v( const double v_minus_i)
{
   return( compute_color_polynomial(
                    v_minus_i, coeffs_vi_to_bv, -.23, 3.70));
}

double b_minus_v_to_v_minus_i( const double b_minus_v)
{
   return( compute_inverse_color_polynomial(
                    b_minus_v, coeffs_vi_to_bv, -.23, 3.70));
}

static const double coeffs_vi_to_vr[COLOR_ORDER] = {
   -0.4708373E+00,    0.5920728E+00,   -0.1095294E-01,
   -0.2281118E+00,   -0.9372892E-01,    0.1931393E+00,
    0.5077253E-01,   -0.9927284E-01,    0.8560631E-02,
    0.1922702E-01,   -0.7201880E-02,    0.7743020E-03, 0. };

double v_minus_i_to_v_minus_r( const double v_minus_i)
{
   return( compute_color_polynomial(
                    v_minus_i, coeffs_vi_to_vr, -.30, 4.00));
}

double v_minus_r_to_v_minus_i( const double v_minus_r)
{
   return( compute_inverse_color_polynomial(
                    v_minus_r, coeffs_vi_to_vr, -.30, 4.00));
}

double v_minus_r_to_b_minus_v( const double v_minus_r)
{
   static const double coeffs[COLOR_ORDER] = {
   0.4860429E+00,   0.6904008E+00,  -0.1229411E+01,   0.2990030E+01,
   0.7104513E+01,  -0.1637799E+02,  -0.2977123E+02,   0.4390751E+02,
   0.6145810E+02,  -0.5265358E+02,  -0.6135921E+02,   0.2297835E+02,
   0.2385013E+02};

   return( compute_color_polynomial( v_minus_r, coeffs, -.10, 1.75));
}

double b_minus_v_to_v_minus_r( const double b_minus_v)
{
   static const double coeffs[COLOR_ORDER] = {
  -0.4140951E+00,   0.7357165E+00,  -0.5242979E-01,  -0.6293304E+00,
   0.2332871E+01,   0.3812365E+01,  -0.5082941E+01,  -0.6520325E+01,
   0.4817797E+01,   0.5065505E+01,  -0.1706011E+01,  -0.1568243E+01, 0. };

   return( compute_color_polynomial( b_minus_v, coeffs, -.23, 1.95));
}

   /* This function derived from data on p 57,  _Intro & Guide to the Data_ */
double johnson_b_minus_v_from_tycho_b_minus_v( const double b_v_t)
{
   double delta = 0.;

   if( b_v_t < -.2 || b_v_t > 1.8)
      return( 99.);        /* no reasonable transformation possible */
   if( b_v_t < .1)
      delta = -.006 + .006 * (b_v_t + .2) / .3;
   else if( b_v_t < .5)
      delta = .046 * (b_v_t - .1) / .4;
   else if( b_v_t < 1.4)
      delta = .046 - .054 * (b_v_t - .5) / .9;
   else if( b_v_t < 1.8)
      delta = -.008 - .024 * (b_v_t - 1.4) / .4;
   return( .85 * b_v_t + delta);
}

/*
This function derived from data on p 57,  _Intro & Guide to the Data_.
It's probably better to use the tycho_to_johnson_colors( ) function,
in COLORS2.CPP,  instead.  I wrote the following some time ago,  and it's
somewhat obsolete now.
*/

double johnson_v_from_tycho_b_minus_v( const double b_v_t, const double tycho_v)
{
   double delta = 0.;

   if( b_v_t < -.2 || b_v_t > 1.8)
      return( 99.);        /* no reasonable transformation possible */
   if( b_v_t < .1)
      delta =  .014 - .014 * (b_v_t + .2) / .3;
   else if( b_v_t < .5)
      delta = -.005 * (b_v_t - .1) / .4;
   else if( b_v_t < 1.4)
      delta = -.005;
   else if( b_v_t < 1.8)
      delta = -.005 - .010 * (b_v_t - 1.4) / .4;
   return( tycho_v - .09 * b_v_t + delta);
}


#ifdef SIMPLE_TEST_PROGRAM

#include <stdio.h>
#include <stdlib.h>

void main( int argc, char **argv)
{
   double ival = atof( argv[1]);

   printf( "v_minus_i_to_b_minus_v( %lf) = %lf\n",
            ival, v_minus_i_to_b_minus_v( ival));
   printf( "v_minus_i_to_v_minus_r( %lf) = %lf\n",
            ival, v_minus_i_to_v_minus_r( ival));
   printf( "b_minus_v_to_v_minus_i( %lf) = %lf\n",
            ival, b_minus_v_to_v_minus_i( ival));
   printf( "v_minus_r_to_v_minus_i( %lf) = %lf\n",
            ival, v_minus_r_to_v_minus_i( ival));
   printf( "v_minus_r_to_b_minus_v( %lf) = %lf\n",
            ival, v_minus_r_to_b_minus_v( ival));
   printf( "b_minus_v_to_v_minus_r( %lf) = %lf\n",
            ival, b_minus_v_to_v_minus_r( ival));
}
#endif

#ifdef GRAPHING_PROGRAM

#include <stdio.h>
#include <conio.h>
#include <stdlib.h>
#include <graph.h>

void main( int argc, char **argv)
{
   int function = atoi( argv[1]), i;
   char buff[200];
   FILE *ifile = fopen( "loneos.phot", "rb");
   double limits[12] = { -.4, 3.9, -.4, 2.,        /* V-I to B-V */
                         -.5, 4.2, -.4, 2.1,       /* V-I to V-R */
                         -.3, 2.,  -.4, 2.2 };     /* V-R to B-V */
   double *lim = limits + function * 4;
   int xcolumns[3] = { 75, 75, 69 };
   int ycolumns[3] = { 63, 69, 63 };

   _setvideomode( _VRES16COLOR);
   _setcolor( 2);
   for( i = 0; i < 640; i++)
      {
      double ocolor, icolor = lim[0] + (lim[1] - lim[0]) * (double)i / 640.;

      if( function == 0)
         ocolor = v_minus_i_to_b_minus_v( icolor);
      else if( function == 1)
         ocolor = v_minus_i_to_v_minus_r( icolor);
      else
         ocolor = v_minus_r_to_b_minus_v( icolor);
      _setpixel( (short)i, (short)( 480. * (ocolor-lim[3]) / (lim[2]-lim[3])));
      }

   _setcolor( 3);
   while( fgets( buff, sizeof( buff), ifile))
      {
      if( buff[xcolumns[function]] == '.' && buff[ycolumns[function]] == '.')
         {
         double icolor = atof( buff + xcolumns[function] - 2);
         double ocolor = atof( buff + ycolumns[function] - 2);
         int xpixel = (int)( 640. * (icolor-lim[0]) / (lim[1]-lim[0]));
         int ypixel = (int)( 480. * (ocolor-lim[3]) / (lim[2]-lim[3]));
         short ix, iy;
         short deltas[9 * 2] = { 0,0, 1,0, 0,1, -1,0, 0,-1,
                        1,1, 1,-1, -1,-1, -1,1 };

         for( i = 0; i < 18; i += 2)
            {
            ix = (short)( xpixel + deltas[i]);
            iy = (short)( ypixel + deltas[i + 1]);
            if( !_getpixel( ix, iy))
               i = 99;
            }
         if( i != 18)
            _setpixel( ix, iy);
         }
      buff[xcolumns[function]] = buff[ycolumns[function]] = ' ';
      }

   getch( );
   _setvideomode( _DEFAULTMODE);
}

#endif

#ifdef LONEOS_PHOT
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void main( int argc, char **argv)
{
   char buff[200];
   FILE *ifile = fopen( "loneos.pho", "rb"), *ofile;
   int i;

   if( !ifile)
      {
      printf( "Couldn't open 'loneos.pho'\n");
      exit( -1);
      }
   ofile = fopen( "loneos2.pho", "wb");
   while( fgets( buff, sizeof( buff), ifile))
      {
      if( buff[27] == '.' && buff[59] == '.' && buff[30] == ' ' &&
                                 strlen( buff) > 60)
         {
         int bv_flag, vr_flag, vi_flag;
         double b_minus_v = 99., v_minus_r = 99., v_minus_i = 99.;

         for( i = 0; buff[i] >= ' '; i++)
            ;
         while( i < 84)
            buff[i++] = '\0';
         buff[84] = '\0';
         bv_flag = (buff[66] == '.');
         vr_flag = (buff[73] == '.');
         vi_flag = (buff[80] == '.');
         if( vi_flag)
            {
            v_minus_i = atof( buff + 78);
            if( !bv_flag)
               {
               b_minus_v = v_minus_i_to_b_minus_v( v_minus_i);
               bv_flag = 'i';
               }
            if( !vr_flag)
               {
               v_minus_r = v_minus_i_to_v_minus_r( v_minus_i);
               vr_flag = 'i';
               }
            }
         else
            if( vr_flag)
               {
               v_minus_r = atof( buff + 71);
               v_minus_i = v_minus_r_to_v_minus_i( v_minus_r);
               vi_flag = 'r';
               if( !bv_flag)
                  {
                  b_minus_v = v_minus_r_to_b_minus_v( v_minus_r);
                  bv_flag = 'r';
                  }
               }
            else     /* no V-R or V-I:  Only B-V is available */
               {
               b_minus_v = atof( buff + 64);
               v_minus_r = b_minus_v_to_v_minus_r( b_minus_v);
               v_minus_i = b_minus_v_to_v_minus_i( b_minus_v);
               vi_flag = vr_flag = 'b';
               }
         if( bv_flag > 1 && b_minus_v < 98.)
            sprintf( buff + 64, "%5.2lf%c", b_minus_v, bv_flag);
         if( vr_flag > 1 && v_minus_r < 98.)
            sprintf( buff + 71, "%5.2lf%c", v_minus_r, vr_flag);
         if( vi_flag > 1 && v_minus_i < 98.)
            sprintf( buff + 78, "%5.2lf%c", v_minus_i, vi_flag);
         for( i = 0; i < 84; i++)
            if( !buff[i])
               buff[i] = ' ';
         buff[84] = '\0';
         fprintf( ofile, "%s\n", buff);
         }
      else
         fprintf( ofile, "%s", buff);
      }
   fclose( ifile);
   fclose( ofile);
}
#endif
