/* Code to find all real roots of a polynomial with real coefficients.
Used in 'gauss.cpp' to get solutions to the equation of Lagrange:

   x^8 + a * x^6 + b * x ^ 3 + c = 0

   and in 'sr.cpp' to solve a particular sixth-degree polynomial used
in figuring out how far away an object might be.  But it could be used
for any polynomial with real coefficients.  It's awkward code,  but
has the virtue of finding _all_ real roots, including double roots and
closely-paired roots that might be neglected by other methods.  (Such
close pairs of solutions are common in the equation of Lagrange.)  Some
other methods can be faster.  But this is the only one I've seen that's
guaranteed to find all real roots,  to within machine precision.  That
certainty was,  for my purposes,  more important than speed.

   It's currently limited to polynomials of degree less than ten.
Redefine MAX_POLY_ORDER if this is a problem.

   It works via a recursive process:  it finds the real roots of the
_derivative_ of the polynomial.  (Therefore,  if you call this function
with an eighth-degree polynomial,  it will internally generate the
seventh-degree derivative polynomial,  find the real roots of that,
which will mean finding the roots of a sixth-degree polynomial, and so
on. As you'll see,  this eventually works down to a first-degree
polynomial, a.k.a. a linear equation,  which is trivially solved without
recursion.)

   Anyway,  the "real roots of the derivative of the polynomial" are also
known as the minima/maxima of the polynomial.  We can know as a fact that
all real roots of the polynomial lie between these maxima/minima.  So the
code evaluates the polynomial at each maximum/minimum;  if its value goes
through a sign change between consecutive maxima/minima, we've got a root
bracketed and can use find_poly_root_between() to nail it down precisely
with the method of Laguerre.

   One odd thing has to be done here,  though.  If we find,  say,  three
minima at x1, x2, x3,  then there may be roots between (x1, x2) and (x2, x3).
There may also be a root less than x1,  and one greater than x3.  To bracket
these roots,  we use a limit on the possible magnitude of the root,  due
to Cauchy (see below).  (Plus another limit I came up with,  which turned out
to be a "rediscovery" of a limit from D. Knuth's _The Art of Programming_.
Knuth's limit is frequently smaller than Cauchy's.)  In general, if we
find N minima/maxima,  there will be N+1 ranges to search.

   One other small improvement has been made:  zero roots are factored
out up front.  Such roots are extremely common,  since the equation
of Lagrange has lots of zero coefficients (five out of nine).  */

#include <math.h>       /* used for fabs( ) prototype */

int find_real_polynomial_roots( const double *poly, int poly_degree,
                                double *real_roots);        /* roots.cpp */

static double evaluate_poly( const double *poly, int poly_degree, const double x)
{
   double rval = 0., power = 1.;

   poly_degree++;
   while( poly_degree--)
      {
      rval += (*poly++) * power;
      power *= x;
      }
   return( rval);
}

/* For the method of Laguerre,  we need the value of the polynomial for a
given x,  _and_ the values of the first and second derivatives of said
poly.  Evaluating all three at once speeds matters up slightly. */

static inline double evaluate_poly_and_derivs( const double *poly,
              int poly_degree, const double x, double *deriv, double *deriv2)
{
   double rval = 0., power = 1.;
   int i;

   *deriv = *deriv2 = 0.;
   for( i = 2; i <= poly_degree; i++)
      {
      const double term = poly[i] * power;
      const double term2 = (double)i * term;

      *deriv2 += term2 * (double)(i - 1);
      *deriv += term2;
      rval += term;
      power *= x;
      }
   *deriv = poly[1] + (*deriv * x);
   return( poly[0] + x * (poly[1] + rval * x));
}

#define SEARCH_TOLERANCE 1.e-10

/* find_poly_root_between() looks for a zero of a polynomial between
two bracketing points.  It starts with a linear interpolation between
the initial two points,  then uses the method of Laguerre to find the
actual root.  If the Laguerre iteration fails due to a negative square
root,  we do a Newton-Raphson step (we've already computed the first
derivative anyway).  If the Laguerre or N-R step would put us outside
the bracketing points,  we reject it and do bisection instead.

   Laguerre is noted for almost always finding a root briskly.  If it
goes past 'max_iterations',  it's probably failing to converge,  and
we switch to bisection for every step.  I've never seen this happen
(except when testing with a low 'max_iterations' value),  but it's
theoretically possible,  and the use of bisection ensures decent worst
case behavior.

   If x1 < 0 and x2 > 0,  then the bracket contains x=0,  and we can
"compute" the polynomial at that point y(0) = poly[0] trivially, and
then adjust the brackets accordingly.  The following code uses this
little trick to get a slight boost in performance.

   It's almost as simple to compute the value of the polynomial at x=1
(just add all the coefficients) and at x=-1 (add all even coeffs,  subtract
all the odd ones),  and I gave this a try.  It does help a little,  and
might be worthwhile in some situations,  but I ended up commenting it out
with #ifdef PROBABLY_NOT_WORTHWHILE.            */

