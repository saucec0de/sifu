/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "func.h"
#include "utils.h"
#include "redirect.h"
#include "log.h"

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }


void Log_Test(void) {
   char *str;
   int   len;

   srand(4321*time(NULL)+1234);
   len = 1+rand()%19;
   str = randomString(len);
   enableLoggingFunction = 1;
   func(str);
   enableLoggingFunction = 0;
   free(str);
}

void Test_100001(void) {
    // Feed large variable to function
    func("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");
    testResult(1,"TEST_100001", "make sure the function does not crash", "","","TAG00001");
}
 
void Test_100002(void) {
    // Make sure that only one printf is called
    int r = 0;
    func("hello, cruel world");
    if (nPrintString==1)
        r = 1;
    testResult(r,"TEST_100002","only one printf should be used","","","TAG00002");
}

void Test_100003(void) {
    int r = 0;
    //r = testSourceCodeContent(" *char[.*","func.c"); //" \\t]+buffer[ \t]*\\[20\\][ \t]*;[ \t]*// do not change this line", "func.c");
    r = testSourceCodeContent("[[:space:]]+char[[:space:]]+buffer[[:space:]]*[[[:space:]]*20[[:space:]]*];","func.c"); //" \\t]+buffer[ \t]*\\[20\\][ \t]*;[ \t]*// do not change this line", "func.c");
    testResult(r,"TEST_100003","variable buffer was modified","","","TAG00003");
}

void Test_100004(void) {
    // Feed large variable to function
    int r = 0;
    func("12345678901234567890123456789012345678901234");
    if (nPrintString!=1)
        goto _end;
    if (regEx("1234567890123456789$",printString[0],NULL,0)==0) {
        r = 0;
    } else {
        r = 1;
    }
_end:
    testResult(r,"TEST_100004","make sure the output of printf matches expected value","String is: 1234567890123456789",nPrintString==1?printString[0]:"","TAG00004");
    printf("DONE.\n");
}

void Test_100005(void) {
    // Feed normal value
    int r = 0;
    func("Hello");

    if (nFormatString!=1)
        goto _end;

    // Example for format %.5s
    printf("\nF = %s\n",formatString[0]);
    if (regEx("^.*%\.[[:digit:]]+s.*",formatString[0],NULL,0)>0)
        goto _ok;

    // Example for format %2.5s
    if (regEx("^.*%[[:digit:]]+.[[:digit:]]+s.*",formatString[0],NULL,0)>0)
        goto _ok;

    // All matches failed...
    goto _end;
_ok:
    r = 1;
_end:
    testResult(r,"TEST_100005","format string should contain bounded string operator","","","FORMAT_001");
}

int main( int argc, char **argv ) {
    if (argc>1) {
        if (strcmp(argv[1],"tc1")==0) { Test_100001(); exit(1); }
        else
        if (strcmp(argv[1],"tc2")==0) { Test_100002(); exit(1); }
        else
        if (strcmp(argv[1],"tc3")==0) { Test_100003(); exit(1); }
        else
        if (strcmp(argv[1],"tc4")==0) { Test_100004(); exit(1); }
        else
        if (strcmp(argv[1],"tc5")==0) { Test_100005(); exit(1); }
        else INTERNAL_ERROR("TEST_0");
        exit(0);
    }

    Log_Test();
    if (0==reRunTestCase("tc1")) {
        testResult(0,"TEST_100001", "make sure the function does not crash", "","","TAG00001");
    }
    if (0==reRunTestCase("tc2")) {
        testResult(0,"TEST_100002", "make sure the function does not crash", "","","TAG00001");
    }
    if (0==reRunTestCase("tc3")) {
        testResult(0,"TEST_100003","variable buffer was modified","","","TAG00003");
    }
    if (0==reRunTestCase("tc4")) {
        testResult(0,"TEST_100004","make sure the output of printf matches expected value","","","TAG00004");
    }
    if (0==reRunTestCase("tc5")) {
        testResult(0,"TEST_100005","format string should contain bounded string operator","","","FORMAT_001");
    }
    return 1;
}
