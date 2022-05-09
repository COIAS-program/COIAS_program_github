/* "mycurses" is a minimal implementation of Curses for DOS,  containing
   just what's needed for a few of my DOS apps (including this one).  It's
   currently used only in the OpenWATCOM implementation,  and even there,
   it's not turned on by default. */

//K.S. 2021/6/14////////////////////////////////////////////////////////////////////////////
char *mypath;
///////////////////////////////////////////////////////////////////////////////////////////

#ifdef USE_MYCURSES
   #include "mycurses.h"
   #include "bmouse.h"
   #include <conio.h>
BMOUSE global_bmouse;
#else
#ifdef _MSC_VER
            /* At least at present,  on my machine,  I use a PDCurses DLL */
            /* when compiling with Visual C/C++,  in part because I've not */
            /* had much luck getting it to work that way in MinGW.  Your   */
            /* mileage may vary.  If so,  revise the following line.       */
   #define PDC_DLL_BUILD
#endif
   #include "curses.h"
#endif
      /* The 'usual' Curses library provided with Linux lacks a few things */
      /* that PDCurses and MyCurses have, such as definitions for ALT_A    */
      /* and such.  'curs_lin.h' fills in these gaps.   */
#ifndef ALT_A
   #include "curs_lin.h"
#endif

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
#include "watdefs.h"
#include "weight.h"
#include "afuncs.h"
#include "comets.h"
#include "mpc_obs.h"
#include "date.h"
#include "monte0.h"

int debug_level = 0;

#define MAX_LINES 250
extern double planet_mass[];
extern int perturbers, separate_periodic_comet_apparitions;
extern double solar_pressure[];
extern int n_extra_params;

//KKK
char *obsline;
//KKK


#define GAUSS_K .01720209895
#define SOLAR_GM (GAUSS_K * GAUSS_K)
#define PI 3.14159265358979323846264338397
#define J2000 2451545.

#define RESIDUAL_FORMAT_SHOW_DELTAS              64

#define EARTH_MAJOR_AXIS 6378140.
#define EARTH_MINOR_AXIS 6356755.
#define EARTH_AXIS_RATIO (EARTH_MINOR_AXIS / EARTH_MAJOR_AXIS)
#define EARTH_MAJOR_AXIS_IN_AU (EARTH_MAJOR_AXIS / (1000. * AU_IN_KM))

int simplex_method( OBSERVE FAR *obs, int n_obs, double *orbit,
               const double r1, const double r2);          /* orb_func.cpp */
int superplex_method( OBSERVE FAR *obs, int n_obs, double *orbit);
static void show_a_file( const char *filename);
const char *get_environment_ptr( const char *env_ptr);     /* mpc_obs.cpp */
void set_environment_ptr( const char *env_ptr, const char *new_value);
static void put_colored_text( const char *text, const int line_no,
               const int column, const int n_bytes, const int color);
int find_trial_orbit( double *orbit, OBSERVE FAR *obs, int n_obs,
             const double r1, const double angle_param);   /* orb_func.cpp */
char *fgets_trimmed( char *buff, size_t max_bytes, FILE *ifile);
int debug_printf( const char *format, ...);                /* runge.cpp */
static void get_mouse_data( int *mouse_x, int *mouse_y, int *mouse_z, unsigned long *button);
int make_pseudo_mpec( const char *mpec_filename, const char *obj_name);
                                              /* ephem0.cpp */
int store_defaults( const int ephemeris_output_options);    /* elem_out.c */
int get_defaults( int *ephemeris_output_options);           /* elem_out.c */
int text_search_and_replace( char FAR *str, const char *oldstr,
                                     const char *newstr);   /* ephem0.cpp */
void put_observer_data_in_text( const char FAR *mpc_code, char *buff);
                                                            /* mpc_obs.c */
#ifdef _WIN32
int clipboard_to_file( const char *filename);         /* mpc_obs.cpp */
#endif

#define COLOR_BACKGROUND            1
#define COLOR_ORBITAL_ELEMENTS      2
#define COLOR_FINAL_LINE            3
#define COLOR_SELECTED_OBS          4
#define COLOR_HIGHLIT_BUTTON        5
#define COLOR_EXCLUDED_OBS          6
#define COLOR_OBS_INFO              7
#define COLOR_MESSAGE_TO_USER       8
#define COLOR_RESIDUAL_LEGEND       9
#define COLOR_MENU                 10
#define COLOR_DEFAULT_INQUIRY       9

#ifdef USE_MYCURSES
static int curses_kbhit( )
{
   return( kbhit( ) ? 0: ERR);
}
#else
static int curses_kbhit( )
{
   int c;

   nodelay( stdscr, TRUE);
   c = getch( );
   nodelay( stdscr, FALSE);
   if( c != ERR)     /* no key waiting */
      ungetch( c);
   return( c);
}
#endif

static int extended_getch( void)
{
#ifdef _WIN32
   int rval = getch( );

   if( !rval)
      rval = 256 + getch( );
#endif
#ifdef __WATCOMC__
   int rval = 0;

   while( !rval)
      {
      if( curses_kbhit( ))
         {
         rval = getch( );
         if( !rval)
            rval = 256 + getch( );
         }
#ifdef USE_MYCURSES
      else
         {
         mouse_read( &global_bmouse);
         if( global_bmouse.released)
            rval = KEY_MOUSE;
         }
#endif
      }
#endif
#if !defined (_WIN32) && !defined( __WATCOMC__)
   int rval = getch( );

   if( rval == 27)
      {
      clock_t end_time = clock( ) + CLOCKS_PER_SEC / 2;

      nodelay( stdscr, TRUE);
      do
         {
         rval = getch( );
         }
         while( rval == ERR && clock( ) < end_time);
      nodelay( stdscr, FALSE);
      if( rval == ERR)    /* no second key found */
         rval = 27;       /* just a plain ol' Escape */
      else
         rval += (ALT_A - 'a');
      }
#endif
   return( rval);
}

int inquire( const char *prompt, char *buff, const int max_len,
                     const int color)
{
   int i, rval, line, col, n_lines = 0, line_start = 0, box_size = 0;
   const int side_borders = 1;   /* leave a blank on either side */
   char tbuff[200];

   for( i = 0; prompt[i]; i++)
      if( prompt[i] == '\n')
         {
         if( box_size < i - line_start)
            box_size = i - line_start;
         line_start = i;
         n_lines++;
         }
   if( box_size < i - line_start)
      box_size = i - line_start;
   if( box_size > getmaxx( stdscr) - 2)
      box_size = getmaxx( stdscr) - 2;

   line = (getmaxy( stdscr) - n_lines) / 2;
   col = (getmaxx( stdscr) - box_size) / 2;
   tbuff[side_borders * 2 + box_size] = '\0';
#ifdef __WATCOMC__
   refresh( );             /* This doesn't work except in mycurses */
   scr_dump( "scr.txt");
   refresh( );
#endif
   for( i = 0; prompt[i]; )
      {
      int j, n_spaces;

      for( j = i; prompt[j] && prompt[j] != '\n'; j++)
         ;
      memset( tbuff, ' ', side_borders);
      memcpy( tbuff + side_borders, prompt + i, j - i);
      n_spaces = box_size + side_borders - (j - i);
      if( n_spaces > 0)
         memset( tbuff + side_borders + j - i, ' ', n_spaces);
      put_colored_text( tbuff, line, col - side_borders,
             side_borders * 2 + box_size, color);
      i = j;
      if( prompt[i] == '\n')
         i++;
      line++;
      }
   if( buff)
      {
      memset( tbuff, ' ', side_borders * 2 + box_size);
      put_colored_text( tbuff, line, col - side_borders,
             side_borders * 2 + box_size, color);
      move( line, col);
      echo( );
      refresh( );
      rval = getnstr( buff, max_len);
      noecho( );
      }
   else
      {
      refresh( );
      rval = extended_getch( );
      }
#ifdef __WATCOMC__
   refresh( );             /* This doesn't work except in mycurses */
   scr_restore( "scr.txt");
   refresh( );
#endif
   return( rval);
}

static int extract_date( const char *buff, double *jd)
{
   int rval = 0;
   static const double jan_1970 = 2440587.5;

   *jd = jan_1970 + time( NULL) / 86400.;
   if( !memcmp( buff, "now", 3))
      {
      if( buff[3] == '+' || buff[3] == '-')
         *jd += get_step_size( buff + 3, NULL, NULL);
      rval = 1;
      }
   else
      {
      *jd = get_time_from_string( *jd, buff,
                     FULL_CTIME_YMD | CALENDAR_JULIAN_GREGORIAN);
      rval = 2;
      if( *buff == '+' || *buff == '-')   /* entered offset */
         rval = 3;
      if( *jd == 0.)
         rval = -1;
      }
   return( rval);
}

/* Here's a simplified example of the use of the 'ephemeris_in_a_file'
   function... nothing fancy,  but it shows how it's used.  */

char mpc_code[8];
char ephemeris_start[80], ephemeris_step_size[80], ephemeris_end[80];
int ephem_options;

