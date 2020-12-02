/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <iostream>
#include "func.h"
#include "utils.h"
#include "log.h"

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }

void Log_Test(void) {
   enableLoggingFunction = 1;
   _main();
   
   enableLoggingFunction = 0;
}




int main( void ) {
    int nrZeros = 0;
    char myPwd[64];
    int  r = TC_FAIL;
    Log_Test();
    
    testResult(1,"TEST_100","Test when everything works","","","NO_TAG");
        

    return 0;
}
