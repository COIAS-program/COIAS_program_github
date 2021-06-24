/* ROCKS.CPP

   This code generates positions for "rocks" (faint inner satellites
that can be modelled,  at least passably well,  as precessing ellipses).
The currently listed "rocks" are:

  505:         Amalthea     706: 1986U7 Cordelia   801: Triton (Neptune I)
  514: 1979J2  Thebe        707: 1986U8 Ophelia    803: 1989 N6 Naiad
  515: 1979J1  Adrastea     708: 1986U9 Bianca     804: 1989 N5 Thalassa
  516: 1979J3  Metis        709: 1986U3 Cressida   805: 1989 N3 Despina
                            710: 1986U6 Desdemona  806: 1989 N4 Galatea
  610: Janus      (+)       711: 1986U2 Juliet     807: 1989 N2 Larissa
  611: Epimetheus (+)       712: 1986U1 Portia     808: 1989 N1 Proteus
  612: Helene     (+)       713: 1986U4 Rosalind
  613: Telesto    (+)       714: 1986U5 Belinda
  614: Calypso    (+)       715: 1986U1 Puck
  615: 1980S28 Atlas        725: 1986U10 = Perdita       401: Phobos (+)
  616: 1980S27 Prometheus   726: Mab (+)                 402: Deimos (+)
  617: 1980S26 Pandora      727: Cupid (+)
  618: 1981S13 Pan
  635: Daphnis (+)

   The orbital elements were provided by Mark Showalter (some updates from
Bob Jacobson),  along with the following comments:

(1) The listing refers to JPL ephemeris IDs JUP120, SAT080, URA039, and
NEP022(*).  If you select the SPICE ephemerides of the same name in
Horizons, then you really should get almost identical results, because
the SPICE files were generated using these exact elements.

(2) Be aware that Saturn's moons Prometheus and Pandora are exhibiting
peculiar variations in longitude that are not currently understood,
probably related to interactions with the other nearby moons and rings.
So don't expect your results for these bodies to be particularly
accurate.

Regards, Mark Showalter

  -------------------------

(+) Data is provided for this object,  but I've not tried it out in Guide yet.

(*) replaced with JUP250 data 3 Nov 2007,  NEP050 data 8 Jan 2008
(and Triton added),  URA086X on 8 Jan 2008, MAR080 on 13 Feb 2009.
Some others updated as noted in comments.

*/

#include <math.h>

#define ROCK struct rock

ROCK
   {
   int jpl_id;
   double epoch_jd, a, h, k, mean_lon0, p, q, apsis_rate, mean_motion;
   double node_rate, laplacian_pole_ra, laplacian_pole_dec;
   };

#define PI 3.14159265358979323846264338327950288
#define N_ROCKS 36