static void create_ephemeris( const double *orbit, const double epoch_jd,
         const double abs_mag, const int is_comet)
{
   int c = 1, n_steps = 0;
   char buff[600];
   double jd_start = 0., jd_end = 0., step = 0.;

   while( c > 0)
      {
      const int format_start = extract_date( ephemeris_start, &jd_start);
      const int format_end   = extract_date( ephemeris_end,   &jd_end);

      step = get_step_size( ephemeris_step_size, NULL, NULL);
      if( format_start == 1 || format_start == 2)
         {
         if( step && format_start == 1)  /* time was relative to 'right now' */
            jd_start = floor( (jd_start - .5) / step) * step + .5;
         sprintf( buff, " (Ephem start: JD %.5lf = ", jd_start);
         full_ctime( buff + strlen( buff), jd_start,
                          FULL_CTIME_DAY_OF_WEEK_FIRST);
         strcat( buff, ")\n");
         }
      else
         {
         strcpy( buff, "(Ephemeris starting time isn't valid)\n");
         jd_start = 0.;
         }

      if( format_end == 1 || format_end == 2)
         {
         if( step && format_end == 1)  /* time was relative to 'right now' */
            jd_end = floor( (jd_end - .5) / step) * step + .5;
         sprintf( buff + strlen( buff), " (Ephem end:   JD %.5lf = ", jd_end);
         full_ctime( buff + strlen( buff), jd_end,
                          FULL_CTIME_DAY_OF_WEEK_FIRST);
         strcat( buff, ")\n");
         }
      else
         {
         strcat( buff, "(Ephemeris ending time isn't valid)\n");
         jd_end = 0.;
         }
      if( jd_start && jd_end && step)
         {
         n_steps = (int)fabs( (jd_start - jd_end) / step) + 1;
         sprintf( buff + strlen( buff), "%d steps\n", n_steps);
         }
      else
         n_steps = 0;

      sprintf( buff + strlen( buff), "T  Ephem start: %s\n", ephemeris_start);
      sprintf( buff + strlen( buff), "E  Ephem end  : %s\n", ephemeris_end);
      sprintf( buff + strlen( buff), "S  Step size: %s\n", ephemeris_step_size);
      sprintf( buff + strlen( buff), "L  Location: (%s) ", mpc_code);
      put_observer_data_in_text( mpc_code, buff + strlen( buff));
      strcat( buff, "\n");
      if( !(ephem_options & 33))    /* for close-approach/vector tables,   */
         {                          /* these options are irrelevant:       */
         sprintf( buff + strlen( buff), "Z  Motion info in ephemerides: %s\n",
                  (ephem_options & OPTION_MOTION_OUTPUT) ? "On" : "Off");
         sprintf( buff + strlen( buff), "A  Alt/az info in ephemerides: %s\n",
                  (ephem_options & OPTION_ALT_AZ_OUTPUT) ? "On" : "Off");
         sprintf( buff + strlen( buff), "R  Radial velocity in ephemerides: %s\n",
                  (ephem_options & OPTION_RADIAL_VEL_OUTPUT) ? "On" : "Off");
         }
      sprintf( buff + strlen( buff), "C  Close approach table: %s\n",
               (ephem_options & OPTION_CLOSE_APPROACHES) ? "On" : "Off");
      sprintf( buff + strlen( buff), "V  State vector table: %s\n",
               (ephem_options & OPTION_STATE_VECTOR_OUTPUT) ? "On" : "Off");
      sprintf( buff + strlen( buff), "?  Help about making ephemerides\n");
      sprintf( buff + strlen( buff), "Hit 'm' to make ephemeris, 'q' to return to main display");
      c = inquire( buff, NULL, 0, COLOR_DEFAULT_INQUIRY);
      switch( c)
         {
         case 't': case 'T':
            inquire( "Enter start of ephemeris (YYYY MM DD, or JD, or 'now'):",
                  ephemeris_start, sizeof( ephemeris_start), COLOR_MESSAGE_TO_USER);
            break;
         case 'e': case 'E':
            inquire( "Enter end of ephemeris (YYYY MM DD, or JD, or 'now'):",
                  ephemeris_end, sizeof( ephemeris_end), COLOR_MESSAGE_TO_USER);
            break;
         case 's': case 'S':
            inquire( "Enter step size in days: ",
                  ephemeris_step_size, sizeof( ephemeris_step_size), COLOR_MESSAGE_TO_USER);
            break;
         case 'l': case 'L':
            inquire( "Enter MPC code: ", buff, sizeof( buff), COLOR_MESSAGE_TO_USER);
            if( strlen( buff) == 3)
               strcpy( mpc_code, buff);
            break;
         case 'z': case 'Z':
            ephem_options ^= OPTION_MOTION_OUTPUT;
            break;
         case 'a': case 'A':
            ephem_options ^= OPTION_ALT_AZ_OUTPUT;
            break;
         case 'r': case 'R':
            ephem_options ^= OPTION_RADIAL_VEL_OUTPUT;
            break;
         case 'c': case 'C':
            ephem_options ^= OPTION_CLOSE_APPROACHES;
            break;
         case 'v': case 'V':
            ephem_options ^= OPTION_STATE_VECTOR_OUTPUT |
                             OPTION_VELOCITY_OUTPUT;
            break;
         case 'm': case 'M':
            {
            const char *err_msg = NULL;

            if( n_steps)         /* yes,  we can make an ephemeris */
               c = -2;
            else if( !jd_start)
               err_msg = "You need to set a valid starting date!";
            else if( !jd_end)
               err_msg = "You need to set a valid end date!";
            else if( !step)
               err_msg = "You need to set a valid step size!";
            if( err_msg)
               inquire( err_msg, NULL, 0, COLOR_FINAL_LINE);
            }
            break;
         case 'q': case 'Q':
            c = -1;
            break;
         default:
            show_a_file( "dosephem.txt");
            break;
         }
      }

   if( c == -2)         /* yes,  we're making an ephemeris */
      {
      double lon, rho_sin_phi, rho_cos_phi;
      extern const char *ephemeris_filename;
      int planet_no = 3;

      if( jd_end < jd_start)  /* ephemeris goes 'backward' */
         step = -step;
      planet_no = get_observer_data( mpc_code, buff, &lon,
                                        &rho_cos_phi, &rho_sin_phi);
      if( ephemeris_in_a_file( ephemeris_filename, orbit, planet_no,
            epoch_jd, jd_start, ephemeris_step_size, abs_mag, lon,
            rho_cos_phi, rho_sin_phi, n_steps,
            is_comet, mpc_code, ephem_options))
         inquire( "Ephemeris generation failed!  Hit any key:", NULL, 0,
                           COLOR_MESSAGE_TO_USER);
      else
         show_a_file( ephemeris_filename);
      }
}


static void object_comment_text( char *buff, const OBJECT_INFO *id)
{
   sprintf( buff, "%d observations; ", id->n_obs);
   make_date_range_text( buff + strlen( buff),
                                (double)id->jd_start / 1440.,
                                (double)id->jd_end / 1440.);
}

/* select_object_in_file( ) uses the find_objects_in_file( ) function to
   get a list of all the objects listed in a file of observations.  It
   prints out their IDs and asks the user to hit a key to select one.
   The name of that object is then copied into the 'obj_name' buffer.

   At present,  it's used only in main( ) when you first start DOS_FIND,
   so you can select the object for which you want an orbit.         */

int select_object_in_file( const OBJECT_INFO *ids, const int n_ids)
{
   static int choice = 0, show_packed = 0;
   int rval = -1;

   if( ids && n_ids)
      {
      int i, curr_page = 0, err_message = 0, force_full_width_display = 0;

      clear( );
      while( rval == -1)
         {
         const int n_lines = getmaxy( stdscr) - 3;
         int column_width = 16;
         int c, n_cols = getmaxx( stdscr) / column_width;
         char buff[280];

         if( force_full_width_display)
            n_cols = 1;
         if( choice < 0)
            choice = 0;
         if( choice > n_ids - 1)
            choice = n_ids - 1;
         while( curr_page > choice)
            curr_page -= n_lines;
         while( curr_page + n_lines * n_cols <= choice)
            curr_page += n_lines;
         if( curr_page < 0)      /* ensure that we wrap around: */
            curr_page = 0;
         if( n_ids < n_lines * n_cols)
            n_cols = n_ids / n_lines + 1;
         column_width = getmaxx( stdscr) / n_cols;
//       if( column_width > 80)
//          column_width = 80;
         for( i = 0; i < n_lines * n_cols; i++)
            {
            char desig[181];
            int color = COLOR_BACKGROUND;

            if( i + curr_page < n_ids)
               {
               if( show_packed)
                  sprintf( desig, "'%s'", ids[i + curr_page].packed_desig);
               else
                  strcpy( desig, ids[i + curr_page].obj_name);
               if( i + curr_page == choice)
                  {
                  sprintf( buff, "Object %d of %d: %s",
                              choice + 1, n_ids, desig);
                  put_colored_text( buff, n_lines + 1, 0, -1,
                                                COLOR_SELECTED_OBS);
                  object_comment_text( buff, ids + choice);
                  put_colored_text( buff, n_lines + 2, 0, -1,
                                                COLOR_SELECTED_OBS);
                  color = COLOR_HIGHLIT_BUTTON;
                  }
               else
                  if( ids[i + curr_page].solution_exists)
                     color = COLOR_OBS_INFO;
               }
            else                        /* just want to erase space: */
               *desig = '\0';
            desig[column_width] = '\0';    /* trim to fit available space */
            sprintf( buff, "%-*s", column_width, desig);
            if( n_cols == 1 && i + curr_page < n_ids)
               object_comment_text( buff + 25, ids + i + curr_page);
            put_colored_text( buff, i % n_lines,
                   (i / n_lines) * column_width,
                   (n_cols == 1 ? -1 : column_width), color);
            }

         put_colored_text( "Use arrow keys to find your choice,  then hit the space bar or Enter",
                                 n_lines, 0, -1, COLOR_SELECTED_OBS);
         if( err_message)
            put_colored_text( "Not a valid choice",
                                 n_lines + 2, 0, -1, COLOR_FINAL_LINE);
         put_colored_text( "Quit", n_lines + 2, 75, 4, COLOR_HIGHLIT_BUTTON);
         put_colored_text( "Next", n_lines + 2, 70, 4, COLOR_HIGHLIT_BUTTON);
         put_colored_text( "Prev", n_lines + 2, 65, 4, COLOR_HIGHLIT_BUTTON);
         put_colored_text( "End", n_lines + 2, 61, 3, COLOR_HIGHLIT_BUTTON);
         put_colored_text( "Start", n_lines + 2, 55, 5, COLOR_HIGHLIT_BUTTON);
         refresh( );
         flushinp( );
         c = extended_getch( );
         err_message = 0;
         if( c == KEY_MOUSE)
            {
            int x, y, z;
            unsigned long button;

            get_mouse_data( &x, &y, &z, &button);
            if( y < n_lines)
               choice = curr_page + y + (x / column_width) * n_lines;
            else if( y == n_lines + 2)
               if( x >= 75)
                  c = 27;          /* quit */
               else if( x >= 70)
                  c = KEY_NPAGE;   /* 'next page' */
               else if( x >= 65)
                  c = KEY_PPAGE;   /* 'prev page' */
               else if( x >= 61)
                  c = KEY_END;     /* end of list */
               else if( x >= 55)
                  c = KEY_HOME;    /* start of list */
#ifndef __WATCOMC__
            if( button & BUTTON1_DOUBLE_CLICKED)
               rval = choice;
#endif
            }
                     /* if a letter/number is hit,  look for an obj that */
                     /* starts with that letter/number: */
         if( c > ' ' && c <= 'z' && isalnum( c))
            for( i = 1; i < n_ids; i++)
               {
               const int loc = (i + choice) % n_ids;

               if( toupper( c) == toupper( ids[loc].obj_name[0]))
                  {
                  choice = loc;
                  i = n_ids;
                  }
               }
         else switch( c)
            {
            case 9:
               force_full_width_display ^= 1;
               break;
            case ' ':
            case 13:
               rval = choice;
               break;
#ifdef KEY_C2
            case KEY_C2:
#endif
            case KEY_DOWN:
               choice++;
               break;
#ifdef KEY_A2
            case KEY_A2:
#endif
            case KEY_UP:
               choice--;
               break;
#ifdef KEY_B1
            case KEY_B1:
#endif
            case KEY_LEFT:
               choice -= n_lines;
               break;
#ifdef KEY_B3
            case KEY_B3:
#endif
            case KEY_RIGHT:
               choice += n_lines;
            break;
            case KEY_C3:         /* "PgDn" = lower right key in keypad */
            case KEY_NPAGE:
            case 'n':
               choice += n_lines * n_cols;
               break;
            case KEY_A3:         /* "PgUp" = upper right key in keypad */
            case KEY_PPAGE:
            case 'p':
               choice -= n_lines * n_cols;
               break;
            case KEY_C1:
            case KEY_END:
            case 'e':
               choice = n_ids - 1;
               break;
            case KEY_A1:
            case KEY_HOME:
            case 's':
               choice = 0;
               break;
            case ',':
               show_packed ^= 1;
               break;
            case KEY_MOUSE:      /* already handled above */
               break;
#ifdef __PDCURSES__
            case KEY_RESIZE:
               resize_term( 0, 0);
               break;
#endif
            case 'q': case 'Q': case 27:
               rval = -2;
               break;
            }
         }
      if( debug_level > 3)
         debug_printf( "rval = %d; leaving select_object_in_file\n", rval);
      }
   return( rval);
}

void format_dist_in_buff( char *buff, const double dist_in_au); /* ephem0.c */

static char command_text[80], command_remap[80];

void show_basic_info( const OBSERVE FAR *obs, const int n_obs)
{
   char buff[80];
   double r1, r2;
   int i;

   get_r1_and_r2( n_obs, obs, &r1, &r2);    /* orb_func.cpp */
   strcpy( buff, "R1:");
   format_dist_in_buff( buff + 3, r1);
   put_colored_text( buff, 0, 0, 15, COLOR_BACKGROUND);

   strcpy( buff, "  R2:");
   format_dist_in_buff( buff + 5, r2);
   put_colored_text( buff, 0, 10, -1, COLOR_BACKGROUND);

   for( i = 0; command_text[i]; i++)
      if( command_text[i] != ' ')
         put_colored_text( (char *)command_text + i, 0, i + 24, 1,
                                 COLOR_MENU);
}

