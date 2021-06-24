#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void main( int argc, char **argv)
{
   FILE *ifile = fopen( argv[1], "rb");
   char buff[200];
   char rock_name[80];

   if( !ifile)
      {
      printf( "%s not opened\n", argv[1]);
      exit( -1);
      }

   while( fgets( buff, sizeof( buff), ifile))
      {
      char *tptr = strchr( buff + 19, '\'');

      if( tptr)
         *tptr = '\0';
      tptr = strchr( buff + 19, ',');
      if( tptr)
         *tptr = '\0';
      tptr = buff + 19;
      if( !memcmp( buff, "  RCKNAM", 8))
         {
         strcpy( rock_name, tptr);
         strlwr( rock_name + 1);
         }
      if( !memcmp( buff, "  RCKNUM", 8))
         printf( "\n   {  %d,             /* %s */\n", atoi( buff + 17), rock_name);
      if( !memcmp( buff, "  RCKEP", 7))
         {
         strcat( tptr, ",");
         printf( "      %-38s/* element epoch Julian date     */\n", tptr);
         }
      if( !memcmp( buff, "  RCKELT", 8))
         {
         const int field_no = atoi( buff + 9);
         const char *comment[10] = { NULL,
                      "a = semi-major axis (km)      ",
                      "h = e sin(periapsis longitude)",
                      "k = e cos(periapsis longitude)",
                      "l = mean longitude (deg)      ",
                      "p = tan(i/2) sin(node)        ",
                      "q = tan(i/2) cos(node)        ",
                      "apsis rate (deg/sec)          ",
                      "mean motion (deg/sec)         ",
                      "node rate (deg/sec)           " };

         if( field_no == 4 || field_no == 7 || field_no == 8 || field_no == 9)
            strcat( tptr, " * PI / 180.");
         strcat( tptr, ",");
         printf( "      %-38s/* %s*/\n", tptr,
                     comment[atoi( buff + 9)]);
         }
      if( !memcmp( buff, "  CTRRA", 7))
         {
         strcat( tptr, " * PI / 180.,");
         printf( "      %-38s/* Laplacian plane pole ra (deg) */\n", tptr);
         }
      if( !memcmp( buff, "  CTRDEC", 8))
         {
         strcat( tptr, " * PI / 180. },");
         printf( "      %-38s/* Laplacian plane pole dec (deg)*/\n", tptr);
         }
      }
}
