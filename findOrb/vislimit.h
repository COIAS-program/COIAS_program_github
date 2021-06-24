#define BRIGHTNESS_DATA struct brightness_data

#pragma pack(4)
BRIGHTNESS_DATA
   {
               /* constants for a given time: */
   double zenith_ang_moon, zenith_ang_sun, moon_elongation;
   double ht_above_sea_in_meters, latitude;
   double temperature_in_c, relative_humidity;
   double year, month;
               /* values varying across the sky: */
   double zenith_angle;
   double dist_moon, dist_sun;         /* angular,  not real linear */
   int mask;   /* indicates which of the 5 photometric bands we want */
               /* Items computed in set_brightness_params: */
   double air_mass_sun, air_mass_moon, lunar_mag;
   double k[5], c3[5], c4[5], ka[5], kr[5], ko[5], kw[5];
   double year_term;
               /* Items computed in compute_limiting_mag: */
   double air_mass_gas, air_mass_aerosol, air_mass_ozone;
   double extinction[5]; 
               /* Internal parameters from compute_sky_brightness: */
   double air_mass;
   double brightness[5];
   };
#pragma pack( )

#ifndef DLL_FUNC
#ifdef _WIN32
#define DLL_FUNC __stdcall
#else
#define DLL_FUNC
#endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

int DLL_FUNC set_brightness_params( BRIGHTNESS_DATA *b);
int DLL_FUNC compute_sky_brightness( BRIGHTNESS_DATA *b);
double DLL_FUNC compute_limiting_mag( BRIGHTNESS_DATA *b);
int DLL_FUNC compute_extinction( BRIGHTNESS_DATA *b);

#ifdef __cplusplus
}
#endif