static const char *perturber_names[12] = {
          "Mercury", "Venus", "Earth", "Mars", "Jupiter",
          "Saturn", "Uranus", "Neptune", "Pluto", "Moon", "Asteroids", NULL };

void show_perturbers( void)
{
   int i;

   for( i = 0; perturber_names[i]; i++)
      {
      int color = COLOR_BACKGROUND;
      const int shift_amt = (i == 10 ? 20 : i + 1);
      char buff[20];

      strcpy( buff, "(o)");
      if( (perturbers >> shift_amt) & 1)
         color = COLOR_HIGHLIT_BUTTON;
      else
         {
         buff[1] = (char)( '0' + (i + 1) % 10);
         if( i == 10)
            buff[1] = 'a';
         }
      put_colored_text( buff, 1, i * 7, 3, color);
      strcpy( buff, perturber_names[i]);
      strcpy( buff + 3, " ");
      put_colored_text( buff, 1, i * 7 + 3, strlen( buff), COLOR_BACKGROUND);
      }
}

int max_mpc_color_codes = 5;
static MPC_STATION *mpc_color_codes = NULL;

/* Show the text for a given residual... which will be in 'default_color'
   unless parentheses are found.  If they're found,  that means we're
   looking at an excluded observation;  the parentheses,  and everything
   between them,  will be shown in COLOR_EXCLUDED_OBS.           */

static void show_residual_text( char *buff, const int line_no,
           const int column, const int default_color, const int mpc_column,
           const int is_included)
{
   put_colored_text( buff, line_no, column, strlen( buff), default_color);
   if( !is_included)
      {
      int start, len;

      switch( mpc_column)
         {
         case 8:        /* three obs/line format */
            start = 11;
            len = 13;
            break;
         default:
            start = 15;
            len = 45;
            break;
         }
      put_colored_text( buff + start, line_no, column + start, len,
                                          COLOR_EXCLUDED_OBS);
      }
   if( mpc_column >= 0)
      {
      buff += mpc_column;
      if( *buff != ' ')       /* show MPC code in color: */
         put_colored_text( buff, line_no, column + mpc_column, 3,
                        512 + 16 + find_mpc_color( mpc_color_codes, buff));
      }
}

#define SORT_BY_SCORE 0
#define SORT_BY_NAME  1

static void sort_mpc_codes( const int n_to_sort, const int sort_flag)
{
   int i, do_swap;

   for( i = 0; i < n_to_sort - 1; i++)
      {
      if( sort_flag == SORT_BY_SCORE)
         do_swap = (mpc_color_codes[i].score < mpc_color_codes[i + 1].score);
      else
         do_swap = (strcmp( mpc_color_codes[i].code,
                            mpc_color_codes[i + 1].code) > 0);
      if( do_swap)
         {
         MPC_STATION temp = mpc_color_codes[i];

         mpc_color_codes[i] = mpc_color_codes[i + 1];
         mpc_color_codes[i + 1] = temp;
         if( i)
            i -= 2;
         }
      }
}

static void add_to_mpc_color( const char *code, const int score_increment)
{
   int i;

   for( i = 0; mpc_color_codes[i].code[0]; i++)
      if( !strcmp( mpc_color_codes[i].code, code))
         mpc_color_codes[i].score += score_increment;
}

int first_residual_shown, n_stations_shown;

void show_residuals( const OBSERVE FAR *obs, const int n_obs,
              const int residual_format, const int curr_obs, int line_no,
              const int list_codes)
{
   int n_obs_shown = getmaxy( stdscr) - line_no;
   int i;
   const int n_mpc_codes = find_mpc_color( mpc_color_codes, NULL);
   const int base_format = (residual_format & 3);
   char buff[120];

   n_stations_shown = n_obs_shown / 3;
   if( n_obs_shown < 0)
      return;
   for( i = 0; i < n_obs_shown; i++)         /* clear out space */
      put_colored_text( "", i + line_no, 0, -1, COLOR_BACKGROUND);
                  /* set 'scores' for each code to equal # of times */
                  /* that code was used: */
   for( i = 0; i < n_mpc_codes; i++)
      mpc_color_codes[i].score = 0;
   for( i = 0; i < n_obs; i++)
      add_to_mpc_color( obs[i].mpc_code, 1);

   if( n_stations_shown > n_mpc_codes)
      n_stations_shown = n_mpc_codes;
   if( !list_codes || n_stations_shown < 1)
      n_stations_shown = 1;
   n_obs_shown -= n_stations_shown;

   if( base_format != RESIDUAL_FORMAT_SHORT)    /* one residual/line */
      {
      int line_start = curr_obs - n_obs_shown / 2;

      if( line_start > n_obs - n_obs_shown)
         line_start = n_obs - n_obs_shown;
      if( line_start < 0)
         line_start = 0;

      for( i = 0; i < n_obs_shown; i++)
         if( line_start + i < n_obs)
            {
            int color = COLOR_BACKGROUND, mpc_column;

            add_to_mpc_color( obs[line_start + i].mpc_code,
                      (line_start + i == curr_obs ? n_obs * n_obs : n_obs));
            if( base_format == RESIDUAL_FORMAT_80_COL)
               {                         /* show in original 80-column MPC  */
               char resid_data[70];      /* format, w/added data if it fits */

               format_observation( obs + line_start + i, buff,
                         (residual_format & ~3) | RESIDUAL_FORMAT_HMS);
               strcpy( resid_data, buff + 42);
               recreate_observation_line( buff, obs + line_start + i);
               if( residual_format & RESIDUAL_FORMAT_HMS)
                  {
                  const long seconds = (long)( atof( buff + 25) * 86400.);
                  const char saved_byte = buff[32];

                  memmove( buff + 35, buff + 32, strlen( buff + 31));
                  sprintf( buff + 25, " %02ld:%02ld:%02ld ",
                       seconds / 3600L, (seconds / 60L) % 60L, seconds % 60L);
                  buff[35] = saved_byte;
                  mpc_column = 80;
                  }
               else
                  mpc_column = 77;
               strcpy( buff + strlen( buff), resid_data + 10);
               }
            else
               {
               format_observation( obs + line_start + i, buff, residual_format);
               if( residual_format & RESIDUAL_FORMAT_HMS)
                  mpc_column = 22;
               else
                  mpc_column = 20;
               }
            if( residual_format & RESIDUAL_FORMAT_SHOW_DELTAS)
               if( line_start + i != curr_obs)
                  {
                  double diff;
                  int column;

                  column = ((base_format == RESIDUAL_FORMAT_80_COL) ?
                                 15 : 0);
                  sprintf( buff + column, "%16.5lf",
                           obs[line_start + i].jd - obs[curr_obs].jd);
                  buff[column + 16] = ' ';
//KKK
                  diff = obs[line_start + i].ra - obs[curr_obs].ra;
                  if( diff > PI)
                     diff -= PI + PI;
                  if( diff < -PI)
                     diff += PI + PI;
                  column = ((base_format == RESIDUAL_FORMAT_80_COL) ?
                                 32 : 24);
                  sprintf( buff + column, "%11.5lf", diff * 180. / PI);
                  buff[column + 11] = ' ';

                  column = ((base_format == RESIDUAL_FORMAT_80_COL) ?
                                 44 : 38);
                  diff = obs[line_start + i].dec - obs[curr_obs].dec;
                  sprintf( buff + column, "%11.5lf", diff * 180. / PI);
                  buff[column + 11] = ' ';
                  }


            if( line_start + i == curr_obs)
               color = COLOR_SELECTED_OBS;
            show_residual_text( buff, line_no++, 0, color, mpc_column,
                                             obs[line_start + i].is_included);
            }
      first_residual_shown = line_start;
      }
   else              /* put three observations/line */
      {
      const int n_cols = getmaxx( stdscr) / 25;
      const int n_rows = (n_obs - 1) / n_cols + 1;
      const int col_width = getmaxx( stdscr) / n_cols;
      int j;
      int line_start = curr_obs % n_rows - n_obs_shown / 2;

      if( line_start > n_rows - n_obs_shown)
         line_start = n_rows - n_obs_shown;
      if( line_start < 0)
         line_start = 0;
      first_residual_shown = line_start;

      for( i = 0; i < n_obs_shown && line_start < n_rows;
                                         i++, line_no++, line_start++)
         for( j = 0; j < n_cols; j++)
            {
            const int obs_number = j * n_rows + line_start;
            char buff[50];
            int color = COLOR_BACKGROUND, is_included = 1;

            if( obs_number < n_obs)
               {
               add_to_mpc_color( obs[obs_number].mpc_code,
                      (obs_number == curr_obs ? n_obs * n_obs : n_obs));
               buff[0] = ' ';
               format_observation( obs + obs_number, buff + 1, residual_format);
               if( obs_number == curr_obs)
                  {
                  buff[0] = '<';
                  color = COLOR_SELECTED_OBS;
                  }
               strcat( buff, (obs_number == curr_obs ? ">    " : "    "));
               is_included = obs[obs_number].is_included;
               }
            else
               memset( buff, ' ', col_width);
            buff[col_width] = '\0';
            show_residual_text( buff, line_no, j * col_width, color, 8,
                     is_included);
            }
      }

   if( n_stations_shown)
      {
                /* OK,  sort obs by score,  highest first... */
      sort_mpc_codes( n_mpc_codes, SORT_BY_SCORE);
                /* ...then sort the ones we're going to display by name: */
      sort_mpc_codes( n_stations_shown, SORT_BY_NAME);

      for( i = 0; i < n_stations_shown; i++)
         {
         const int line_no = getmaxy( stdscr) - n_stations_shown + i;
         const int is_curr_code = !strcmp( mpc_color_codes[i].code,
                                        obs[curr_obs].mpc_code);

         sprintf( buff, "(%s)", mpc_color_codes[i].code);
         show_residual_text( buff, line_no, 0, COLOR_BACKGROUND, 1, 1);
         put_observer_data_in_text( mpc_color_codes[i].code, buff);
         show_residual_text( buff, line_no, 6,
             (is_curr_code ? COLOR_FINAL_LINE : COLOR_BACKGROUND), -1, 1);
         }
      sort_mpc_codes( n_mpc_codes, SORT_BY_NAME);
      }
}

void reference_to_text( char *obuff, const char *reference);    /* mpc_obs.c */

void show_final_line( const OBSERVE FAR *obs, const int n_obs,
                                      const int curr_obs, const int color)
{
   char buff[190];
   int len;

   reference_to_text( buff, obs[curr_obs].reference);
   sprintf( buff + strlen( buff), "  %d/%d", curr_obs + 1, n_obs);
   len = strlen( buff);
   put_colored_text( buff, getmaxy( stdscr) - 1,
                              getmaxx( stdscr) - len, len, color);
}

