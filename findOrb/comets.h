#define ELEMENTS struct elements

#pragma pack(4)
ELEMENTS
   {
   double perih_time, q, ecc, incl, arg_per, asc_node;
   double epoch,  mean_anomaly;
            /* derived quantities: */
   double lon_per, minor_to_major;
   double perih_vec[3], sideways[3];
   double angular_momentum, major_axis, t0, w0;
   double abs_mag, slope_param;
   int is_asteroid, central_obj;
   };
#pragma pack( )

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _MSC_VER            /* Microsoft Visual C/C++ lacks a 'stdint.h'; */
#include "stdintvc.h"      /* 'stdintvc.h' is a replacement version      */
#else
#include <stdint.h>
#endif

// void calc_vectors( ELEMENTS *elem, const double sqrt_gm);
int DLL_FUNC calc_classical_elements( ELEMENTS *elem, const double *r,
                             const double t, const int ref, const double gm);
int calc_posn_and_vel( double *r, ELEMENTS *elem, double t, double sqrt_gm);
         /* Above is still in use by PERTURB... hope to eliminate it soon */
int DLL_FUNC comet_posn_and_vel( ELEMENTS DLLPTR *elem, double t,
                  double DLLPTR *loc, double DLLPTR *vel);
int DLL_FUNC comet_posn( ELEMENTS DLLPTR *elem, double t, double DLLPTR *loc);       /* astfuncs.c */
void DLL_FUNC derive_quantities( ELEMENTS DLLPTR *e, const double gm);
int DLL_FUNC setup_elems_from_ast_file( ELEMENTS DLLPTR *class_elem,
              const uint32_t DLLPTR *elem, const double t_epoch);

#ifdef __cplusplus
}
#endif
