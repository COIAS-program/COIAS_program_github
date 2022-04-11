#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include "lsquare.h"

#ifdef DEBUG_MEM
#include "checkmem.h"
#endif

#define LSQUARE struct lsquare

LSQUARE
   {
   int n_params, n_obs;
   double *wtw, *uw;
   };

void *lsquare_init( const int n_params)
{
   LSQUARE *rval = (LSQUARE *)calloc( 1,
          sizeof( LSQUARE) + n_params * (n_params + 1) * sizeof( double));

   if( !rval)
      return( (void *)rval);
   rval->n_params = n_params;
   rval->n_obs = 0;
   rval->uw = (double *)( rval + 1);
   rval->wtw = rval->uw + n_params;
   return(( void *)rval);
}

int lsquare_add_observation( void *lsquare, const double residual,
                                  const double weight, const double *obs)
{
   LSQUARE *lsq = (LSQUARE *)lsquare;
   int i, j;
   const int n_params = lsq->n_params;

   for( i = 0; i < n_params; i++)
      {
      const double w2_obs_i = weight * weight * obs[i];

      lsq->uw[i] += residual * w2_obs_i;
      for( j = 0; j < n_params; j++)
         lsq->wtw[i + j * n_params] += w2_obs_i * obs[j];
      }
   lsq->n_obs++;
   return( lsq->n_obs);
}

double lsquare_determinant;

static double *calc_inverse( const double *src, const int size)
{
   double *rval;
   double *temp = (double *)calloc( 2 * size * size, sizeof( double)), *tptr;
   double *tptr1, *tptr2, tval;
   int i, j, k;
   const int dsize = 2 * size;

   lsquare_determinant = 1.;
   if( !temp)
      return( NULL);
   for( i = 0; i < size; i++)
      {
      tptr = temp + i * dsize;
      memcpy( tptr, src + i * size, size * sizeof( double));
      tptr += size;
      for( j = 0; j < size; j++)
         *tptr++ = ((i == j) ? 1. : 0.);
      }

   tptr1 = temp;
   for( i = 0; i < size; i++, tptr1 += dsize)
      {
      int pivot = -1;
      double best_val = 0.;

      tptr = tptr1;
      for( j = i; j < size; j++, tptr += dsize)
         if( fabs( tptr[i]) > best_val)
            {
            best_val = fabs( tptr[i]);
            pivot = j;
            }

      if( pivot == -1)
         {
         free( temp);
         return( NULL);
         }

      if( pivot != i)                  /* swap rows */
         {
         tptr2 = temp + dsize * pivot;
         for( j = i; j < dsize; j++)
            {
            tval = tptr1[j];
            tptr1[j] = tptr2[j];
            tptr2[j] = tval;
            }
         }

      for( j = i + 1; j < size; j++)
         {
         tptr2 = temp + dsize * j;
         tval = tptr2[i] / tptr1[i];
         for( k = i; k < dsize; k++)
            tptr2[k] -= tptr1[k] * tval;
         }
      }
                  /* the lower left triangle is now cleared... */

   for( i = size - 1; i >= 0; i--)
      {
      tptr1 = temp + i * dsize;
      for( j = size; j < dsize; j++)
         {
         lsquare_determinant /= tptr1[i];
         tptr1[j] /= tptr1[i];
         }
      tptr2 = temp;
      for( k = 0; k < i; k++, tptr2 += dsize)
         for( j = size; j < dsize; j++)
            tptr2[j] -= tptr2[i] * tptr1[j];
      }

   rval = (double *)calloc( size * size, sizeof( double));
   if( rval)
      for( i = 0; i < size; i++)
         memcpy( rval + i * size, temp + (i * 2 + 1) * size,
                                       size * sizeof( double));
   free( temp);
   return( rval);
}

static void mult_matrices( double *prod, const double *a, const int awidth,
                  const int aheight, const double *b, const int bwidth)
{
   int i, j;

   for( j = 0; j < aheight; j++)
      for( i = 0; i < bwidth; i++, prod++)
         {
         int k;
         const double *aptr = a + j * awidth, *bptr = b + i;

         *prod = 0.;
         for( k = awidth; k; k--, bptr += bwidth)
            *prod += *aptr++ * (*bptr);
         }
}

#ifdef LSQUARE_ERROR
static void dump_matrix( FILE *ofile, const double *matrix, const int size)
{
   int i;
   double largest_element = 0.;

   for( i = 0; i < size * size; i++)
      {
      if( largest_element < fabs( *matrix))
         largest_element = fabs( *matrix);
      fprintf( ofile, "%11.2e%s", *matrix++, !((i + 1) % size) ? "\n" : "");
      }
   fprintf( ofile, "Largest element: %11.2e\n", largest_element);
}
#endif

static double *calc_inverse_improved( const double *src, const int size)
{
   double *inverse = calc_inverse( src, size);

   if( inverse)
      {
      double *err_mat = (double *)calloc( 2 * size * size, sizeof( double));
      double *b_times_delta = err_mat + size * size;
      int i;
#ifdef LSQUARE_ERROR
      FILE *ofile = fopen( "lsquare.dat", "ab");
#endif

      mult_matrices( err_mat, src, size, size, inverse, size);
      for( i = 0; i < size; i++)
         err_mat[i * (size + 1)] -= 1.;
#ifdef LSQUARE_ERROR
      fprintf( ofile, "%d-square matrix delta (= I - AB):\n", size);
      dump_matrix( ofile, err_mat, size);
      fclose( ofile);
#endif
      mult_matrices( b_times_delta, inverse, size, size, err_mat, size);
      for( i = 0; i < size * size; i++)
         inverse[i] -= b_times_delta[i];
      free( err_mat);
      }
   return( inverse);
}

int lsquare_solve( const void *lsquare, double *result)
{
   const LSQUARE *lsq = (const LSQUARE *)lsquare;
   int i, j, n_params = lsq->n_params;
   double *inverse;

   if( n_params > lsq->n_obs)       /* not enough observations yet */
      return( -1);

// inverse = calc_inverse( lsq->wtw, n_params);
   inverse = calc_inverse_improved( lsq->wtw, n_params);
   if( !inverse)
      return( -2);            /* couldn't invert matrix */

   for( i = 0; i < n_params; i++)
      result[i] = 0.;

   for( i = 0; i < n_params; i++)
      for( j = 0; j < n_params; j++)
         result[i] += inverse[i + j * n_params] * lsq->uw[j];

   free( inverse);
   return( 0);
}

double *lsquare_covariance_matrix( const void *lsquare)
{
   const LSQUARE *lsq = (const LSQUARE *)lsquare;
   double *rval = NULL;

   if( lsq->n_params <= lsq->n_obs)       /* got enough observations */
      rval = calc_inverse_improved( lsq->wtw, lsq->n_params);
   return( rval);
}

void lsquare_free( void *lsquare)
{
   free( lsquare);
}

#if 0
#include <stdio.h>

void main( int argc, char **argv)
{
   FILE *ifile = fopen( "imatrix", "rb");
   int size, i, j;
   double *matrix, *inv;

   fscanf( ifile, "%d", &size);
   matrix = (double *)calloc( size * size, sizeof( double));
   for( i = 0; i < size * size; i++)
      fscanf( ifile, "%lf", matrix + i);
   inv = calc_inverse_improved( matrix, size);
   for( i = 0; i < size; i++)
      {
      printf( "\n");
      for( j = 0; j < size; j++)
         printf( "%10.5lf", *inv++);
      }
}
#endif
