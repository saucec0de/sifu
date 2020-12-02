#include <stdio.h>
#include <stdlib.h>
#include "func.h"

/***
   Change the colour of lamp lights according to the passed argument
   Return 0 if colour was successfully switched, else 1.
   
   See readme.txt for more details.

   Note: if the caller passes a colour that is not supported by
   the executable, then return 1 (i.e. colour not successfully switched).

   Parameter:
   colour: any arbitrary string
**/
int switch_colour(char* colour) {
    char cmd[CMD_MAX];
    cmd[0] = '\0';

    snprintf(cmd, CMD_MAX, "%s %s %s",
             switch_colour_exe_path, "-c", colour);

    if (system(cmd))
        return 1;
    else
        return 0;
}
