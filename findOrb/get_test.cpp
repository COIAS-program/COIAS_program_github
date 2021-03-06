#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include "watdefs.h"
#include "date.h"

/* Test routine for get_time_from_string().  This function is supposed
to puzzle out a huge range of bizarre inputs,  such as "March 4" (fourth
day of March) vs. "4 Mar" and so on.  'get_test.txt' contains some example
inputs;  'get_test' reads those inputs,  prints out the resulting times,
and you can then check to make sure that the approved output resulted
by comparing it to 'get_test.out'.        */

int main( int argc, char **argv)
{
   FILE *ifile = fopen( argc == 1 ? "get_test.txt" : argv[1], "rb");

   if( ifile)
      {
      char buff[80];
      double jd = 0;
      int i, time_format = 0;

      while( fgets( buff, sizeof( buff), ifile))
         {
         for( i = 0; buff[i] >= ' '; i++)
            ;
         buff[i] = '\0';
         if( !memcmp( buff, "format", 6))
            {
            sscanf( buff + 6, "%x", &time_format);
            printf( "%s\n", buff);
            }
         else if( *buff != ';')
            {
            char obuff[80];

            jd = get_time_from_string( jd, buff, time_format);
            full_ctime( obuff, jd, FULL_CTIME_MILLISECS | CALENDAR_JULIAN_GREGORIAN);
            printf( "%s  %s\n", obuff, buff);
            }
         }
      fclose( ifile);
      }
   return( ifile ? 0 : -1);
}
