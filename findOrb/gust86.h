/* Output state vector is in AU and AU/second */

#ifndef __stdcall
#define __stdcall
#endif

#ifdef __cplusplus
extern "C" {
#endif
void __stdcall gust86_posn( const double jde, const int isat, double *r );
#ifdef __cplusplus
}
#endif

#define GUST86_ARIEL          0
#define GUST86_UMBRIEL        1
#define GUST86_TITANIA        2
#define GUST86_OBERON         3
#define GUST86_MIRANDA        4