static void show_residual_legend( const int line_no, const int residual_format)
{
   const int base_format = (residual_format & 3);
   static const char *legends[4] = {
"YYYY MM DD.DDDDD  Obscode   RA (J2000)   dec        Xresid  Yresid  delta  R",
NULL,       /* this is the 'with tabs' format used in Windows Find_Orb */
" YYMMDD Obs  Xres Yres      ",
" Obj ID        YYYY MM DD.DDDDD   RA (J2000)   dec               mag     ref cod   Xres Yres    delta  R" };
   char buff[190];

   strcpy( buff, legends[base_format]);
   if( residual_format & RESIDUAL_FORMAT_TIME_RESIDS)
      {         /* residuals in time & cross-time, not RA and dec */
      char *text_loc;

      while( (text_loc = strstr( buff, "Xres")))
         *text_loc = 'T';
      while( (text_loc = strstr( buff, "Yres")))
         *text_loc = 'C';
      }
   if( residual_format & RESIDUAL_FORMAT_MAG_RESIDS)
      {
      if( base_format == RESIDUAL_FORMAT_FULL_NO_TABS)
         strcpy( buff + strlen( buff) - 2, "mresid");
      if( base_format == RESIDUAL_FORMAT_SHORT)
         memcpy( buff + 13, "Resi MRes", 9);
      }
   if( base_format == RESIDUAL_FORMAT_SHORT)
      {
      const int width = getmaxx( stdscr), n_cols = width / 25;
      const int cols = width / n_cols;
      int i;

      buff[cols] = '\0';
      for( i = 0; i < n_cols; i++)
         put_colored_text( buff, line_no, i * cols, -1, COLOR_RESIDUAL_LEGEND);
      }
   else
      put_colored_text( buff, line_no, 0, -1,
                              COLOR_RESIDUAL_LEGEND);
}

static void show_a_file( const char *filename)
{
   FILE *ifile = fopen( filename, "rb");
   char buff[150], err_text[100];
   int line_no = 0, keep_going = 1;
   int n_lines = 0, read_to = 0, *index, msg_num = 0;

   if( !ifile)
      return;
   while( fgets( buff, sizeof( buff), ifile))
      n_lines++;
   index = (int *)calloc( n_lines + 1, sizeof( int));
   *err_text = '\0';
   while( keep_going && line_no < n_lines)
      {
      int i, c, at_bottom;
      const char *msgs[3] = { "1Cursor keys to move",
                              "2Already at end of file!",
                              "2Already at top of file!" };

      clear( );
      if( line_no > n_lines - getmaxy( stdscr) + 1)
         line_no = n_lines - getmaxy( stdscr) + 1;
      if( line_no < 0)
         line_no = 0;
      if( line_no > read_to)
         {
         fseek( ifile, index[read_to], SEEK_SET);
         while( read_to < line_no && fgets( buff, sizeof( buff), ifile))
            {
            read_to++;
            index[read_to] = ftell( ifile);
            }
         }
      fseek( ifile, index[line_no], SEEK_SET);
      for( i = 0; i < getmaxy( stdscr) - 1
                        && fgets_trimmed( buff, sizeof( buff), ifile); i++)
         {
         put_colored_text( buff, i, 0, -1, COLOR_BACKGROUND);
         index[line_no + i + 1] = ftell( ifile);
         }
      sprintf( buff, "   Line %d of %d", line_no, n_lines);
      put_colored_text( buff, i, getmaxx( stdscr) - strlen( buff),
                                      strlen( buff), COLOR_FINAL_LINE);
      at_bottom = (line_no >= n_lines - getmaxy( stdscr) + 1);
      put_colored_text( "Quit", i, 25, 4, COLOR_FINAL_LINE);
      if( !at_bottom)
         {
         put_colored_text( "pgDown", i, 30, 6, COLOR_FINAL_LINE);
         put_colored_text( "End", i, 37, 3, COLOR_FINAL_LINE);
         }
      if( line_no)
         {
         put_colored_text( "pgUp", i, 41, 4, COLOR_FINAL_LINE);
         put_colored_text( "Top", i, 46, 3, COLOR_FINAL_LINE);
         }

      strcpy( buff, msgs[msg_num] + 1);
      if( *err_text)
         strcpy( buff, err_text);
      put_colored_text( buff, i, 0, strlen( buff), msgs[msg_num][0] - '0');
      *err_text = '\0';
      msg_num = 0;
      refresh( );
      flushinp( );
      c = extended_getch( );
      if( c == KEY_MOUSE)
         {
         int x, y, z;
         unsigned long button;

         get_mouse_data( &x, &y, &z, &button);
         if( y == i)
            {
            if( x >= 25 && x <= 28)       /* "Quit" */
               c = 'q';
            else if( x >= 30 && x <= 35)  /* "pgDown" */
               c = 'd';
            else if( x >= 37 && x <= 39)  /* "End" */
               c = 'e';
            else if( x >= 41 && x <= 44)  /* "pgUp" */
               c = 'u';
            else if( x >= 46 && x <= 48)  /* "Top" */
               c = 't';
            }
         else
            line_no += y - i / 2;
         }
      switch( c)
         {
         case KEY_C1:
         case KEY_END:
         case 'e': case 'E':
            line_no = n_lines - getmaxy( stdscr) + 1;
            break;
         case KEY_A1:
         case KEY_HOME:
         case 't': case 'T':
            line_no = 0;
            break;
         case KEY_UP:
#ifdef KEY_A2
         case KEY_A2:
#endif
            if( line_no > 0)
               line_no--;
            else
               msg_num = 2;
            break;
         case KEY_DOWN:
         case ' ':
#ifdef KEY_C2
         case KEY_C2:
#endif
            if( at_bottom)
               msg_num = 1;
            else
               line_no++;
            break;
         case KEY_C3:         /* "PgDn" = lower right key in keypad */
         case KEY_NPAGE:
         case 'd': case 'D':
         case 13:
            if( at_bottom)
               msg_num = 1;
            else
               line_no += getmaxy( stdscr) - 2;
            break;
         case KEY_A3:         /* "PgUp" = upper right key in keypad */
         case KEY_PPAGE:
         case 'u': case 'U':
            if( line_no > 0)
               line_no -= getmaxy( stdscr) - 2;
            else
               msg_num = 2;
            break;
#ifdef __PDCURSES__
         case KEY_RESIZE:
            resize_term( 0, 0);
            break;
#endif
         case 'q': case 'Q': case 27:
            keep_going = 0;
            break;
         default:
            break;
         }
      }
   fclose( ifile);
   free( index);
   refresh( );
}

static int get_epoch_range_of_included_obs( const OBSERVE FAR *obs,
                  const int n_obs, double *start_jd, double *end_jd)
{
   int idx1, idx2, rval;

   rval = get_idx1_and_idx2( n_obs, obs, &idx1, &idx2);
   if( start_jd)
      *start_jd = obs[idx1].jd;
   if( end_jd)
      *end_jd   = obs[idx2].jd;
   return( rval);
}

#ifdef USE_MYCURSES
static void initialize_global_bmouse( void)
{
   memset( &global_bmouse, 0, sizeof( BMOUSE));
   global_bmouse.xmax = getmaxx( stdscr) - 1;
   global_bmouse.ymax = getmaxy( stdscr) - 1;
   global_bmouse.x = getmaxx( stdscr) / 2;
   global_bmouse.y = getmaxy( stdscr) / 2;
   global_bmouse.sensitivity = 0;
   init_mouse( &global_bmouse);
}
#endif

static void get_mouse_data( int *mouse_x, int *mouse_y,
                            int *mouse_z, unsigned long *button)
{
#ifdef USE_MYCURSES
            *mouse_x = global_bmouse.x / 8;
            *mouse_y = global_bmouse.y / 8;
            *mouse_z = 0;
            *button = global_bmouse.released;
#else
#ifdef __PDCURSES__
            request_mouse_pos( );
            *mouse_x = MOUSE_X_POS;
            *mouse_y = MOUSE_Y_POS;
            *mouse_z = 0;
            *button = (BUTTON_STATUS( 1) ? 1 : 0)
                    | (BUTTON_STATUS( 2) ? 2 : 0)
                    | (BUTTON_STATUS( 3) ? 4 : 0)
                    | (MOUSE_WHEEL_UP    ? 8 : 0)
                    | (MOUSE_WHEEL_DOWN  ? 16 : 0);
#else      /* "generic" curses version: */
            MEVENT mouse_event;

            getmouse( &mouse_event);
            *mouse_x = mouse_event.x;
            *mouse_y = mouse_event.y;
            *mouse_z = mouse_event.z;
            *button  = mouse_event.bstate;
#endif
#endif
}

static void put_colored_text( const char *text, const int line_no,
               const int column, const int n_bytes, const int color)
{
   attrset( COLOR_PAIR( color & 255));
   if( color & 256)
      attron( A_BLINK);
   if( color & 512)
      attron( A_BOLD);
   if( n_bytes > 0)
      {
      const int len = getmaxx( stdscr) - column;

      mvaddnstr( line_no, column, text, (n_bytes < len) ? n_bytes : len);
      }
   else              /* clear to end of line */
      {
      int len = strlen( text), remains = getmaxx( stdscr) - len - column;

      if( remains < 0)
         {
         len += remains;
         remains = 0;
         }
      mvaddnstr( line_no, column, text, len);
      if( remains > 0 && remains < 190)
         {
         char buff[200];

         memset( buff, ' ', remains);
         buff[remains] = '\0';
         mvaddnstr( line_no, column + len, buff, remains);
         }
      }
   if( color & 256)
      attron( A_BLINK);
   if( color & 512)
      attroff( A_BOLD);
}


static void cycle_residual_format( int *residual_format, char *message_to_user)
{
   switch( *residual_format & 3)
      {
      case RESIDUAL_FORMAT_FULL_NO_TABS:      /* 0 */
         (*residual_format) += 2;             /* cycle to short format */
         break;
      case RESIDUAL_FORMAT_SHORT:             /* 2 */
         (*residual_format)++;                /* cycles to MPC 80-col */
         break;
      case RESIDUAL_FORMAT_80_COL:            /* 3 */
         (*residual_format) -= 3;             /* cycles back to full-no-tab */
         break;
      }
   switch( *residual_format & 3)
      {
      case RESIDUAL_FORMAT_FULL_NO_TABS:        /* 0 */
         strcpy( message_to_user, "Standard observation data shown");
         *residual_format |= RESIDUAL_FORMAT_FOUR_DIGIT_YEARS;
         break;
      case RESIDUAL_FORMAT_SHORT:               /* 2 */
         strcpy( message_to_user, "Short MPC residual format selected");
         *residual_format &= ~RESIDUAL_FORMAT_FOUR_DIGIT_YEARS;
         break;
      case RESIDUAL_FORMAT_80_COL:              /* 3 */
         strcpy( message_to_user, "Display of original MPC reports selected");
         break;
      }

}

static OBSERVE FAR *load_object( FILE *ifile, OBJECT_INFO *id,
                       double *curr_epoch, double *epoch_shown, double *orbit)
{
   extern int n_obs_actually_loaded;
   int got_vector;
   OBSERVE FAR *obs = load_observations( ifile, id->packed_desig,
                                                id->n_obs);

   if( debug_level || n_obs_actually_loaded != id->n_obs)
      {
      char buff[80];

      debug_printf( " %d observations loaded\n", n_obs_actually_loaded);
      make_date_range_text( buff, obs[0].jd,
                                    obs[n_obs_actually_loaded - 1].jd);
      debug_printf( "%s\n", buff);
      }
   obj_desig_to_perturber( id->packed_desig);
   got_vector = fetch_previous_solution( obs, id->n_obs, orbit,
                            curr_epoch, &perturbers);
   *epoch_shown = (got_vector ? *curr_epoch : floor( *curr_epoch) + .5);
   return( obs);
}

extern const char *elements_filename;

int sanity_test_observations( const char *filename);

/* main( ) begins by using the select_object_in_file( ) function (see above)
   to determine which object is going to be analyzed in the current 'run'.
   It loads up the observations for the object to be analyzed,
   and computes an initial guess for the orbit.

   It then goes into a loop,  setting up and displaying a screenful of
   data,  then asking the user to hit a key.  Based on which key is hit,
   an action such as taking an Herget step or a "full step",  or resetting
   the epoch,  or quitting,  is taken. */