#include <stdio.h>

static double find_poly_root_between( const double *poly, const int poly_degree,
                               double x1, double y1, double x2, double y2)
{
   double delta, x;
   int iteration = 0;

   if( x1 < 0. && x2 > 0.)            /* brackets span zero;  move   */
      if( y1 * poly[0] > 0.)          /* one end to x=0, y = poly[0] */
         {
         x1 = 0.;
         y1 = poly[0];
         }
      else
         {
         x2 = 0.;
         y2 = poly[0];
         }
#ifdef PROBABLY_NOT_WORTHWHILE            /* see comments above */
   if( x1 < 1. && x2 > 1.)          /* brackets span x=1:  move */
      {                             /* one end to x=1, y=poly(1) */
      double y = 0.;
      int i;

      for( i = 0; i <= poly_degree; i++)  /* computing poly(1) is easy; */
         y += poly[i];                    /* just sum coefficients */
      if( y1 * y > 0.)
         {
         x1 = 1.;
         y1 = y;
         }
      else
         {
         x2 = 1.;
         y2 = y;
         }
      }
   else if( x1 < -1. && x2 > -1.)    /* brackets span x=-1:  move */
      {                              /* one end to x=-1, y=poly(-1) */
      double y = 0.;
      int i;

      for( i = 0; i <= poly_degree; i += 2)
         y += poly[i];
      for( i = 1; i <= poly_degree; i += 2)
         y -= poly[i];
      if( y1 * y > 0.)
         {
         x1 = -1.;
         y1 = y;
         }
      else
         {
         x2 = -1.;
         y2 = y;
         }
      }
#endif            /* #ifdef PROBABLY_NOT_WORTHWHILE */
   x = (y1 * x2 - y2 * x1) / (y1 - y2);    /* linear interpolation */
// printf( "N-R range %lf %lf (%lf %lf)\n", x1, x2, y1, y2);
   do
      {
      double y, deriv, deriv2;
      int use_bisection = 0;
      const int max_iterations = 9;

      iteration++;
      y = evaluate_poly_and_derivs( poly, poly_degree, x, &deriv, &deriv2);
      if( y1 < 0. && y < 0. || y1 > 0. && y > 0.)
         {
         x1 = x;
         y1 = y;
         }
      else
         {
         x2 = x;
         y2 = y;
         }
      if( !y)
         delta = 0.;
      else if( iteration > max_iterations)   /* Laguerre has probably  */
         use_bisection = 3;                  /* failed; bisect instead */
      else
         {
         const double n = poly_degree;
         const double big_g = deriv / y;
         const double big_h = big_g * big_g - deriv2 / y;
         const double discr = (n - 1) * (n * big_h - big_g * big_g);

         if( discr >= 0.)     /* take Laguerre step */
            {
            if( big_g > 0.)
               delta = -n / (big_g + sqrt( discr));
            else
               delta = -n / (big_g - sqrt( discr));
            }
         else if( deriv)     /* if Laguerre fails,  try N-R: */
            delta = -y / deriv;
         else                 /* Laguerre _and_ Newton-Raphson fail;  */
            {
            delta = 0.;
            use_bisection = 1;
            }
//       printf( "   x = %lf, y = %lf, delta = %lf\n", x, y, delta);
         x += delta;
         if( x < x1 || x > x2)      /* step would be outside bracket */
            use_bisection = 2;
         }
      if( use_bisection)
         {
         x =     (x1 + x2) * .5;
         delta = (x1 - x2) * .5;
//       printf( "Use_bisection: %d\n", use_bisection);
         }
      }
      while( delta > SEARCH_TOLERANCE || delta < -SEARCH_TOLERANCE);
   return( x);
}

/* Cauchy came up with a useful bound to the absolute value of the roots of
a polynomial:  for the polynomial y = a0 + a1 * x + a2 * x^2 + ... + an * x^n,
the roots will all have absolute values less than

c = 1. + max | ai / an |,  with i=0...n-1

   For comments/proof,  see http://en.wikipedia.org/wiki/Sturm_chain (search
for 'Cauchy' within the text) or:
http://fermatslasttheorem.blogspot.com/2009/02/cauchys-bound-for-real-roots.html
*/

