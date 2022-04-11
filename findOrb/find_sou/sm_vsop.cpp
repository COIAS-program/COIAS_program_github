#include <math.h>
#include <stdlib.h>

/* Following are the first few terms of the VSOP series for each planet
   (Mercury through Neptune).  The 'axis' is 1 for x, 2 for y, 3 for z.

   The position is computed as the sum of terms of the form

   amplitude * cos( phase + freq * t_cen)

   where t_cen = (JD - 2451545) / 36525 = centuries from J2000.  Except that
   the first term,  with axis = 0,  just includes constant offsets:  the
   'amplitude' = xoffset, 'phase' = yoffset, 'freq' = zoffset.

   Coordinates are J2000 ecliptic.

   All this is used to get _very_ rough planetary positions for use in
   deciding if any perturbers are needed for the initial orbit determination
   (basically,  "is this coordinate  within a few Hill spheres of a planet").
   We can usually use this to say:  "No planet is conceivably close enough
   to exert serious short-term perturbations right now",  saving us any
   really computationally intensive effort (most of the time),  even the
   effort of finding more accurate planetary positions.  The full series
   contain thousands of terms,  including some where the terms are multiplied
   by t_cen ^ n (n=1...5).

   Terms of the following magnitude or greater are included:
      Mercury     .006 AU
      Venus       .003
      Earth       .001
      Mars        .01
      Jupiter     .02
      Saturn      .025
      Uranus      .02
      Neptune     .03         */

int compute_rough_planet_loc( const double t_cen, const int planet_idx,
                                          double *vect);    /* sm_vsop.c */
int check_for_perturbers( const double t_cen, const double *vect); /* sm_vsop*/

#define SMALL_VSOP_TERM struct small_vsop_term

SMALL_VSOP_TERM
   {
   int axis;
   double amplitude, phase, freq;
   };

#define N_MERC_TERMS 6
#define N_VENU_TERMS 4
#define N_EART_TERMS 5
#define N_MARS_TERMS 6
#define N_JUPI_TERMS 6
#define N_SATU_TERMS 10
#define N_URAN_TERMS 12
#define N_NEPT_TERMS 10

static const int n_terms[9] = { 0, N_MERC_TERMS, N_VENU_TERMS, N_EART_TERMS,
       N_MARS_TERMS, N_JUPI_TERMS, N_SATU_TERMS, N_URAN_TERMS, N_NEPT_TERMS };

static const SMALL_VSOP_TERM merc_terms[N_MERC_TERMS] = {
 { 0, -0.02625615963, -0.11626131831, -0.00708734365 },
 { 1,  0.37546291728, 4.39651506942,   2608.790314157420  },
 { 1,  0.03825746672, 1.16485604339,   5217.580628314840  },
 { 2,  0.37953642888, 2.83780617820,   2608.790314157420  },
 { 2,  0.03854668215, 5.88780608966,   5217.580628314840  },
 { 3,  0.04607665326, 1.99295081967,   2608.790314157420  } };

static const SMALL_VSOP_TERM venu_terms[N_VENU_TERMS] = {
 { 0,  0.00486448018, -0.00549506273, -0.00035588343 },
 { 1,  0.72211281391, 3.17575836361,   1021.328554621100  },
 { 2,  0.72324820731, 1.60573808356,   1021.328554621100  },
 { 3,  0.04282990302, 0.26703856476,   1021.328554621100  } };

static const SMALL_VSOP_TERM eart_terms[N_EART_TERMS] = {
 { 0,  0.00561144206, -0.02442699036, -0.00000001086 },
 { 1,  0.99982928844, 1.75348568475,    628.307584999140  },
 { 1,  0.00835257300, 1.71034539450,   1256.615169998280  },
 { 2,  0.99989211030, 0.18265890456,    628.307584999140  },
 { 2,  0.00835292314, 0.13952878991,   1256.615169998280  } };

