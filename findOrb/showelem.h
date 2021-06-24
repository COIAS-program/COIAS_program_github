#define SHOWELEM_PRECISION_MASK      0x0f
#define SHOWELEM_PERIH_TIME_MASK     0x10
#define SHOWELEM_OMIT_PQ_MASK        0x20
#define SHOWELEM_COMET_MAGS_NUCLEAR  0x40

/* REMEMBER:  set 'central_obj', 'epoch', 'abs_mag', 'slope_param' fields */

int DLL_FUNC elements_in_mpc_format( char *obuff, const ELEMENTS *elem,
                const char *obj_id, const int is_cometary, const int format);
