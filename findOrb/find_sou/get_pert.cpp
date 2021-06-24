#include <stdio.h>
#include <stdlib.h>
#ifdef _MSC_VER            /* Microsoft Visual C/C++ lacks a 'stdint.h'; */
#include "stdintvc.h"      /* 'stdintvc.h' is a replacement version      */
#else
#include <stdint.h>
#endif
#include "watdefs.h"
#include "comets.h"

/* Code to get asteroid elements for (1) Ceres, (2) Pallas,  and/or (4)
Vesta.

   The main problem I had in adding asteroid perturbations to Find_Orb was
in computing their positions at semi-arbitrary times.  You can use the
DE ephemerides or a series solution to get planetary and lunar positions
at any desired time,  and there are analytic theories for other planetary
satellites.  But in general,  if you want to know where an asteroid was
on a given date,  you have to integrate its orbit.

   To duck around that,  I used the JPL _Horizons_ system to compute
orbital elements,  at 200-day intervals,  for the years 1800 to 2100,
for a total of 731 sets of elements.  That got me the data in a rather
enormous text file (three of them,  actually,  one each for Ceres,  Pallas,
and Vesta).  Within that time span,  I could be sure of having elements
with 100 days (worst case;  50 days on average).  A two-body solution
ignoring those 100 days of perturbations will work just fine.

   I then compressed the elements to consume six long integers (24 bytes)
each.  (This is a recycling of code I used in _Guide_,  which uses a
similar system for _all_ asteroids.)  That way,  the file size was reduced
to (3 objects) * (731 element sets/object) * (24 bytes/element set) =
52632 bytes.  The file 'ast_pert.dat' isn't actually _that_ small,  because
it has some header data specifying which asteroids are present,  the time
span covered,  and their masses.  I included all this in part because it's
possible I'll want to include other asteroids at some point,  perhaps in
a project to do mass determinations. */

int get_asteroid_perturber_elems( ELEMENTS *elem,        /* get_pert.cpp */
                  const double jd, const int perturber_no);

/* get_perturber_elems( ) is the low-level function that looks in a file
for elements for a given perturber at a given time.  The range for which
they are to be used spans from jd_range[0] to jd_range[1].

   Elements are _always_ returned;  if we're before the start of the
range of the elements,  the first set of elements is returned,  and
jd_range[0] = -1e+20.  If we're past the range of the elements,  the
last set of elements is returned,  and jd_range[1] = +1e+20.  In between,
elements cover 200-day spans,  so jd_range[1] = jd_range[0] + 200.   The
elements are returned in six packed long integers.  jd_range[2] returns
the epoch of the elements. */

static int get_perturber_elems( uint32_t *packed_elems, FILE *ifile,
            const int perturber, const double jd, double *jd_range)
{
   char buff[40];
   double step_size, starting_jd;
   long offset = 385L;
   int i, rec_no, max_rec;

   fseek( ifile, 0L, SEEK_SET);
   for( i = 0; i <= perturber && fgets( buff, sizeof( buff), ifile); i++)
      if( i != perturber)
         offset += 24L * atol( buff + 15);
   if( i != perturber)
      return( -2);         /* didn't read all lines */
   step_size = atof( buff + 19);
   starting_jd = atof( buff + 6);
   rec_no = (int)( (jd - starting_jd) / step_size + .5);
   if( rec_no < 0)
      rec_no = 0;
   max_rec = atoi( buff + 15) - 1;
   if( rec_no > max_rec)
      rec_no = max_rec;
   offset += 24L * rec_no;
   fseek( ifile, offset, SEEK_SET);
   if( fread( packed_elems, sizeof( uint32_t), 6, ifile) != 6)
      return( -1);
         /* If we're on non-Intel hardware,  these uint32_ts need to */
         /* be byte-swapped!               */
   if( jd_range)
      {
      jd_range[2] = starting_jd + (double)rec_no * step_size;
      jd_range[0] = jd_range[2] - step_size / 2.;
      jd_range[1] = jd_range[0] + step_size;
      if( !rec_no)
         jd_range[0] = -1.e+20;
      else if( rec_no == max_rec)
         jd_range[1] = 1.e+20;
      }
   return( 0);
}

#define N_CACHED_ELEMS 8
#define CACHED_ASTEROID_ELEMS struct cached_asteroid_elems

CACHED_ASTEROID_ELEMS
   {
   double jd_range[3];
   int perturber_no;
   uint32_t elems[6];
   };

/* get_asteroid_perturber_elems( ) is the function used by the outside
world.  It checks to see if it already has usable elements in its cache;
if it doesn't,  it fetches them using get_perturber_elems( ).  In the
cache,  elements are stored in the six-byte long integer format. */

int get_asteroid_perturber_elems( ELEMENTS *elem,
                          const double jd, const int perturber_no)
{
   static CACHED_ASTEROID_ELEMS cache[N_CACHED_ELEMS];
   static int n_cached = 0;
   int entry_no = -1, i;

   if( n_cached == -1)        /* no perturbers available;  can stop now */
      return( -1);

   for( i = 0; i < n_cached; i++)
      if( jd >= cache[i].jd_range[0] && jd <= cache[i].jd_range[1] &&
                                    perturber_no == cache[i].perturber_no)
         entry_no = i;

   if( entry_no == -1)        /* not in cache;  look in file */
      {
      FILE *ifile = fopen( "ast_pert.dat", "rb");

      if( !ifile)           /* wups!  don't have an asteroid perturber file */
         {
         n_cached = -1;
         return( -1);
         }
      else
         {
         if( n_cached < N_CACHED_ELEMS)
            n_cached++;
         entry_no = n_cached - 1;
         get_perturber_elems( cache[entry_no].elems, ifile,
                        perturber_no, jd, cache[entry_no].jd_range);
         cache[entry_no].perturber_no = perturber_no;
         fclose( ifile);
         }
      }
   if( entry_no)
      {
      CACHED_ASTEROID_ELEMS swap_temp = cache[entry_no];

      cache[entry_no] = cache[0];
      cache[0] = swap_temp;
      }
   setup_elems_from_ast_file( elem, cache[0].elems, cache[0].jd_range[2]);
   return( 0);
}

#ifdef TEST_MAIN

#include <string.h>

/* The following 'test' main reads in elements for a given asteorid
(number specified on the command line) for a given epoch (specified as
a JD on the command line).  It then outputs those elements in the
8-line MPC format. */

int DLL_FUNC elements_in_mpc_format( char *obuff, const ELEMENTS *elem,
                const char *obj_id, const int is_cometary, const int format);

void main( int argc, char **argv)
{
   ELEMENTS elem;
   char buff[800], *tptr = buff;
   int n_lines;

   memset( &elem, sizeof( ELEMENTS), 0);
   get_asteroid_perturber_elems( &elem, atof( argv[1]), atoi( argv[2]));
   n_lines = elements_in_mpc_format( buff, &elem, "Harry", 0, 0);
   while( n_lines--)
      {
      printf( "%s\n", tptr);
      tptr += strlen( tptr) + 1;
      }
}
#endif