static const ROCK rocks[N_ROCKS] = {
   {  401,             /* Phobos: MAR080 data */
      2433282.50,                           /* element epoch Julian date     */
       9.376164153345777E+03,               /* a = semi-major axis (km)      */
      -5.689907327111091E-04,               /* h = e sin(periapsis longitude)*/
       1.508976478046249E-02,               /* k = e cos(periapsis longitude)*/
       8.889912565234037E+01 * PI / 180.,   /* l = mean longitude (deg)      */
      -4.374861644190954E-03,               /* p = tan(i/2) sin(node)        */
      -8.303312581096576E-03,               /* q = tan(i/2) cos(node)        */
       5.037011787882128E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.306533283449532E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -5.043841563630776E-06 * PI / 180.,   /* node rate (deg/sec)           */
       3.176707407767539E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       5.289299367003886E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   {  402,             /* Deimos:  MAR080 data */
      2433282.50,                           /* element epoch Julian date     */
       2.345766038183417E+04,               /* a = semi-major axis (km)      */
      -2.390285567613731E-04,               /* h = e sin(periapsis longitude)*/
       6.518182753851608E-05,               /* k = e cos(periapsis longitude)*/
       2.505824379527014E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       6.477849519349295E-03,               /* p = tan(i/2) sin(node)        */
       1.419810985499536E-02,               /* q = tan(i/2) cos(node)        */
       2.076162603566793E-07 * PI / 180.,   /* apsis rate (deg/sec)          */
       3.300484710930912E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.091750616728367E-07 * PI / 180.,   /* node rate (deg/sec)           */
       3.166569791010836E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       5.352937471037383E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    {  505,            /* Amalthea: JUP250 */
       2450000.500000000,                   /* element epoch Julian date     */
       1.813655512465877E+05,               /* a = semi-major axis (km)      */
       3.524243705442326E-04,               /* h = e sin(periapsis longitude)*/
      -3.060388597797567E-03,               /* k = e cos(periapsis longitude)*/
       3.088979995508090E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -8.524633361449484E-04,               /* p = tan(i/2) sin(node)        */
      -3.277584681172060E-03,               /* q = tan(i/2) cos(node)        */
       2.908651473226303E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       8.363792987058621E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.898772964219916E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.680573067077756E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       6.449433514883954E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 514,                /* Thebe: JUP250 */
      2450000.500000000,                    /* element epoch Julian date     */
       2.218882574500956E+05,               /* a = semi-major axis (km)      */
      -1.707742712451856E-02,               /* h = e sin(periapsis longitude)*/
      -4.631931271882844E-03,               /* k = e cos(periapsis longitude)*/
       2.889925861272768E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       9.336528660574965E-03,               /* p = tan(i/2) sin(node)        */
       7.503268096368817E-05,               /* q = tan(i/2) cos(node)        */
       1.433399183927280E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.177086242379696E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.430832006152276E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.680573566856980E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       6.449436369487705E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 515,           /* Adrastea: JUP250 */
      2450000.500000000,                    /* element epoch Julian date     */
       1.289847619277409E+05,               /* a = semi-major axis (km)      */
       7.733436951055491E-05,               /* h = e sin(periapsis longitude)*/
      -7.119915620542968E-04,               /* k = e cos(periapsis longitude)*/
       8.469076821476101E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       7.291459020134167E-04,               /* p = tan(i/2) sin(node)        */
       2.676849686756846E-04,               /* q = tan(i/2) cos(node)        */
       9.721724518582802E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.396989430143032E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -9.865593193437598E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.680565964128937E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       6.449530295172036E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 516,           /* Metis: JUP250 */
      2450000.500000000,                    /* element epoch Julian date     */
       1.279996083074168E+05,               /* a = semi-major axis (km)      */
       4.232619343306958E-04,               /* h = e sin(periapsis longitude)*/
      -6.389823783865655E-04,               /* k = e cos(periapsis longitude)*/
       3.380483431923231E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       2.332741944310790E-04,               /* p = tan(i/2) sin(node)        */
       5.651570478951611E-04,               /* q = tan(i/2) cos(node)        */
       9.905391637419158E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.413489189624821E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -9.817915317723091E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.680565964128937E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       6.449530295172036E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 610,      /* Janus:  SAT080 data */
      2444786.5,                            /* element epoch Julian date     */
       1.514471646942220E+05,               /* a = semi-major axis (km)      */
      -3.356112346396347E-03,               /* h = e sin(periapsis longitude)*/
       5.663424289609894E-03,               /* k = e cos(periapsis longitude)*/
       1.993639755564592E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -1.210639146126198E-03,               /* p = tan(i/2) sin(node)        */
       8.350119519512047E-04,               /* q = tan(i/2) cos(node)        */
       2.378317712273239E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       5.998806000756397E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.367392401124433E-05 * PI / 180.,   /* node rate (deg/sec)           */
       4.057999864473820E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353999955183330E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 611,      /* Epimetheus:  SAT080 data */
      2444786.5,                            /* element epoch Julian date     */
       1.513991905498270E+05,               /* a = semi-major axis (km)      */
       1.244955044467311E-02,               /* h = e sin(periapsis longitude)*/
       1.689723618147796E-03,               /* k = e cos(periapsis longitude)*/
       1.438890791888553E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -1.212371038828309E-03,               /* p = tan(i/2) sin(node)        */
       2.571443713031926E-03,               /* q = tan(i/2) cos(node)        */
       2.379040740977320E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.001665785000491E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.367577385695356E-05 * PI / 180.,   /* node rate (deg/sec)           */
       4.057999864473820E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353999955183330E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 612,      /* Helene:  SAT080 data */
      2444786.5,                            /* element epoch Julian date     */
       3.774166381879790E+05,               /* a = semi-major axis (km)      */
      -9.353516152747377E-05,               /* h = e sin(periapsis longitude)*/
       1.583034918343283E-03,               /* k = e cos(periapsis longitude)*/
       1.006212707258068E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       3.230333151378729E-04,               /* p = tan(i/2) sin(node)        */
       1.710869900001995E-03,               /* q = tan(i/2) cos(node)        */
      -6.777890900303528E-07 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.522394989535369E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -9.680289928992843E-07 * PI / 180.,   /* node rate (deg/sec)           */
       4.057615013244320E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.354534172579820E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 613,      /* Telesto:  SAT080 data */
      2444786.5,                            /* element epoch Julian date     */
       2.946735826892260E+05,               /* a = semi-major axis (km)      */
      -5.228888695475952E-04,               /* h = e sin(periapsis longitude)*/
      -6.853986134369704E-04,               /* k = e cos(periapsis longitude)*/
       2.150026475454563E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       8.124186851739944E-03,               /* p = tan(i/2) sin(node)        */
      -5.785202572889351E-03,               /* q = tan(i/2) cos(node)        */
       2.297061650453675E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       2.207149546064677E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.290176906415847E-06 * PI / 180.,   /* node rate (deg/sec)           */
       4.057999864473820E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353999955183330E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 614,      /* Calypso:  SAT080 data */
      2444786.5,                            /* element epoch Julian date     */
       2.946734418892560E+05,               /* a = semi-major axis (km)      */
       2.900726601141678E-05,               /* h = e sin(periapsis longitude)*/
      -1.805642558770706E-04,               /* k = e cos(periapsis longitude)*/
       9.486345898172432E+01 * PI / 180.,   /* l = mean longitude (deg)      */
      -6.373255324934580E-03,               /* p = tan(i/2) sin(node)        */
      -1.114711641632123E-02,               /* q = tan(i/2) cos(node)        */
       2.297022164277979E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       2.207149553889344E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.289705897532556E-06 * PI / 180.,   /* node rate (deg/sec)           */
       4.057999864473820E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353999955183330E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 615,           /* Atlas: SAT080 data */
      2444786.50,                           /* element epoch Julian date     */
       1.376664620000000E+05,               /* a = semi-major axis (km)      */
       0.000000000000000E+00,               /* h = e sin(periapsis longitude)*/
       0.000000000000000E+00,               /* k = e cos(periapsis longitude)*/
       1.865410967364615E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       0.000000000000000E+00,               /* p = tan(i/2) sin(node)        */
       0.000000000000000E+00,               /* q = tan(i/2) cos(node)        */
       3.334584985561025E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.924845572071244E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.318681015315788E-05 * PI / 180.,   /* node rate (deg/sec)           */
       4.058861887893110E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.352533375484340E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 616,              /* Prometheus: SAT127 data */
      2444940.,                       /* element epoch Julian date     */
       1.393776240E+5,                /* a = semi-major axis (km)      */
      -1.870790E-3,                   /* h = e sin(periapsis longitude)*/
      -4.319060E-4,                   /* k = e cos(periapsis longitude)*/
       339.155 * PI / 180.,           /* l = mean longitude (deg)      */
       0.0,                           /* p = tan(i/2) sin(node)        */
       0.0,                           /* q = tan(i/2) cos(node)        */
       3.191398148E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.797308681E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.191398148E-05 * PI / 180.,   /* node rate (deg/sec)           */
       40.5955         * PI / 180.,   /* Laplacian plane pole ra (deg) */
       83.53812        * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 617,              /* Pandora: SAT127 data */
      2444940.0,                            /* element epoch Julian date     */
       1.417131075E+05,               /* a = semi-major axis (km)      */
      -7.853582898E-05,               /* h = e sin(periapsis longitude)*/
       4.499314628E-03,               /* k = e cos(periapsis longitude)*/
       96.023          * PI / 180.,   /* l = mean longitude (deg)      */
       0.000000000E+00,               /* p = tan(i/2) sin(node)        */
       0.000000000E+00,               /* q = tan(i/2) cos(node)        */
       3.008501157E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.629462963E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.008501157E-05 * PI / 180.,   /* node rate (deg/sec)           */
       40.5955         * PI / 180.,   /* Laplacian plane pole ra (deg) */
       83.53812        * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 618,      /* Pan: SAT291 data */
      2451545.,                             /* element epoch Julian date     */
       1.335844266338847E+05,               /* a = semi-major axis (km)      */
      -8.643034594633570E-08,               /* h = e sin(periapsis longitude)*/
      -7.016794165866033E-06,               /* k = e cos(periapsis longitude)*/
       1.465967563599653E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       2.373283544887851E-06,               /* p = tan(i/2) sin(node)        */
       1.930502263049383E-06,               /* q = tan(i/2) cos(node)        */
       3.707485545660000E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       7.245737650483481E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.688416608906115E-05 * PI / 180.,   /* node rate (deg/sec)           */
       4.058210938819655E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353764539058524E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 635,      /* Daphnis: SAT291 data */
      2453491.914120370,                    /* element epoch Julian date     */
       1.365055479974113E+05,               /* a = semi-major axis (km)      */
       3.342707916499629E-05,               /* h = e sin(periapsis longitude)*/
       1.607484388141352E-05,               /* k = e cos(periapsis longitude)*/
       2.229482858404000E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       1.926317848761353E-05,               /* p = tan(i/2) sin(node)        */
      -2.359648608882712E-05,               /* q = tan(i/2) cos(node)        */
       3.490324559958422E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       7.013647706058515E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.417545198164673E-05 * PI / 180.,   /* node rate (deg/sec)           */
       4.058210938819655E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       8.353764539058524E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 706,   /* Cordelia: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       4.975226513768263E+04,               /* a = semi-major axis (km)      */
      -3.382827956730996E-05,               /* h = e sin(periapsis longitude)*/
      -2.379773334714911E-04,               /* k = e cos(periapsis longitude)*/
       7.000400382154136E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       3.444190898489106E-04,               /* p = tan(i/2) sin(node)        */
       4.811906514485254E-04,               /* q = tan(i/2) cos(node)        */
       1.738799696981362E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.243657356363762E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.736377492435019E-05 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 707,    /* Ophelia: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       5.376756832000196E+04,               /* a = semi-major axis (km)      */
      -3.588254484691443E-04,               /* h = e sin(periapsis longitude)*/
      -9.963069487737418E-03,               /* k = e cos(periapsis longitude)*/
       2.980833019182993E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       1.039466856471680E-04,               /* p = tan(i/2) sin(node)        */
      -5.415474417983882E-04,               /* q = tan(i/2) cos(node)        */
       1.324712040631912E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.106965982985822E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.323133607399601E-05 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 708,    /* Bianca: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       5.916600622843648E+04,               /* a = semi-major axis (km)      */
       7.907724012720749E-04,               /* h = e sin(periapsis longitude)*/
      -1.914431544380098E-04,               /* k = e cos(periapsis longitude)*/
       2.400006327016626E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       1.583149484871827E-03,               /* p = tan(i/2) sin(node)        */
       8.479741043373598E-05,               /* q = tan(i/2) cos(node)        */
       9.467105548594393E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       9.587823195724045E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -9.457950543934906E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 709,    /* Cressida: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       6.176700384106977E+04,               /* a = semi-major axis (km)      */
       7.347344576265666E-05,               /* h = e sin(periapsis longitude)*/
      -3.104096618505799E-04,               /* k = e cos(periapsis longitude)*/
       1.744155419168578E+01 * PI / 180.,   /* l = mean longitude (deg)      */
      -8.444272409392927E-05,               /* p = tan(i/2) sin(node)        */
      -3.081728314296660E-05,               /* q = tan(i/2) cos(node)        */
       8.142357893631056E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       8.988222148947005E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -8.135007925901379E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 710,   /* Desdemona: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       6.265800854041584E+04,               /* a = semi-major axis (km)      */
       2.172430774036136E-05,               /* h = e sin(periapsis longitude)*/
      -6.598031717380385E-05,               /* k = e cos(periapsis longitude)*/
       3.140086133295854E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -8.159492292618122E-04,               /* p = tan(i/2) sin(node)        */
       2.954377849879345E-04,               /* q = tan(i/2) cos(node)        */
       7.743633229159851E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       8.796938549058478E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -7.736867825787147E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 711,   /* Juliet: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       6.435799380605987E+04,               /* a = semi-major axis (km)      */
       5.102069179571489E-04,               /* h = e sin(periapsis longitude)*/
       3.290951175690370E-04,               /* k = e cos(periapsis longitude)*/
       3.086603989435880E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       3.732510088859260E-06,               /* p = tan(i/2) sin(node)        */
      -2.984139406375623E-04,               /* q = tan(i/2) cos(node)        */
       7.050789555402506E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       8.450533526985233E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -7.044928085318312E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 712,   /* Portia: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       6.609699652935463E+04,               /* a = semi-major axis (km)      */
      -7.073393416690628E-05,               /* h = e sin(periapsis longitude)*/
       5.359454380567737E-05,               /* k = e cos(periapsis longitude)*/
       3.408229477693081E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -6.214971266125020E-04,               /* p = tan(i/2) sin(node)        */
      -6.518153623767534E-06,               /* q = tan(i/2) cos(node)        */
       6.422466432321616E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       8.119056159096675E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -6.417420983992342E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 713,    /* Rosalind: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       6.992700278480248E+04,               /* a = semi-major axis (km)      */
      -4.109675227500860E-05,               /* h = e sin(periapsis longitude)*/
      -2.403088254671275E-04,               /* k = e cos(periapsis longitude)*/
       2.895211830809949E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       1.443531067612200E-04,               /* p = tan(i/2) sin(node)        */
       1.401065041139977E-03,               /* q = tan(i/2) cos(node)        */
       5.273919837749587E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       7.460999954191480E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -5.270264644406115E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 714,   /* Belinda: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       7.525599740418985E+04,               /* a = semi-major axis (km)      */
      -1.688404437443101E-04,               /* h = e sin(periapsis longitude)*/
       1.225325148570106E-04,               /* k = e cos(periapsis longitude)*/
       3.189607642601064E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -1.798049614109377E-04,               /* p = tan(i/2) sin(node)        */
       2.616178929518709E-04,               /* q = tan(i/2) cos(node)        */
       4.080592112111099E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.682410774718794E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -4.078118716334471E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 715,   /* Puck: URA086X data */
      2446450.0,                            /* element epoch Julian date     */
       8.600500231070553E+04,               /* a = semi-major axis (km)      */
      -5.133930728219832E-05,               /* h = e sin(periapsis longitude)*/
       9.713461222699562E-05,               /* k = e cos(periapsis longitude)*/
       3.316352115991056E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -2.931323672585479E-03,               /* p = tan(i/2) sin(node)        */
      -1.988692603298827E-04,               /* q = tan(i/2) cos(node)        */
       2.563927692592904E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       5.469265726242158E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -2.562898939602568E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731359116506646E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517445781731228E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 725,    /* 1986 U 10 = Perdita: URA074 */
       2453243.0,                           /* element epoch Julian date     */
       7.641667990000000E+04,               /* a = semi-major axis (km)      */
      -4.599985060466543E-03,               /* h = e sin(periapsis longitude)*/
      -1.068053268538066E-02,               /* k = e cos(periapsis longitude)*/
       3.570600000000003E+01 * PI / 180.,   /* l = mean longitude (deg)      */
      -3.170493092396990E-03,               /* p = tan(i/2) sin(node)        */
       2.602049043514138E-03,               /* q = tan(i/2) cos(node)        */
       3.858668981481482E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.530636099537036E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -3.856388888888889E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731126999999999E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517520000000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 726,      /* Mab: URA074 */
       2453243.0,                           /* element epoch Julian date     */
       9.773590949999999E+04,               /* a = semi-major axis (km)      */
      -2.203762027618953E-03,               /* h = e sin(periapsis longitude)*/
      -1.256901716772159E-03,               /* k = e cos(periapsis longitude)*/
       1.540710000000000E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -1.875272329542152E-04,               /* p = tan(i/2) sin(node)        */
       1.149815949367713E-03,               /* q = tan(i/2) cos(node)        */
       1.629212962962963E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       4.514468831018519E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.628634259259259E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731126999999999E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517520000000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 727,      /* Cupid: URA074 */
       2453243.0,                           /* element epoch Julian date     */
       7.439234090000000E+04,               /* a = semi-major axis (km)      */
       1.257654515349878E-03,               /* h = e sin(periapsis longitude)*/
       4.478058954726516E-04,               /* k = e cos(periapsis longitude)*/
       2.342309999999999E+02 * PI / 180.,   /* l = mean longitude (deg)      */
      -4.201271164581371E-05,               /* p = tan(i/2) sin(node)        */
      -8.611686635128044E-04,               /* q = tan(i/2) cos(node)        */
       4.239432870370370E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       6.799116307870371E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -4.236793981481481E-06 * PI / 180.,   /* node rate (deg/sec)           */
       7.731126999999999E+01 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       1.517520000000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 801,  /* Triton, aka Neptune I: NEP050 */
       2447757.0,                           /* element epoch Julian date     */
       3.547591460000000E+05,               /* a = semi-major axis (km)      */
       2.183485420000000E-06,               /* h = e sin(periapsis longitude)*/
      -1.543648510000000E-05,               /* k = e cos(periapsis longitude)*/
       7.672436890000000E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       2.818138250000000E-02,               /* p = tan(i/2) sin(node)        */
      -2.030103396000000E-01,               /* q = tan(i/2) cos(node)        */
       1.211953824000000E-08 * PI / 180.,   /* apsis rate (deg/sec)          */
       7.089961076000000E-04 * PI / 180.,   /* mean motion (deg/sec)         */
       1.657793254000000E-08 * PI / 180.,   /* node rate (deg/sec)           */
       2.989472940000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.331890600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

    { 803,  /* Naiad, a.k.a. 1989N6: NEP050 */
       2447757.0,                           /* element epoch Julian date     */
       4.822701435905355E+04,               /* a = semi-major axis (km)      */
       3.620224770838396E-04,               /* h = e sin(periapsis longitude)*/
       1.156185304588290E-05,               /* k = e cos(periapsis longitude)*/
       6.810339767839658E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       3.452822063733985E-02,               /* p = tan(i/2) sin(node)        */
       2.290770169216655E-02,               /* q = tan(i/2) cos(node)        */
       1.964161049323076E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.415326558087714E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.985180471594082E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 804,   /* Thalassa, a.k.a. 1989N5: NEP050 */
      2447757.0,                            /* element epoch Julian date     */
       5.007495130640859E+04,               /* a = semi-major axis (km)      */
       1.881434320556790E-04,               /* h = e sin(periapsis longitude)*/
       1.033517936279606E-04,               /* k = e cos(periapsis longitude)*/
       2.475810361721285E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       1.808988491806543E-03,               /* p = tan(i/2) sin(node)        */
      -2.572520444193769E-04,               /* q = tan(i/2) cos(node)        */
       1.745544005794959E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.337678870805562E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.746377282651943E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 805,   /* Despina,  a.k.a. 1989N3: NEP050 */
      2447757.0,                            /* element epoch Julian date     */
       5.252607405757254E+04,               /* a = semi-major axis (km)      */
       2.232930551031250E-04,               /* h = e sin(periapsis longitude)*/
      -1.115774312255063E-05,               /* k = e cos(periapsis longitude)*/
       9.311343295481528E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       1.944862825322830E-04,               /* p = tan(i/2) sin(node)        */
      -5.200679669272585E-04,               /* q = tan(i/2) cos(node)        */
       1.475565828888696E-05 * PI / 180.,   /* apsis rate (deg/sec)          */
       1.245059755574818E-02 * PI / 180.,   /* mean motion (deg/sec)         */
      -1.476785707594837E-05 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 806,   /* Galatea, a.k.a. 1989N4: NEP050 */
      2447757.0,                            /* element epoch Julian date     */
       6.195297903638693E+04,               /* a = semi-major axis (km)      */
       1.674342888688514E-05,               /* h = e sin(periapsis longitude)*/
      -3.311081056771463E-05,               /* k = e cos(periapsis longitude)*/
       5.448813192644227E+01 * PI / 180.,   /* l = mean longitude (deg)      */
       4.358773699437865E-04,               /* p = tan(i/2) sin(node)        */
      -3.132950150251619E-04,               /* q = tan(i/2) cos(node)        */
       8.264989830842901E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       9.718285365249440E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -8.284262531923991E-06 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 807,   /* Larissa, a.k.a. 1989N2: NEP050 */
      2447757.0,                            /* element epoch Julian date     */
       7.354791709303492E+04,               /* a = semi-major axis (km)      */
       5.742600597431634E-04,               /* h = e sin(periapsis longitude)*/
      -1.269545891017604E-03,               /* k = e cos(periapsis longitude)*/
       1.926654222778896E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       5.395612235869184E-04,               /* p = tan(i/2) sin(node)        */
       1.702120710409934E-03,               /* q = tan(i/2) cos(node)        */
       4.526939181068548E-06 * PI / 180.,   /* apsis rate (deg/sec)          */
       7.512183377052987E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -4.555573945715664E-06 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }, /* Laplacian plane pole dec (deg)*/

   { 808,   /* Proteus,  a.k.a. 1989N1: NEP050 */
      2447757.0,                            /* element epoch Julian date     */
       1.176468148802116E+05,               /* a = semi-major axis (km)      */
       5.138756385126203E-04,               /* h = e sin(periapsis longitude)*/
      -1.319038194876358E-04,               /* k = e cos(periapsis longitude)*/
       2.214459710358717E+02 * PI / 180.,   /* l = mean longitude (deg)      */
       6.691721009767980E-05,               /* p = tan(i/2) sin(node)        */
      -2.147144625701844E-04,               /* q = tan(i/2) cos(node)        */
       8.764111065373391E-07 * PI / 180.,   /* apsis rate (deg/sec)          */
       3.712548540365151E-03 * PI / 180.,   /* mean motion (deg/sec)         */
      -9.086814828264133E-07 * PI / 180.,   /* node rate (deg/sec)           */
       2.993634890000000E+02 * PI / 180.,   /* Laplacian plane pole ra (deg) */
       4.344909600000000E+01 * PI / 180. }  /* Laplacian plane pole dec (deg)*/
   };


               /* In Win32,  if this function is in a DLL,  we gotta     */
               /* mention that fact up front.  The following #ifdef      */
               /* lets us do that without confusing OSes that are        */
               /* blessedly ignorant of the weirdnesses of Windoze DLLs: */
#ifdef _WIN32
#define DLL_FUNC __stdcall
#else
#define DLL_FUNC
#endif

   /* Given a JDE and a JPL ID number (see list at the top of this file), */
   /* evaluate_rock( ) will compute the J2000 equatorial Cartesian        */
   /* position for that "rock" and will return 0.  Otherwise,  it returns */
   /* -1 as an error condition.  No other errors are returned... though   */
   /* hypothetically,  something indicating you're outside the valid time */
   /* coverage for the orbit in question would be nice.                   */

#ifdef _WIN32
extern "C" {
#endif

int DLL_FUNC evaluate_rock( const double jde, const int jpl_id,
                                                  double *output_vect)
{
   int i;
   const ROCK *rptr = rocks;

   for( i = N_ROCKS; i; i--, rptr++)
      if( rptr->jpl_id == jpl_id)
         {
         const double seconds_per_day = 86400.;
         const double dt_seconds = (jde - rptr->epoch_jd) * seconds_per_day;
         const double mean_lon =
                    rptr->mean_lon0 + dt_seconds * rptr->mean_motion;
         double avect[3], bvect[3], cvect[3];
         double h, k, p, q, tsin, tcos, r, e, omega, true_lon;
         double a_fraction, b_fraction, c_fraction, dot_prod;

                        /* avect is at right angles to Laplacian pole, */
                        /* but in plane of the J2000 equator:          */
         avect[0] = -sin( rptr->laplacian_pole_ra);
         avect[1] = cos( rptr->laplacian_pole_ra);
         avect[2] = 0.;

                        /* bvect is at right angles to Laplacian pole  */
                        /* _and_ to avect:                             */
         tsin = sin( rptr->laplacian_pole_dec);
         tcos = cos( rptr->laplacian_pole_dec);
         bvect[0] = -avect[1] * tsin;
         bvect[1] = avect[0] * tsin;
         bvect[2] = tcos;

                        /* cvect is the Laplacian pole vector:  */
         cvect[0] = avect[1] * tcos;
         cvect[1] = -avect[0] * tcos;
         cvect[2] = tsin;

                           /* Rotate the (h, k) vector to account for */
                           /* a constant apsidal motion:              */
         tsin = sin( dt_seconds * rptr->apsis_rate);
         tcos = cos( dt_seconds * rptr->apsis_rate);
         h = rptr->k * tsin + rptr->h * tcos;
         k = rptr->k * tcos - rptr->h * tsin;

                           /* I'm sure there's a better way to do this...  */
                           /* all I do here is to compute the eccentricity */
                           /* and omega,  a.k.a. longitude of perihelion,  */
                           /* and do a first-order correction to get the   */
                           /* 'actual' r and true longitude values.        */
         e = sqrt( h * h + k * k);
         omega = atan2( h, k);
         true_lon = mean_lon + 2. * e * sin( mean_lon - omega)
                          + 1.25 * e * e * sin( 2. * (mean_lon - omega));
         r = rptr->a * (1. - e * e) / (1 + e * cos( true_lon - omega));

                           /* Just as we rotated (h,k),  we gotta rotate */
                           /* the (p,q) vector to account for precession */
                           /* in the Laplacian plane:                    */

         tsin = sin( dt_seconds * rptr->node_rate);
         tcos = cos( dt_seconds * rptr->node_rate);
         p = rptr->q * tsin + rptr->p * tcos;
         q = rptr->q * tcos - rptr->p * tsin;

                           /* Now we evaluate the position in components */
                           /* along avect, bvect, cvect.  I derived the  */
                           /* formulae from scratch... sorry I can't     */
                           /* give references:                           */
         tsin = sin( true_lon);
         tcos = cos( true_lon);
         dot_prod = 2. * (q * tsin - p * tcos) / (1. + p * p + q * q);
         a_fraction = tcos + p * dot_prod;
         b_fraction = tsin - q * dot_prod;
         c_fraction = dot_prod;

                           /* Now that we've got components on each axis, */
                           /* the remainder is trivial: */
         for( i = 0; i < 3; i++)
            output_vect[i] = r * (a_fraction * avect[i]
                                + b_fraction * bvect[i]
                                + c_fraction * cvect[i]);
         return( 0);
         }
   return( -1);
}

#ifdef _WIN32
}
#endif

#ifdef TEST_PROGRAM

/* A simple piece of test code that,  given a JPL ID and a JD,  prints out  */
/* the result of evaluate_rock.  Comparison to Horizons is straightforward, */
/* and indicates agreement to better than a meter.                          */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void main( int argc, char **argv)
{
   double vect[3], r2 = 0.;
   int i, jpl_id = atoi( argv[2]);

   evaluate_rock( atof( argv[1]), jpl_id, vect);
   printf( "%lf %lf %lf\n", vect[0], vect[1], vect[2]);
   for( i = 0; i < 3; i++)
      r2 += vect[i] * vect[i];
   printf( "\n%lf", sqrt( r2));
}
#endif