static inline double cauchy_upper_root_bound( const double *poly,
                               int poly_degree)
{
   double max = 0., new_max;

   while( poly_degree--)
      if( (new_max = fabs( *poly++)) > max)
         max = new_max;
   return( 1. + max / fabs( *poly));
}

static inline double knuth_upper_root_bound( const double *poly,
                               int poly_degree)
{
   double rval = 0.;
   int i;

   for( i = 0; i < poly_degree; i++)
      {
      const double new_ratio =
                   log( fabs( poly[i] / poly[poly_degree])) / (double)(poly_degree - i);

      if( !i || new_ratio > rval)
         rval = new_ratio;
      }
   return( 2. * exp( rval));
}

#define MAX_POLY_ORDER 10

int find_real_polynomial_roots( const double *poly, int poly_degree,
                                double *real_roots)
{
   int i, n_roots_found = 0;

   while( poly_degree > 1 && !poly[0])    /* get rid of zero roots quickly. */
      {                                  /* Not strictly necessary, but it */
      real_roots[n_roots_found++] = 0.;  /* speeds things up if there are  */
      poly_degree--;                    /* lots of zero roots... which there */
      poly++;                          /* are when solving Legendre eqn */
      }

   if( poly_degree == 1)      /* simple linear case */
      real_roots[n_roots_found++] = -poly[0] / poly[1];
   else
      {
      double slope_poly[MAX_POLY_ORDER], minmax[MAX_POLY_ORDER];
      double x1, y1, x2, y2;
      int n_minmax;
      const double cauchy_bound = cauchy_upper_root_bound( poly, poly_degree);
      const double knuth_bound  =  knuth_upper_root_bound( poly, poly_degree);
      const double bound =
                 (cauchy_bound < knuth_bound ? cauchy_bound : knuth_bound);

//    printf( "Degree %d: Bounds: Cauchy %lf, mine %lf\n", poly_degree,
//             cauchy_bound, knuth_bound);
      for( i = 0; i < poly_degree; i++)    /* find derivative of poly: */
         slope_poly[i] = (double)( i + 1) * poly[i + 1];
      n_minmax = find_real_polynomial_roots( slope_poly, poly_degree - 1,
                                                minmax);

      x1 = -bound;
      y1 = evaluate_poly( poly, poly_degree, x1);
      for( i = -1; i < n_minmax; i++)
         {
         if( i != n_minmax - 1)
            x2 = minmax[i + 1];
         else
            x2 = bound;
         y2 = evaluate_poly( poly, poly_degree, x2);
//       printf( "Range %lf %lf (%lf %lf)\n", x1, x2, y1, y2);
               /* Make sure there is root searching to do (i.e.,  there is */
               /* a range to search and a sign change within that range): */
         if( x2 != x1 && y1 * y2 <= 0.)
            {
            real_roots[n_roots_found++] = find_poly_root_between( poly,
                                  poly_degree, x1, y1, x2, y2);
//          printf( "Root = %lf\n", real_roots[n_roots_found - 1]);
            }
         if( i != n_minmax - 1)
            {
            x1 = minmax[i + 1];
            y1 = y2;
            }
         }
      }
                  /* If zero roots were found,  then our list of roots may */
                  /* not be in numerical order.  The following ugly sort   */
                  /* (well-suited to almost-sorted lists) will fix that.   */
   for( i = 0; i < n_roots_found - 1; i++)
      if( real_roots[i + 1] < real_roots[i])
         {
         const double tval = real_roots[i + 1];

         real_roots[i + 1] = real_roots[i];
         real_roots[i] = tval;
         if( i)
            i -= 2;
         }
   return( n_roots_found);
}

#ifdef TEST_CODE

/* If compiled with TEST_CODE defined,  you get the following little
test routine which can be run with coefficients on the command line.  The
roots are then printed out on the console. */

#include <stdio.h>
#include <stdlib.h>

int main( const int argc, const char **argv)
{
   int degree = argc - 2, i, n_roots;
   double poly[10], roots[10];

   for( i = 0; i <= degree; i++)
      poly[i] = atof( argv[i + 1]);
   n_roots = find_real_polynomial_roots( poly, degree, roots);
   for( i = 0; i < n_roots; i++)
      printf( "%lf   ", roots[i]);
   return( 0);
}
#endif
