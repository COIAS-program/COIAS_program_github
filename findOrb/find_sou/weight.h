int load_up_weight_records( const char *filename);
void free_weight_recs( void);
double get_observation_weight( const double jd, const int mag_in_tenths,
                  const char *mpc_code);
