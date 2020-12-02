/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "log.h"
#include "user.h"
#include <stdbool.h>

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }

extern int _main( int argc, char **argv );

int main( int argc, char **argv ) {
    bool canLogin;
    int  passFail;

    enableLoggingFunction = 1;
    printf("START TEST\n");

    if (argc>1) {
        if (strcmp(argv[1],"a")==0) {
            canLogin = checkUserLogin(0,"passWord..");
            if (canLogin) {
                printf("TC 1a: pass\n");
                passFail = 1;
            } else {
                printf("TC 1a: fail\n");
                passFail = 0;
            }
            testResult(passFail,"TEST_100000","Test login of some user","","","");

            canLogin = checkUserLogin(0,"passWord.");
            if (canLogin) {
                printf("TC 2a: fail\n");
                passFail = 0;
            } else {
                printf("TC 2a: pass\n");
                passFail = 1;
            }
            testResult(passFail,"TEST_100000","Test failed login of some user","","","");

            canLogin = checkUserLogin(0,"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");
            if (canLogin) {
                printf("TC 3a: fail\n");
                passFail = 0;
            } else {
                printf("TC 3a: pass\n");
                passFail = 1;
            }
            testResult(passFail,"TEST_100000","This code can be tricked to login any user","","","INCREMENTAL_2_FUNC_8948618040_A_");
        } else
        if (strcmp(argv[1],"b")==0) {
            canLogin = checkUserLogin(0,"passWord..");
            if (canLogin) {
                printf("TC 1b: pass\n");
                passFail = 1;
            } else {
                printf("TC 1b: fail\n");
                passFail = 0;
            }
            testResult(passFail,"TEST_900000","Test login of some user","","","");

            canLogin = checkUserLogin(0,"passWord.");
            if (canLogin) {
                printf("TC 2b: fail\n");
                passFail = 0;
            } else {
                printf("TC 2b: pass\n");
                passFail = 1;
            }
            testResult(passFail,"TEST_900000","Test failed login of some user","","","");
        } else {
            testResult(0,"TEST_1000","Internal error - check with coaches","","","");
        }
    }
    printf("END TEST\n");
    return 0;
}