int main( const int argc, const char **argv)
{
   char obj_name[80], tbuff[100], orbit_constraints[90];
   int c = 1, precision, get_new_object = 1, add_off_on = -1;
   int top_line_basic_info_perturbers, top_line_observation_info;
   int top_line_orbital_elements, top_line_residual_legend;
   int top_line_residuals, is_monte_orbit = 0, list_codes = 1;
   OBSERVE FAR *obs;
   int n_obs, i, curr_obs, observation_display, quit = 0;
   int original_xmax, original_ymax;
   double epoch_shown, curr_epoch, orbit[6];
   double r1 = 1., r2 = 1.;
   char message_to_user[80];
   int update_element_display = 1, gauss_soln = 0;
   int residual_format, bad_elements = 0, debug_mouse_messages = 0;
   int heliocentric_only = 0;
#ifdef USE_MYCURSES
   int curr_text_mode = 0;
#endif
   int auto_repeat_full_improvement = 0, n_ids, planet_orbiting = 0;
   int interactive_mode = 1;
//KKK
   int kve_mode = 1;
//KKK
   OBJECT_INFO *ids;
   //K.S. 2021/6/14////////////////////////////////
   //const char *option_filename = "options.txt";
   mypath = (char*)malloc(sizeof(char)*256);
   char home[256];
   strcpy(home, getenv("HOME"));
   sprintf(mypath,"%s/.coias/param",home);
   
   char option_filename[256];
   const char *option_filename_org = "options.txt";
   sprintf(option_filename,"%s/%s",mypath,option_filename_org);
   FILE *option_file = fopen( option_filename, "rb");
   if( option_file == NULL ){
     fprintf(stderr,"cannot open options.txt file! \n");
     exit(1);
   }
   ////////////////////////////////////////////////

   //K.S. 2021/2/26////////////////////////////////
   const char *orbitalElementFilename = "orbital_elements_summary.txt";
   FILE *fpOrbitalElement = fopen(orbitalElementFilename, "w");
   if( fpOrbitalElement == NULL ){
     fprintf(stderr,"cannot open orbital_elements_summary.txt file! \n");
     exit(1);
   }
   ////////////////////////////////////////////////
   double noise_in_arcseconds = 1.;
   double monte_data[MONTE_DATA_SIZE];
   extern int monte_carlo_object_count;

   for( i = 1; i < argc; i++)       /* check to see if we're debugging: */
      if( argv[i][0] == '-')
         switch( argv[i][1])
            {
            case 'd':
               debug_level = atoi( argv[i] + 2);
               if( !debug_level)
                  debug_level = 1;
               debug_printf( "DOS_FIND: debug_level = %d; %s %s\n",
                           debug_level, __DATE__, __TIME__);
               break;
            case 'i':
               interactive_mode = 0;
               break;
//KKK
            case 'k':
               kve_mode = 0;
               interactive_mode = 0;
               break;
//KKK
            case 'c':
               {
               extern int combine_all_observations;

               combine_all_observations = 1;
               }
               break;
            case 'm':
               {
               extern int integration_method;

               integration_method = atoi( argv[i] + 2);
               }
               break;
            case 'a':
               separate_periodic_comet_apparitions ^= 1;
               break;
            case 'n':
               max_mpc_color_codes = atoi( argv[i] + 2);
               break;
            case 's':
               sanity_test_observations( argv[1]);
               printf( "Sanity check complete\n");
               exit( 0);
               break;
            default:
               printf( "Unknown command-line option '%s'\n", argv[i]);
               return( -1);
            }

   if( fgets( tbuff, sizeof( tbuff), option_file))
     sscanf( tbuff, "%s %d %d %d %d",
	     mpc_code, &precision, &observation_display,
	     &residual_format, &list_codes);
   get_defaults( &ephem_options);                       /* elem_out.c */
   precision += 5;
   fgets_trimmed( command_text, sizeof( command_text), option_file);
   fgets_trimmed( command_remap, sizeof( command_remap), option_file);
   fgets_trimmed( ephemeris_start, sizeof( ephemeris_start), option_file);
   fgets_trimmed( ephemeris_step_size, sizeof( ephemeris_step_size), option_file);
   fgets_trimmed( ephemeris_end, sizeof( ephemeris_end), option_file);
   fclose( option_file);
   if( debug_level)
     debug_printf( "Options read\n");
   load_up_weight_records( "weight.txt");
   if( debug_level)
     debug_printf( "Default weighting table read\n");
   
   if( argc < 2)
     {
       printf( "DOS_FIND needs the name of an input file of MPC-formatted\n");
       printf( "astrometry as a command-line argument.\n");
       exit( 0);
     }
   
   *message_to_user = '\0';
   
#ifdef _WIN32
   if( !strcmp( argv[1], "c"))
     {
       const char *temp_clipboard_filename = "obs_temp.txt";
       
       clipboard_to_file( temp_clipboard_filename);
       argv[1] = temp_clipboard_filename;
     }
#endif
   
   ids = find_objects_in_file( argv[1], &n_ids, NULL);
   if( n_ids <= 0)
     {        /* no objects found,  or file not found */
       const char *err_msg;
       
       if( n_ids == -1)
         err_msg = "Couldn't locate the file '%s'";
       else
         err_msg = "No objects found in file '%s'";
       printf( err_msg, argv[1]);
       return( -1);
     }
   
   if( debug_level > 2)
     debug_printf( "%d objects in file\n", n_ids);
   if( debug_level > 3)
     for( i = 0; i < n_ids; i++)
       {
         debug_printf( "   Object %d: '%s', '%s'\n", i,
		       ids[i].packed_desig, ids[i].obj_name);
         object_comment_text( tbuff, ids + i);
         debug_printf( "   %s\n", tbuff);
       }
   if( n_ids > 0)
     set_solutions_found( ids, n_ids);
   if( debug_level > 2)
     debug_printf( "solutions set\n");
   if( !interactive_mode)
     {
       FILE *ifile = fopen( argv[1], "rb");
       extern int show_runtime_messages;
       
       show_runtime_messages = 0;
       heliocentric_only = 1;

       //K.S. 2021/2/26/////////////////////////////
       //printf( "Processing %d objects\n", n_ids);
       for( i = 0; i < n_ids; i++)
         {
	   *orbit_constraints = '\0';
	   n_obs = ids[i].n_obs;
	   object_comment_text( tbuff, ids + i);
	   /* Abbreviate 'observations:' to 'obs:' */
	   text_search_and_replace( tbuff, "ervations", "");
	   //K.S. 2021/2/26/////////////////////////////////////
	   fprintf(fpOrbitalElement, " %d: %s: %s", i + 1, ids[i].obj_name, tbuff);
	   if( n_obs < 2)
	     //K.S. 2021/2/26////////////
	     fprintf(fpOrbitalElement, "; skipping\n");
	   else
	     {
	       extern int append_elements_to_element_file;
	       extern char orbit_summary_text[];
	       long file_offset = ids[i].file_offset - 40L;
	       
	       /* Start a bit ahead of the actual data,  just in case */
	       /* there's a #Weight: or similar command in there: */
	       if( file_offset < 0L)
		 file_offset = 0L;
	       fseek( ifile, file_offset, SEEK_SET);
	       obs = load_object( ifile, ids + i, &curr_epoch, &epoch_shown, orbit);
	       
	       get_r1_and_r2( n_obs, obs, &r1, &r2);    /* orb_func.cpp */
	       if( i)
		 append_elements_to_element_file = 1;
	       //            write_out_elements_to_file( orbit, curr_epoch, epoch_shown,
	       //                  obs, n_obs, orbit_constraints, precision,
	       //                  0, heliocentric_only);
	       
	       //KKK ***********************
	       if(!kve_mode){
		 int nk;
		 double dra,ddec;
		 char obuff[81];
		 double vaisala_dist;
		 double ra0,dec0,rae,dece;
		 double ar, ad, br, bd;
		 
		 /* check dra, ddec */
		 
		 ra0 = obs[0].ra  - obs[0].computed_ra;
		 if( ra0 > PI)
		   ra0 -= PI + PI;
		 if( ra0 < -PI)
		   ra0 += PI + PI;
		 ra0 =  ra0 * 180./PI * 3600 * cos(obs[0].dec);
		 dec0= obs[0].dec - obs[0].computed_dec;
		 dec0 = dec0 * 180./PI * 3600;
		 rae = obs[n_obs-1].ra  - obs[n_obs-1].computed_ra;
		 if( rae > PI)
		   rae -= PI + PI;
		 if( rae < -PI)
		   rae += PI + PI;
		 rae =  rae * 180./PI * 3600 * cos(obs[n_obs-1].dec);
		 dece= obs[n_obs-1].dec - obs[n_obs-1].computed_dec;
		 dece = dece * 180./PI * 3600;
		 
		 /*  re calc orbit */
		 if(fabs(ra0)>0.1 || fabs(dec0)>0.1 || fabs(rae)>0.1 || fabs(dece)>0.1){
		   vaisala_dist = r1;
		   herget_method( obs, n_obs, -vaisala_dist, 0., orbit, NULL, NULL, NULL);
		   adjust_herget_results( obs, n_obs, orbit);
		   /* epoch is that of last included observation: */
		   get_epoch_range_of_included_obs( obs, n_obs, &curr_epoch, NULL);
		   get_r1_and_r2( n_obs, obs, &r1, &r2);
		 }
		 if( i)
		   append_elements_to_element_file = 1;
		 write_out_elements_to_file( orbit, curr_epoch, epoch_shown,
					     obs, n_obs, orbit_constraints, precision,
					     0, heliocentric_only);
		 //K.S. 2021/2/26//////////////////////////////////
		 fprintf(fpOrbitalElement, "; %s\n", orbit_summary_text);
		 
		 /* calc linear param ar br ad bd : ra = ar x jd + br, dec = dr x jd + bd */  
		 
		 ra0 = obs[0].ra  - obs[0].computed_ra;
		 if( ra0 > PI)
		   ra0 -= PI + PI;
		 if( ra0 < -PI)
		   ra0 += PI + PI;
		 ra0 =  ra0 * 180./PI * 3600 * cos(obs[0].dec);
		 dec0= obs[0].dec - obs[0].computed_dec;
		 dec0 = dec0 * 180./PI * 3600;
		 rae = obs[n_obs-1].ra  - obs[n_obs-1].computed_ra;
		 if( rae > PI)
		   rae -= PI + PI;
		 if( rae < -PI)
		   rae += PI + PI;
		 rae =  rae * 180./PI * 3600 * cos(obs[n_obs-1].dec);
		 dece= obs[n_obs-1].dec - obs[n_obs-1].computed_dec;
		 dece = dece * 180./PI * 3600;
		 
		 ar = (rae - ra0)/(obs[n_obs-1].jd - obs[0].jd); 
		 br = ra0 - ar * obs[0].jd; 
		 ad = (dece-dec0)/(obs[n_obs-1].jd - obs[0].jd); 
		 bd = dec0- ad * obs[0].jd; 
		 
		 for(nk=0;nk<n_obs;nk++){ 
		   dra = obs[nk].ra - obs[nk].computed_ra;
		   if( dra > PI)
                     dra -= PI + PI;
		   if( dra < -PI)
                     dra += PI + PI;
		   dra =  dra * 180./PI * 3600 * cos(obs[nk].dec) - (ar*obs[nk].jd + br);
		   
		   ddec = obs[nk].dec - obs[nk].computed_dec;
		   ddec = ddec * 180./PI * 3600 - (ad*obs[nk].jd + bd);
		   
		   recreate_observation_line( obuff,&obs[nk]);
		   printf("%81s | %9.2f %9.2f\n",obuff,dra,ddec);
		 }
		 
	       }else{
		 printf( "; %s\n", orbit_summary_text);
	       }
	       //KKK ***********************
	     }
         }
       fclose( ifile);
       fclose( fpOrbitalElement);
       exit( 0);
     }           /* end non-interactive processing... now on to "usual": */
   
   if( debug_level > 2)
     debug_printf( "Initializing curses...");
#ifdef XCURSES
   Xinitscr( argc, argv);
#else
   initscr( );
#endif
   cbreak( );
   noecho( );
   clear( );
   refresh( );
   start_color( );
   init_pair( COLOR_BACKGROUND, COLOR_WHITE, COLOR_BLACK);
   init_pair( COLOR_ORBITAL_ELEMENTS, COLOR_BLACK, COLOR_YELLOW);
   init_pair( COLOR_FINAL_LINE, COLOR_WHITE, COLOR_BLUE);
   init_pair( COLOR_SELECTED_OBS, COLOR_WHITE, COLOR_MAGENTA);
   init_pair( COLOR_HIGHLIT_BUTTON, COLOR_BLACK, COLOR_GREEN);
   init_pair( COLOR_EXCLUDED_OBS, COLOR_RED, COLOR_GREEN);
   init_pair( COLOR_OBS_INFO, COLOR_WHITE, COLOR_RED);
   init_pair( COLOR_MESSAGE_TO_USER, COLOR_BLACK, COLOR_WHITE);
   init_pair( COLOR_RESIDUAL_LEGEND, COLOR_BLACK, COLOR_CYAN);
   init_pair( COLOR_MENU, COLOR_GREEN, COLOR_MAGENTA);

                  /* MPC color-coded station colors: */
   init_pair( 16, COLOR_YELLOW, COLOR_BLACK);
   init_pair( 17, COLOR_BLUE, COLOR_BLACK);
   init_pair( 18, COLOR_MAGENTA, COLOR_BLACK);
   init_pair( 19, COLOR_RED, COLOR_BLACK);
   init_pair( 20, COLOR_GREEN, COLOR_BLACK);
   if( debug_level > 2)
      debug_printf( "Curses initialised, ");
   keypad( stdscr, 1);
   original_xmax = getmaxx( stdscr);
   original_ymax = getmaxy( stdscr);
#ifdef __PDCURSES__
   PDC_set_title( "DOS_FIND -- Orbit Determination");
   if( strstr( longname( ), "SDL"))
      resize_term( 40, 110);
   if( strstr( longname( ), "Win32"))
      resize_term( 50, 110);
#endif
#if !defined (_WIN32) && !defined( __WATCOMC__)
   mousemask( ALL_MOUSE_EVENTS, NULL);
#endif
#ifdef _WIN32
   mouse_set( ALL_MOUSE_EVENTS);
// mouse_set( BUTTON1_RELEASED | BUTTON2_RELEASED | BUTTON3_RELEASED
//                      | MOUSE_WHEEL_SCROLL);
#endif
#ifdef USE_MYCURSES
   initialize_global_bmouse( );
#endif
   while( !quit)
      {
      int obs_per_line;
      int base_format = (residual_format & 3);
      int line_no = 0, total_obs_lines;

      if( debug_level > 3)
         debug_printf( "get_new_object = %d\n", get_new_object);
      if( get_new_object)
         {
         int id_number = 0;

         if( n_ids > 1)
            id_number = select_object_in_file( ids, n_ids);
         if( debug_level > 3)
            debug_printf( "id_number = %d; '%s'\n", id_number,
                                    ids[id_number].obj_name);
         get_new_object = 0;
         *orbit_constraints = '\0';
         if( id_number < 0)
            {
            attrset( COLOR_PAIR( COLOR_BACKGROUND));
            endwin( );
            printf( "User exited program\n");
            return( -1);
            }
         else
            {
            FILE *ifile;
            long file_offset;

            strcpy( obj_name, ids[id_number].obj_name);
            sprintf( tbuff, "Loading '%s'...", obj_name);
            put_colored_text( tbuff, getmaxy( stdscr) - 3,
                                 0, -1, COLOR_FINAL_LINE);
            if( debug_level)
               debug_printf( "%s: ", tbuff);
            refresh( );
            n_obs = ids[id_number].n_obs;
            monte_carlo_object_count = 0;

            ifile = fopen( argv[1], "rb");
                /* Start a bit ahead of the actual data,  just in case */
                /* there's a #Weight: or similar command in there: */
            file_offset = ids[id_number].file_offset - 40L;
            if( file_offset < 0L)
               file_offset = 0L;
            fseek( ifile, file_offset, SEEK_SET);

            obs = load_object( ifile, ids + id_number, &curr_epoch,
                                                  &epoch_shown, orbit);
            fclose( ifile);
            if( debug_level)
               debug_printf( "got obs; ");
            if( mpc_color_codes)
               free( mpc_color_codes);
            if( max_mpc_color_codes)
               mpc_color_codes = find_mpc_color_codes( n_obs, obs,
                          max_mpc_color_codes);
            if( debug_level)
               debug_printf( "got color codes; ");
            get_r1_and_r2( n_obs, obs, &r1, &r2);    /* orb_func.cpp */
            if( debug_level)
               debug_printf( "R1 = %lf; R2 = %lf\n", r1, r2);
            for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
               ;
            curr_obs = i;
            update_element_display = 1;
            clear( );
            }
         }

      if( curr_obs > n_obs - 1)
         curr_obs = n_obs - 1;
      if( curr_obs < 0)
         curr_obs = 0;
      if( debug_level > 2)
         debug_printf( "update_element_display = %d\n", update_element_display);
      if( update_element_display)
         bad_elements = write_out_elements_to_file( orbit, curr_epoch, epoch_shown,
             obs, n_obs, orbit_constraints, precision,
             is_monte_orbit, heliocentric_only);
      is_monte_orbit = 0;
      if( debug_level > 2)
         debug_printf( "elements written\n");
      update_element_display = 0;
      top_line_basic_info_perturbers = line_no;
      if( observation_display & 1)
         {
         show_basic_info( obs, n_obs);
         show_perturbers( );
         line_no = 2;
         if( debug_level)
            refresh( );
         }
      top_line_observation_info = line_no;
      if( observation_display & 2)
         for( i = 0; i < 4; i++)
            {
            char buff[190];

            generate_observation_text( obs, n_obs, curr_obs, i, buff);
            if( *buff)
               put_colored_text( buff, line_no++, 0, -1, COLOR_OBS_INFO);
            if( debug_level)
               refresh( );
            }
      top_line_orbital_elements = line_no;
      if( observation_display & 4)
         {
         FILE *ifile;

         ifile = fopen( elements_filename, "rb");
         if( ifile)
            {
            int iline = 0;
            const int elem_color = (bad_elements ?
                         256 + COLOR_OBS_INFO : COLOR_ORBITAL_ELEMENTS);

            while( fgets_trimmed( tbuff, sizeof( tbuff), ifile))
               if( iline < 20 && *tbuff != '#')
                  put_colored_text( tbuff, line_no + iline++, 0, -1, elem_color);
               else if( !memcmp( tbuff, "# Tisserand", 11))
                  {
                  tbuff[30] = tolower( tbuff[24]);
                  tbuff[29] = 'T';
                  put_colored_text( tbuff + 29, line_no + (tbuff[30] == 'n'),
                                          80, -1, elem_color);
                  }
            line_no += iline;
            fclose( ifile);
            }
         if( debug_level)
            refresh( );
         }
      top_line_residual_legend = line_no;
      if( observation_display & 8)
         show_residual_legend( line_no++, residual_format);
      if( debug_level)
         refresh( );
      if( debug_level > 2)
         debug_printf( "resid legend shown\n");

      top_line_residuals = line_no;
      show_residuals( obs, n_obs, residual_format, curr_obs, line_no,
                                       list_codes);
      if( debug_level > 2)
         debug_printf( "resids shown\n");
      if( debug_level)
         refresh( );
      show_final_line( obs, n_obs, curr_obs, COLOR_FINAL_LINE);
      if( debug_level)
         refresh( );
      if( *message_to_user)
         {
         int xloc;

         if( add_off_on >= 0)
            strcat( message_to_user, (add_off_on ? " on" : " off"));
         xloc = getmaxx( stdscr) - strlen( message_to_user) - 1;
         put_colored_text( message_to_user, getmaxy( stdscr) - 1,
                           (xloc < 0 ? 0 : xloc), -1, COLOR_MESSAGE_TO_USER);
         *message_to_user = '\0';
         }
      add_off_on = -1;
      refresh( );
      move( getmaxy( stdscr) - 1, 0);
      if( c == '|')
         if( curses_kbhit( ) != ERR)
            c = 0;
      if( c != '|')
         {
         flushinp( );
         c = extended_getch( );
         auto_repeat_full_improvement = 0;
         }

      if( base_format == RESIDUAL_FORMAT_SHORT)  /* multi-obs per line */
         {
         obs_per_line = getmaxx( stdscr) / 25;
         total_obs_lines = (n_obs - 1) / obs_per_line + 1;
         }
      else
         {
         obs_per_line = 1;
         total_obs_lines = n_obs;
         }

      if( c == KEY_MOUSE)
         {
         int x, y, z;
         unsigned long button;

         get_mouse_data( &x, &y, &z, &button);
#ifndef USE_MYCURSES
         if( debug_mouse_messages)
            sprintf( message_to_user, "x=%d y=%d z=%d button=%lx",
                              x, y, z, button);
//                            Mouse_status.button[0],
//                            Mouse_status.button[1],
//                            Mouse_status.button[2],
//                            Mouse_status.changes
#endif
         if( y >= getmaxy( stdscr) - n_stations_shown)
            c = '-';             /* toggle display of station codes */
         else if( y >= top_line_residuals)
            {
            const int max_x = getmaxx( stdscr);

            curr_obs = first_residual_shown +
                      (y - top_line_residuals);
            if( base_format == RESIDUAL_FORMAT_SHORT)  /* multi-obs per line */
               curr_obs += total_obs_lines * (x * obs_per_line / max_x);
#ifndef __WATCOMC__
            if( button & BUTTON1_DOUBLE_CLICKED)
               obs[curr_obs].is_included ^= 1;
#endif
            }
         else if( y >= top_line_residual_legend &&
                                  y < top_line_residuals)
            c = 'k';       /* cycle the residual format */
         else if( (observation_display & 1) &&
                          y == top_line_basic_info_perturbers + 1)
            {                      /* clicked on a perturber 'radio button' */
            if( x / 7 == 9)
               c = '0';
            else if( x / 7 == 10)
               c = 'a';
            else
               c = '1' + (x / 7);
            }
         else if( (observation_display & 1) &&
                          y == top_line_basic_info_perturbers)
            {
            if( x < 24)             /* clicked on R1/R2 */
               c = 'r';
            else                    /* clicked on top-line command list */
               c = command_remap[x - 24];
            }
         else if( (observation_display & 4) &&
                          y == top_line_orbital_elements + 3 && x < 40)
            c = 'e';             /* Reset epoch of elements */
         }

      if( c >= '1' && c <= '9')
         perturbers ^= (1 << (c - '0'));
#ifdef ALT_0
      else if( c >= ALT_0 && c <= ALT_9)
         curr_obs = (n_obs - 1) * (c - ALT_0) / 10;
#endif
      else switch( c)
         {
         case '0':
            perturbers ^= 1024;
            break;
         case KEY_C1:
         case KEY_END:
            curr_obs = n_obs - 1;
            break;
         case KEY_A1:
         case KEY_HOME:
            curr_obs = 0;
            break;
         case KEY_UP:
#ifdef KEY_A2
         case KEY_A2:
#endif
            curr_obs--;
            break;
         case KEY_DOWN:
#ifdef KEY_C2
         case KEY_C2:
#endif
            curr_obs++;
            break;
         case KEY_LEFT:
#ifdef KEY_B1
         case KEY_B1:
#endif
            if( base_format == RESIDUAL_FORMAT_SHORT)  /* multi-obs per line */
               curr_obs -= total_obs_lines;
            else
               curr_obs--;
            break;
         case KEY_RIGHT:
#ifdef KEY_B3
         case KEY_B3:
#endif
            if( base_format == RESIDUAL_FORMAT_SHORT)  /* multi-obs per line */
               curr_obs += total_obs_lines;
            else
               curr_obs++;
            break;
         case KEY_C3:         /* "PgDn" = lower right key in keypad */
         case KEY_NPAGE:
            curr_obs += getmaxy( stdscr) - line_no - 1;
            break;
         case KEY_A3:         /* "PgUp" = upper right key in keypad */
         case KEY_PPAGE:
            curr_obs -= getmaxy( stdscr) - line_no - 1;
            break;
         case KEY_F(1):          /* turn on/off all obs prior to curr one */
            obs[curr_obs].is_included ^= 1;
            for( i = 0; i < curr_obs; i++)
               obs[i].is_included = obs[curr_obs].is_included;
            strcpy( message_to_user, "All preceding observations toggled");
            add_off_on = obs[curr_obs].is_included;
            break;
         case KEY_F(2):          /* turn on/off all obs after curr one */
            obs[curr_obs].is_included ^= 1;
            for( i = curr_obs; i < n_obs; i++)
               obs[i].is_included = obs[curr_obs].is_included;
            strcpy( message_to_user, "All subsequent observations toggled");
            add_off_on = obs[curr_obs].is_included;
            break;
         case KEY_F(3):          /* turn on/off all obs w/same observatory ID */
            obs[curr_obs].is_included ^= 1;
            for( i = 0; i < n_obs; i++)
               if( !FSTRCMP( obs[i].mpc_code, obs[curr_obs].mpc_code))
                  obs[i].is_included = obs[curr_obs].is_included;
            strcpy( message_to_user, "All observations from xxx toggled");
            FMEMCPY( message_to_user + 22, obs[curr_obs].mpc_code, 3);
            add_off_on = obs[curr_obs].is_included;
            break;
         case KEY_F(4):          /* find prev obs from this observatory */
         case KEY_F(5):          /* find next obs from this observatory */
            {
            const int dir = (c == KEY_F(4) ? n_obs - 1 : 1);
            int new_obs = (curr_obs + dir) % n_obs;

            while( new_obs != curr_obs &&
                        FSTRCMP( obs[new_obs].mpc_code, obs[curr_obs].mpc_code))
               new_obs = (new_obs + dir) % n_obs;
            curr_obs = new_obs;
            }
            break;
         case KEY_F(6):          /* find prev excluded obs */
         case KEY_F(7):          /* find next excluded obs */
            {
            const int dir = (c == KEY_F(6) ? n_obs - 1 : 1);
            int new_obs = (curr_obs + dir) % n_obs;

            while( new_obs != curr_obs && obs[new_obs].is_included)
               new_obs = (new_obs + dir) % n_obs;
            curr_obs = new_obs;
            }
            break;
         case '*':         /* toggle use of solar radiation pressure */
            n_extra_params ^= 1;
            strcpy( message_to_user, "Solar radiation pressure is now");
            add_off_on = n_extra_params;
            break;
         case '^':
            n_extra_params = (n_extra_params == 3 ? 0 : 3);
            strcpy( message_to_user, "J002E3 parameters are now ");
            add_off_on = (n_extra_params == 3);
            break;
#ifdef __WATCOMC__
         case KEY_F(8):     /* show original screens */
            endwin( );
            extended_getch( );
            refresh( );
            break;
#endif
         case 'a': case 'A':
            perturbers ^= (7 << 20);
            strcpy( message_to_user, "Asteroids toggled");
            add_off_on = (perturbers >> 20) & 1;
            break;
         case 'b': case 'B':
            residual_format ^= RESIDUAL_FORMAT_HMS;
            strcpy( message_to_user,
                 (residual_format & RESIDUAL_FORMAT_HMS) ?
                 "Showing observation times as HH:MM:SS" :
                 "Showing observation times as decimal days");
            break;
         case 'c': case 'C':
#ifdef USE_MYCURSES
            if( c == 'c')
               curr_text_mode++;
            else
               curr_text_mode += N_TEXT_MODES - 1;
            curr_text_mode %= N_TEXT_MODES;
            set_text_mode( curr_text_mode);
            initialize_global_bmouse( );
#else
            {
            int new_xsize, new_ysize;

            inquire( "New screen size: ", tbuff, sizeof( tbuff),
                              COLOR_DEFAULT_INQUIRY);
            if( sscanf( tbuff, "%d %d", &new_xsize, &new_ysize) == 2)
               resize_term( new_ysize, new_xsize);
            }
#endif
            sprintf( message_to_user, "%d x %d text mode selected",
                        getmaxx( stdscr), getmaxy( stdscr));
            break;
         case '!':
            perturbers = ((perturbers == 0x3fe) ? 0 : 0x3fe);
            break;
         case KEY_F(9):           /* find start of included arc */
            for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
               ;
            curr_obs = i;
            break;
         case KEY_F(10):          /* find end of included arc */
            for( i = n_obs - 1; i > 0 && !obs[i].is_included; i--)
               ;
            curr_obs = i;
            break;
         case KEY_F(11):
            auto_repeat_full_improvement ^= 1;
            strcpy( message_to_user, "Automatic full improvement repeat is");
            add_off_on = auto_repeat_full_improvement;
            break;
#ifdef NOW_OBSOLETE_I_HOPE
         case KEY_F(12):            /* toggle motion details in ephemerides */
            ephem_options ^= OPTION_MOTION_OUTPUT;
            strcpy( message_to_user, "Motion details in ephemerides are");
            add_off_on = (ephem_options & OPTION_MOTION_OUTPUT);
            break;
#endif
         case 'd': case 'D':
            if( base_format == RESIDUAL_FORMAT_80_COL)
               {
               create_obs_file( obs, n_obs);
               show_a_file( "observe.txt");
               }
            else
               {
               extern const char *residual_filename;

               write_residuals_to_file( residual_filename, argv[1], n_obs, obs,
                           residual_format);
               show_a_file( residual_filename);
               }
            break;
         case 'e': case'E':
            {
            inquire( "Enter new epoch,  as YYYY MM DD, or JD,  or 'now':",
                             tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            if( extract_date( tbuff, &epoch_shown) == 1)
               epoch_shown = floor( epoch_shown) + .5;
            }
            update_element_display = 1;
            break;
         case 'f': case 'F':        /* do a "full improvement" step */
         case '|':                  /* Monte Carlo step */
            {
            double *stored_ra_decs = NULL;

            if( c == '|')
               {
               if( !monte_carlo_object_count)
                  {
                  inquire( "Gaussian noise level (arcsec): ",
                             tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
                  noise_in_arcseconds = atof( tbuff);
                  }
               stored_ra_decs =
                   add_gaussian_noise_to_obs( n_obs, obs, noise_in_arcseconds);
               }
            if( !strcmp( orbit_constraints, "e=1"))
               improve_parabolic( obs, n_obs, orbit, curr_epoch);
            else
               for( i = (c == '|' ? 5 : 1); i; i--)
                  full_improvement( obs, n_obs, orbit, curr_epoch,
                                          orbit_constraints);
            get_r1_and_r2( n_obs, obs, &r1, &r2);
            update_element_display = 1;
            if( c == '|')
               {
               extern double planet_mass[];
               ELEMENTS elem;
               double rel_orbit[6], orbit2[6];
               int curr_planet_orbiting;

               remove_gaussian_noise_from_obs( n_obs, obs, stored_ra_decs);
               is_monte_orbit = 1;
               memcpy( orbit2, orbit, 6 * sizeof( double));
               integrate_orbit( orbit2, curr_epoch, epoch_shown);
               sprintf( message_to_user, "Monte Carlo %d",
                                    monte_carlo_object_count);
               curr_planet_orbiting = find_best_fit_planet( epoch_shown,
                                  orbit2, rel_orbit);
               if( !monte_carlo_object_count)
                  planet_orbiting = curr_planet_orbiting;

               if( planet_orbiting == curr_planet_orbiting)
                  {
                  calc_classical_elements( &elem, rel_orbit, epoch_shown, 1,
                               SOLAR_GM * planet_mass[planet_orbiting]);
                  add_monte_orbit( monte_data, &elem, monte_carlo_object_count);
                  }
               if( monte_carlo_object_count > 3)
                  {
                  double sigmas[MONTE_N_ENTRIES], sigma_a;
                  FILE *monte_file = fopen( "monte.txt", "wb");
                  static const char *text[MONTE_N_ENTRIES] = {
                           "Tp", "e", "q", "Q", "1/a", "i", "M",
                           "omega", "Omega" };

                  fprintf( monte_file,
                          "Computed from %d orbits around object %d\n",
                          monte_carlo_object_count, planet_orbiting);
                  compute_monte_sigmas( sigmas, monte_data,
                                             monte_carlo_object_count);
                  for( i = 0; i < MONTE_N_ENTRIES; i++)
                     fprintf( monte_file, "sigma_%-7s%12.3lg %12.3lg %12.3lg %12.3lg\n",
                                 text[i], sigmas[i],
                                 monte_data[i],
                                 monte_data[i + MONTE_N_ENTRIES],
                                 monte_data[i + MONTE_N_ENTRIES * 2]);

                  sigma_a = sigmas[MONTE_INV_A] * elem.major_axis * elem.major_axis;
                  if( elem.major_axis > sigma_a)
                     {
                     const double sigma_P_in_days = 365.25 * 1.5 * sigma_a *
                         sqrt( elem.major_axis / planet_mass[planet_orbiting]);

                     fprintf( monte_file, "sigma_a:     %12.3lg AU\n", sigma_a);
                     fprintf( monte_file, "sigma_P:     %12.3lg days\n",
                                       sigma_P_in_days);
                     }
                  fclose( monte_file);
                  }
               }
            else
               strcpy( message_to_user, "Full step taken");
            }
            break;
         case 'g': case 'G':        /* do a method of Gauss soln */
            {
            double new_epoch;

            perturbers = 0;
            new_epoch = convenient_gauss( obs, n_obs, orbit, 1., gauss_soln++);
            if( new_epoch)
               {
               curr_epoch = new_epoch;
               set_locs( orbit, curr_epoch, obs, n_obs);
               get_r1_and_r2( n_obs, obs, &r1, &r2);
               update_element_display = 1;
               strcpy( message_to_user, "Gauss solution found");
               }
            else
               strcpy( message_to_user, "Gauss method failed!");
            }
            break;
         case '#':
         case '/':
                     /* epoch is that of first valid observation: */
            for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
                ;
            if( c == '#')
               {
               simplex_method( obs + i, n_obs - i, orbit, r1, r2);
               strcpy( message_to_user, "Simplex method used");
               }
            else
               {
               integrate_orbit( orbit, curr_epoch, obs[i].jd);
               superplex_method( obs + i, n_obs - i, orbit);
               strcpy( message_to_user, "Superplex method used");
               }
//          integrate_orbit( orbit, obs[i].jd, curr_epoch);
            curr_epoch = obs[i].jd;
            get_r1_and_r2( n_obs, obs, &r1, &r2);    /* orb_func.cpp */
            update_element_display = 1;
            break;
         case 'h': case 'H':     /* do a method of Herget step */
         case ':':               /* just linearize */
            {
            if( c != ':')
               {
               double d_r1, d_r2;

               herget_method( obs, n_obs, r1, r2, orbit, &d_r1, &d_r2,
                                          orbit_constraints);
               r1 += d_r1;
               r2 += d_r2;
               herget_method( obs, n_obs, r1, r2, orbit, NULL, NULL, NULL);
               }
            adjust_herget_results( obs, n_obs, orbit);
                     /* epoch is that of first valid observation: */
            for( i = 0; i < n_obs - 1 && !obs[i].is_included; i++)
                ;
            curr_epoch = obs[i].jd;
            update_element_display = 1;
            strcpy( message_to_user, (c == ':') ? "Orbit linearized" :
                                                  "Herget step taken");
            }
            break;
         case 'i': case 'I':
            observation_display ^= 2;
            strcpy( message_to_user, "Observation details toggled");
            add_off_on = (observation_display & 2);
            clear( );
            break;
         case 'j': case 'J':
            observation_display ^= 1;
            strcpy( message_to_user,
                     "Perturber/R1 & R2/step size data display toggled");
            add_off_on = (observation_display & 1);
            clear( );
            break;
         case 'k': case 'K':
            cycle_residual_format( &residual_format, message_to_user);
            break;
         case 'l': case 'L':
            if( !*orbit_constraints)
               inquire(
"Enter limits on the orbit (e.g.,  'e=0' or 'q=2.3' or 'q=.7,P=1.4').\n\
Constraints can be placed on e, q, Q, P, a, n, or i.",
                     orbit_constraints, sizeof( orbit_constraints),
                     COLOR_DEFAULT_INQUIRY);
            else
               {
               *orbit_constraints = '\0';
               strcpy( message_to_user, "Orbit is now unconstrained");
               }
            break;
         case 'm': case 'M':
            {
            extern const char *residual_filename;

            create_obs_file( obs, n_obs);
            create_ephemeris( orbit, curr_epoch,
                   calc_absolute_magnitude( obs, n_obs),
                   obs->is_comet);
            write_residuals_to_file( residual_filename,
                             argv[1], n_obs, obs, RESIDUAL_FORMAT_SHORT);
            make_pseudo_mpec( "mpec.htm", obj_name);      /* ephem0.cpp */
            }
            break;
         case 'n': case 'N':   /* select a new object from the input file */
            get_new_object = 1;
            update_element_display = 1;
            break;
         case 'o': case 'O':
            observation_display ^= 4;
            strcpy( message_to_user, "Display of orbital elements toggled");
            add_off_on = (observation_display & 4);
            clear( );
            break;
         case 'p':
            if( precision < 9)
               {
               precision++;
               update_element_display = 1;
               }
            break;
         case 'P':
            if( precision > 1)
               {
               precision--;
               update_element_display = 1;
               }
            break;
         case 'r': case 'R':
            inquire( "Enter new R1, R2: ", tbuff, sizeof( tbuff),
                            COLOR_DEFAULT_INQUIRY);
            if( sscanf( tbuff, "%lf%n", &r1, &i) == 1)
               {
               int j;

               while( tbuff[i] == ' ')
                  i++;
               if( tolower( tbuff[i]) == 'k')
                  {
                  r1 /= AU_IN_KM;
                  i++;
                  if( tolower( tbuff[i]) == 'm')
                     i++;
                  }
               if( !tbuff[i])    /* only one distance entered */
                  r2 = r1;
               else if( sscanf( tbuff + i, "%lf%n", &r2, &j) == 1)
                  {
                  i += j;
                  while( tbuff[i] == ' ')
                     i++;
                  if( tolower( tbuff[i]) == 'k')
                     r2 /= AU_IN_KM;
                  }
               }
            update_element_display = 1;
            break;
         case 's': case 'S':     /* save orbital elements to a file */
            {
            char filename[80];
            FILE *ofile, *ifile;;
            double orbit2[6];

            inquire( "Enter filename for saving elements: ",
                                tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            sscanf( tbuff, "%s", filename);
            ofile = fopen( filename, "wb");
            if( ofile)
               {
               ifile = fopen( elements_filename, "rb");
               while( fgets( tbuff, sizeof( tbuff), ifile))
                  fputs( tbuff, ofile);
               fclose( ifile);
               fclose( ofile);
               }

            memcpy( orbit2, orbit, 6 * sizeof( double));
            integrate_orbit( orbit2, curr_epoch, epoch_shown);
            store_solution( obs, n_obs, orbit2, epoch_shown,
                                          perturbers);
            }
            break;
         case 't': case 'T':
            residual_format ^= RESIDUAL_FORMAT_TIME_RESIDS;
            if( residual_format & RESIDUAL_FORMAT_TIME_RESIDS)
               strcpy( message_to_user, "Showing time/cross-track residuals");
            else
               strcpy( message_to_user, "Showing RA/dec residuals");
            break;
         case 'u': case 'U':
            observation_display ^= 8;
            strcpy( message_to_user,"Residual legend");
            add_off_on = (observation_display & 8);
            clear( );
            break;
         case 'v': case 'V':
            {
            double vaisala_dist, angle_param;
            int n_fields, success = 0;

            inquire( "Enter peri/apohelion distance: ", tbuff, sizeof( tbuff),
                                    COLOR_DEFAULT_INQUIRY);
            n_fields = sscanf( tbuff, "%lf,%lf", &vaisala_dist, &angle_param);
            if( n_fields == 1)      /* simple Vaisala */
               {
               herget_method( obs, n_obs, -vaisala_dist, 0., orbit, NULL, NULL,
                                                   NULL);
               adjust_herget_results( obs, n_obs, orbit);
               success = 1;
               }
            else if( n_fields == 2)       /* "trial orbit" method */
               if( !find_trial_orbit( orbit, obs, n_obs,
                                           vaisala_dist, angle_param))
                  {
                  adjust_herget_results( obs, n_obs, orbit);
                  success = 1;
                  }
            if( success)
               {
                        /* epoch is that of last included observation: */
               get_epoch_range_of_included_obs( obs, n_obs, &curr_epoch, NULL);
               get_r1_and_r2( n_obs, obs, &r1, &r2);
               update_element_display = 1;
               }
            }
            break;
         case 'w': case 'W':
            i = find_worst_observation( obs, n_obs);
            if( i > -1)
               curr_obs = i;
            break;
         case 'x': case 'X':
            if( obs[curr_obs].is_included)
               obs[curr_obs].is_included = 0;
            else
               obs[curr_obs].is_included = 1;
            strcpy( message_to_user, "Inclusion of observation toggled");
            add_off_on = obs[curr_obs].is_included;
            break;
         case 'y': case 'Y':
            show_a_file( "gauss.out");
            break;
         case 'z': case 'Z':
            {
            double state2[6], delta_squared = 0;

            inquire( "Time span: ", tbuff, sizeof( tbuff),
                              COLOR_DEFAULT_INQUIRY);
            memcpy( state2, orbit, 6 * sizeof( double));
            integrate_orbit( state2, curr_epoch, curr_epoch + atof( tbuff));
            integrate_orbit( state2, curr_epoch + atof( tbuff), curr_epoch);
            for( i = 0; i < 3; i++)
               {
               state2[i] -= orbit[i];
               delta_squared += state2[i] * state2[i];
               }
            sprintf( message_to_user, "Change = %.3e AU = %.3e km",
                              sqrt( delta_squared),
                              sqrt( delta_squared) * AU_IN_KM);
            }
            break;
         case ALT_D:
            inquire( "Debug level: ",
                                tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            debug_level = atoi( tbuff);
            break;
#ifdef __WATCOMC__
         case ALT_T:
#endif
         case '$':
            inquire( "Tolerance: ",
                                tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            if( atof( tbuff))
               {
               extern double integration_tolerance;

               integration_tolerance = atof( tbuff);
               }
            break;
         case '%':
            inquire( "Weight of this observation: ",
                                tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            if( atof( tbuff))
               {
               obs[curr_obs].weight = atof( tbuff);
               sprintf( message_to_user, "Weight reset to %.3e",
                                    obs[curr_obs].weight);
               }
            break;
         case '"':
            debug_mouse_messages ^= 1;
            strcpy( message_to_user, "Mouse debugging");
            add_off_on = debug_mouse_messages;
            break;
         case '@':
            {
            extern int setting_outside_of_arc;

            setting_outside_of_arc ^= 1;
            strcpy( message_to_user, "Setting outside of arc turned");
            add_off_on = setting_outside_of_arc;
            }
            break;
         case '(':
            set_locs( orbit, curr_epoch, obs, n_obs);
            break;
         case ')':
            inquire( "Enter name of file to be displayed: ",
                               tbuff, sizeof( tbuff), COLOR_DEFAULT_INQUIRY);
            show_a_file( tbuff);
            break;
         case '`':
            {
            extern char default_comet_magnitude_type;

            default_comet_magnitude_type =
                        'N' + 'T' - default_comet_magnitude_type;
            if( default_comet_magnitude_type == 'N')
               strcpy( message_to_user, "Using nuclear mags for comets");
            else
               strcpy( message_to_user, "Using total mags for comets");
            }
         case KEY_MOUSE:   /* already handled above */
            break;
         case 27:
         case 'q': case 'Q':
            quit = 1;
            break;
         case '=':
            residual_format ^= RESIDUAL_FORMAT_MAG_RESIDS;
            strcpy( message_to_user, "Magnitude residual display turned");
            add_off_on = (residual_format & RESIDUAL_FORMAT_MAG_RESIDS);
            break;
         case '+':
            heliocentric_only ^= 1;
            strcpy( message_to_user, (heliocentric_only ?
                     "Heliocentric elements only" :
                     "Planetocentric elements allowed"));
            update_element_display = 1;
            break;
         case '[':
            show_a_file( "covar.txt");
            break;
         case ']':
            residual_format ^= RESIDUAL_FORMAT_SHOW_DELTAS;
            strcpy( message_to_user, "Delta display turned");
            add_off_on = (residual_format & RESIDUAL_FORMAT_SHOW_DELTAS);
            break;
         case '-':
            list_codes ^= 1;
            strcpy( message_to_user, "Codes listing turned");
            add_off_on = list_codes;
            break;
         case ',':
            show_a_file( "debug.txt");
            break;
         case '.':
            strcpy( message_to_user, longname( ));
            break;
#ifdef __PDCURSES__
         case KEY_RESIZE:
            resize_term( 0, 0);
            break;
#endif
         case '{': case '}': case '\\':             /* currently unassigned */
         case '\'': case '~':                       /* hotkeys */
         case ';': case '&': case '_':
         case KEY_F(12): case '>': case '<':
         default:
            debug_printf( "Key %d hit\n", c);
            show_a_file( "dos_help.txt");
            break;
         }
      }
   attrset( COLOR_PAIR( COLOR_BACKGROUND));
   show_final_line( obs, n_obs, curr_obs, COLOR_BACKGROUND);
#ifdef __PDCURSES__
   resize_term( original_ymax, original_xmax);
#endif
// refresh( );
   endwin( );
   free_weight_recs( );
   create_obs_file( obs, n_obs);

   option_file = fopen( option_filename, "wb");
   fprintf( option_file, "%s %d %d %d %d\n", mpc_code, precision - 5,
             observation_display, residual_format, list_codes);
   store_defaults( ephem_options);                     /* elem_out.c */
   fprintf( option_file, "%s\n%s\n", command_text, command_remap);
   fprintf( option_file, "%s\n", ephemeris_start);
   fprintf( option_file, "%s\n", ephemeris_step_size);
   fprintf( option_file, "%s\n", ephemeris_end);
   fclose( option_file);
   free( ids);
#ifdef XCURSES
   XCursesExit();
#endif
   exit(0);
   return( 0);
}
