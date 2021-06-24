double v_minus_i_to_b_minus_v( const double v_minus_i);         /* colors.c */
double b_minus_v_to_v_minus_i( const double b_minus_v);         /* colors.c */
double v_minus_i_to_v_minus_r( const double v_minus_i);         /* colors.c */
double v_minus_r_to_v_minus_i( const double v_minus_r);         /* colors.c */
double v_minus_r_to_b_minus_v( const double v_minus_r);         /* colors.c */
double b_minus_v_to_v_minus_r( const double b_minus_v);         /* colors.c */
double johnson_b_minus_v_from_tycho_b_minus_v( const double b_v_t);
double johnson_v_from_tycho_b_minus_v( const double b_v_t, const double tycho_v);
int tycho_to_johnson_colors( double bt_minus_vt, double *results);