#ifdef MORE_PRECISE_EARTH
         /* Might come in handy someday,  for computing basic orbits without */
         /* PS-1996 or DE ephems.  At this level,  though,  we may have to   */
         /* include some of the currently ignored secular terms.             */
static const SMALL_VSOP_TERM eart_terms[21] = {
 { 0,  0.00561144206, -0.02442699036, -0.00000001086 },
 { 1,  0.99982928844, 1.75348568475,    628.307584999140  },
 { 1,  0.00835257300, 1.71034539450,   1256.615169998280  },
 { 1,  0.00010466628, 1.66722645223,   1884.922754997420  },
 { 1,  0.00003110838, 0.66875185215,   8399.684731811189  },
 { 1,  0.00002552498, 0.58310207301,     52.969096509460  },
 { 1,  0.00002137256, 1.09235189672,    157.734354244780  },
 { 1,  0.00001709103, 0.49540223397,    627.955273164240  },
 { 1,  0.00001707882, 6.15315547484,    628.659896834040  },
 { 1,  0.00001445242, 3.47272783760,    235.286615377180  },
 { 1,  0.00001091006, 3.68984782465,    522.369391980220  },
 { 2,  0.99989211030, 0.18265890456,    628.307584999140  },
 { 2,  0.00835292314, 0.13952878991,   1256.615169998280  },
 { 2,  0.00010466965, 0.09641690558,   1884.922754997420  },
 { 2,  0.00003110838, 5.38114091484,   8399.684731811189  },
 { 2,  0.00002570338, 5.30103973360,     52.969096509460  },
 { 2,  0.00002147473, 2.66253538905,    157.734354244780  },
 { 2,  0.00001709219, 5.20780401071,    627.955273164240  },
 { 2,  0.00001707987, 4.58232858766,    628.659896834040  },
 { 2,  0.00001440265, 1.90068164664,    235.286615377180  },
 { 2,  0.00001135092, 5.27313415220,    522.369391980220  } };,
#endif

#ifdef INCLUDE_EARTH_MOON_BARYCENTER
         /* no real use for these,  except for reference: */
static const SMALL_VSOP_TERM emb_terms[5] = {
 { 0,  0.00561144161, -0.02442698841, -0.00000001086 },
 { 1,  0.99982927460, 1.75348568475,    628.307584999140  },
 { 1,  0.00835257300, 1.71034539450,   1256.615169998280  },
 { 2,  0.99989209645, 0.18265890456,    628.307584999140  },
 { 2,  0.00835292314, 0.13952878991,   1256.615169998280  } };
#endif

static const SMALL_VSOP_TERM mars_terms[N_MARS_TERMS] = {
 { 0, -0.19502945246,  0.08655481102,  0.00660669541 },
 { 1,  1.51769936383, 6.20403346548,    334.061242669980  },
 { 1,  0.07070919655, 0.25870338558,    668.122485339960  },
 { 2,  1.51558976277, 4.63212206588,    334.061242669980  },
 { 2,  0.07064550239, 4.97051892902,    668.122485339960  },
 { 3,  0.04901207220, 3.76712324286,    334.061242669980  } };

static const SMALL_VSOP_TERM jupi_terms[N_JUPI_TERMS] = {
 { 0, -0.36662642320, -0.09363670616,  0.00859031952 },
 { 1,  5.19663470114, 0.59945082355,     52.969096509460  },
 { 1,  0.12593937922, 0.94911583701,    105.938193018920  },
 { 2,  5.19520046589, 5.31203162731,     52.969096509460  },
 { 2,  0.12592862602, 5.66160227728,    105.938193018920  },
 { 3,  0.11823100489, 3.55844646343,     52.969096509460  } };

