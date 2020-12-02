/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "redirect.h"
#include "log.h"

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }

extern int _main( int argc, char **argv );

int main( void ) {
    enableLoggingFunction = 1;
    _main(1,NULL);
    return 0;
}
