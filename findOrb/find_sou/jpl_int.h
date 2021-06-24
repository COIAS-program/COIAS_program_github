/* Right now,  DEs 403 and 405 have the maximum kernel size,  of 2036.    */
/* This value may need to be updated the next time JPL releases a new DE: */

#define MAX_KERNEL_SIZE 2036

/***** THERE IS NO NEED TO MODIFY THE REST OF THIS SOURCE (I hope) *********/

            /* A JPL binary ephemeris header contains five doubles and */
            /* (up to) 41 int32_t integers,  so:                          */
#define JPL_HEADER_SIZE (5 * sizeof( double) + 41 * sizeof( int32_t))

#pragma pack(1)

struct jpl_eph_data {
   double ephem_start, ephem_end, ephem_step;
   int32_t ncon;
   double au;
   double emrat;
   int32_t ipt[13][3];
   int32_t ephemeris_version;
   int32_t kernel_size, recsize, ncoeff;
   int32_t swap_bytes;
   int32_t curr_cache_loc;
   double pvsun[6];
   double *cache;
   void *iinfo;
   FILE *ifile;
   };
#pragma pack()

struct interpolation_info
   {
   double pc[18],vc[18], twot;
   int np, nv;
   };