static const SMALL_VSOP_TERM satu_terms[N_SATU_TERMS] = {
 { 0,  0.04244797817, -0.79387988806,  0.01214249867 },
 { 1,  9.51638335797, 0.87441380794,     21.329909543800  },
 { 1,  0.26412374238, 0.12390892620,     42.659819087600  },
 { 1,  0.06760430339, 4.16767145778,     20.618554843720  },
 { 1,  0.06624260115, 0.75094737780,     22.041264243880  },
 { 2,  9.52986882699, 5.58600556665,     21.329909543800  },
 { 2,  0.26441781302, 4.83528061849,     42.659819087600  },
 { 2,  0.06916653915, 2.55279408706,     20.618554843720  },
 { 2,  0.06633570703, 5.46258848288,     22.041264243880  },
 { 3,  0.41356950940, 3.60234142982,     21.329909543800  } };

static const SMALL_VSOP_TERM uran_terms[N_URAN_TERMS] = {
 { 0,  1.32272523872, -0.16256125476, -0.01774318778 },
 { 1, 19.17370730359, 5.48133416489,      7.478159856730  },
 { 1,  0.44402496796, 1.65967519586,     14.956319713460  },
 { 1,  0.14668209481, 3.42395862804,      7.329712585900  },
 { 1,  0.14130269479, 4.39572927934,      7.626607127560  },
 { 1,  0.06201106178, 5.14043574125,       .148447270830  },
 { 2, 19.16518231584, 3.91045677002,      7.478159856730  },
 { 2,  0.44390465203, 0.08884111329,     14.956319713460  },
 { 2,  0.14755940186, 1.85423280679,      7.329712585900  },
 { 2,  0.14123958128, 2.82486076549,      7.626607127560  },
 { 2,  0.06250078231, 3.56960243857,       .148447270830  },
 { 3,  0.25878127698, 2.61861272578,      7.478159856730  } };

static const SMALL_VSOP_TERM nept_terms[N_NEPT_TERMS] = {
 { 0, -0.27080164222, -0.30205857683,  0.01245978462 },
 { 1, 30.05890004476, 5.31211340029,      3.813303563780  },
 { 1,  0.13505661755, 3.50078975634,      7.626607127560  },
 { 1,  0.15726094556, 0.11319072675,      3.664856292950  },
 { 1,  0.14935120126, 1.08499403018,      3.961750834610  },
 { 2, 30.06056351665, 3.74086294714,      3.813303563780  },
 { 2,  0.13506391797, 1.92953034883,      7.626607127560  },
 { 2,  0.15706589373, 4.82539970129,      3.664856292950  },
 { 2,  0.14936165806, 5.79694900665,      3.961750834610  },
 { 3,  0.92866054405, 1.44103930278,      3.813303563780  } };

static const SMALL_VSOP_TERM *vsop_terms[9] = { NULL,
         merc_terms, venu_terms, eart_terms, mars_terms,
         jupi_terms, satu_terms, uran_terms, nept_terms };

int compute_rough_planet_loc( const double t_cen, const int planet_idx,
                                          double *vect)
{
   int i;
   const SMALL_VSOP_TERM *vptr = vsop_terms[planet_idx];

   vect[0] = vptr->amplitude;
   vect[1] = vptr->phase;
   vect[2] = vptr->freq;
   vptr++;
   for( i = n_terms[planet_idx] - 1; i; i--, vptr++)
      vect[vptr->axis - 1] +=
            vptr->amplitude * cos( vptr->phase + vptr->freq * t_cen);
   return( 0);
}

#define MERCURY_PERIHELION          0.30749951
#define MERCURY_APHELION            0.46669835
#define VENUS_PERIHELION            0.71843270
#define VENUS_APHELION              0.72823128
#define EARTH_PERIHELION            0.97
#define EARTH_APHELION              1.03
#define MARS_PERIHELION             1.38133346
#define MARS_APHELION               1.66599116
#define JUPITER_PERIHELION          4.95155843
#define JUPITER_APHELION            5.45516759
#define SATURN_PERIHELION           9.02063224
#define SATURN_APHELION            10.0535084
#define URANUS_PERIHELION          18.2860560
#define URANUS_APHELION            20.0964719
#define NEPTUNE_PERIHELION         29.8107953
#define NEPTUNE_APHELION           30.3271317

/* Perturbations from a given planet ought to be included if its rough
position is within the following ranges.  These include the fact that
the positions are somewhat approximate,  plus a little room beyond the
Hill sphere,  but they're a tad arbitrary/subject to tweaking.  Set 'em
too high,  and perturbations will be included when not needed.  Too low,
and perturbations will be omitted when they _are_ needed.

   The currently-set ranges are essentially twice the Hill sphere radii
(except for Mercury and Mars,  for which the uncertainty in the position
formula is the limiting factor).   */

#define MERCURY_RANGE            .02
#define VENUS_RANGE              .02
#define EARTH_RANGE              .02
#define MARS_RANGE               .02
#define JUPITER_RANGE            .7
#define SATURN_RANGE             .8
#define URANUS_RANGE             .9
#define NEPTUNE_RANGE           1.4

#define MERCURY_INNER_LIMIT   (MERCURY_PERIHELION - MERCURY_RANGE)
#define MERCURY_OUTER_LIMIT   (MERCURY_APHELION   + MERCURY_RANGE)
#define VENUS_INNER_LIMIT     (VENUS_PERIHELION   - VENUS_RANGE  )
#define VENUS_OUTER_LIMIT     (VENUS_APHELION     + VENUS_RANGE  )
#define EARTH_INNER_LIMIT     (EARTH_PERIHELION   - EARTH_RANGE  )
#define EARTH_OUTER_LIMIT     (EARTH_APHELION     + EARTH_RANGE  )
#define MARS_INNER_LIMIT      (MARS_PERIHELION    - MARS_RANGE   )
#define MARS_OUTER_LIMIT      (MARS_APHELION      + MARS_RANGE   )
#define JUPITER_INNER_LIMIT   (JUPITER_PERIHELION - JUPITER_RANGE)
#define JUPITER_OUTER_LIMIT   (JUPITER_APHELION   + JUPITER_RANGE)
#define SATURN_INNER_LIMIT    (SATURN_PERIHELION  - SATURN_RANGE )
#define SATURN_OUTER_LIMIT    (SATURN_APHELION    + SATURN_RANGE )
#define URANUS_INNER_LIMIT    (URANUS_PERIHELION  - URANUS_RANGE )
#define URANUS_OUTER_LIMIT    (URANUS_APHELION    + URANUS_RANGE )
#define NEPTUNE_INNER_LIMIT   (NEPTUNE_PERIHELION - NEPTUNE_RANGE)
#define NEPTUNE_OUTER_LIMIT   (NEPTUNE_APHELION   + NEPTUNE_RANGE)

/* In determining whether any planet may be close enough to exert
serious perturbations,  we first check the square of its distance from
the sun;  if that's between the limits we're using for a given planet,
we then have to compute the location of that planet.  (We check the
square of the distance against the square of the planet's q and Q,
just to avoid taking a square root.)

   We don't necessarily compute the entire planetary position.  If,
after computing the approximate z-coordinate of the planet, we see
that it can't be within the limits set above,  then there's no point
in going on to compute the x and y coordinates.

   Incidentally,  z is checked first,  because that coordinate requires
the fewest terms.  (For the earth,  it requires none,  since the z-coord
in the ecliptic frame of the earth is basically zero at this rough level.)
If z is okay,  then y is checked,  then x. */

int check_for_perturbers( const double t_cen, const double *vect)
{
   const double r2 = vect[0] * vect[0] + vect[1] * vect[1] + vect[2] * vect[2];
   int planet_to_check = 0, axis;

   if( r2 > JUPITER_INNER_LIMIT * JUPITER_INNER_LIMIT)
      {                 /* consider gas giants only */
      if( r2 < JUPITER_OUTER_LIMIT * JUPITER_OUTER_LIMIT)
         planet_to_check = 5;
      else if( r2 > SATURN_INNER_LIMIT * SATURN_INNER_LIMIT)
         {              /* Saturn,  Uranus,  or Neptune? */
         if( r2 < SATURN_OUTER_LIMIT * SATURN_OUTER_LIMIT)
            planet_to_check = 6;
         else if( r2 > URANUS_INNER_LIMIT * URANUS_INNER_LIMIT)
            {
            if( r2 < URANUS_OUTER_LIMIT * URANUS_OUTER_LIMIT)
               planet_to_check = 7;
            else if( r2 > NEPTUNE_INNER_LIMIT * NEPTUNE_INNER_LIMIT &&
                        r2 < NEPTUNE_OUTER_LIMIT * NEPTUNE_OUTER_LIMIT)
               planet_to_check = 8;
            }
         }
      }
   else        /* check inner planets */
      if( r2 < EARTH_OUTER_LIMIT * EARTH_OUTER_LIMIT)
         {
         if( r2 > EARTH_INNER_LIMIT * EARTH_INNER_LIMIT)
            planet_to_check = 3;
         else if( r2 > VENUS_INNER_LIMIT * VENUS_INNER_LIMIT)
            {
            if( r2 < VENUS_OUTER_LIMIT * VENUS_OUTER_LIMIT)
               planet_to_check = 2;
            }
         else if( r2 < MERCURY_OUTER_LIMIT * MERCURY_OUTER_LIMIT &&
                  r2 > MERCURY_INNER_LIMIT * MERCURY_INNER_LIMIT)
            planet_to_check = 1;
         }
      else if( r2 < MARS_OUTER_LIMIT * MARS_OUTER_LIMIT &&
               r2 > MARS_INNER_LIMIT * MARS_INNER_LIMIT)
         planet_to_check = 4;

// printf( "r2 = %lf, planet_to_check = %d\n", r2, planet_to_check);
   for( axis = 3; planet_to_check && axis > 0; axis--)
      {
      double delta = -vect[axis - 1];
      int i;
      const SMALL_VSOP_TERM *vptr = vsop_terms[planet_to_check];
      const double ranges[9] = {0., MERCURY_RANGE, VENUS_RANGE, EARTH_RANGE,
                  MARS_RANGE, JUPITER_RANGE, SATURN_RANGE,
                  URANUS_RANGE, NEPTUNE_RANGE };

      if( axis == 3)
         delta += vptr->freq;
      else if( axis == 2)
         delta += vptr->phase;
      else if( axis == 1)
         delta += vptr->amplitude;
      vptr++;
      for( i = n_terms[planet_to_check] - 1; i; i--, vptr++)
         if( vptr->axis == axis)
            delta += vptr->amplitude * cos( vptr->phase + vptr->freq * t_cen);
//    printf( "Axis %d, delta %lf, range %lf\n", axis, delta, ranges[planet_to_check]);
//                   /* Is the difference delta within limits? */
      if( delta > ranges[planet_to_check] || delta < -ranges[planet_to_check])
         planet_to_check = 0;
      }
   return( planet_to_check);
}

#ifdef TEST_MAIN
#include <stdio.h>

void main( int argc, char **argv)
{
   const double jd = atof( argv[1]);
   const double t_cen = (jd - 2451545.) / 36525.;
   double vect[3];
   int i;

   for( i = 1; i < 9; i++)
      {
      compute_rough_planet_loc( t_cen, i, vect);
      printf( "%d   %8.4lf %8.4lf %8.4lf\n", i, vect[0], vect[1], vect[2]);
      }
   if( argc >= 5)
      {
      for( i = 0; i < 3; i++)
         vect[i] = atof( argv[i + 2]);
      printf( "Perturber = %d\n", check_for_perturbers( t_cen, vect));
      }
}
#endif
