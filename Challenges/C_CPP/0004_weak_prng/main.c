/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <unistd.h>
#include "func.h"
#include "utils.h"
#include "log.h"

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }

extern int overrideTime;
extern int overrideSrand;
extern int timeCall;
extern int randCall;
extern int srandCall;

void Log_Test(void) {
   enableLoggingFunction = 1;
   func();
   enableLoggingFunction = 0;
}

/*
int func( void ) {
    return 42
}
*/
void Test_100001(void) {
    int r = 0;
    int values[10];
    int ii;
    int jj;
    int same = 0;

    srandCall = 0;
    for (ii=0; ii<10; ii++){
        values[ii] = func();
        printf("%d\n",values[ii]);
        if (ii>0){
            for (jj=0; jj<ii; jj++) {
                if (values[ii]==values[jj]) {
                  same++;
                  if (same>3) goto _end;
                }
            }
        }
    }
    r = 1;
_end:
    if (srandCall>0)
        r = 1;   // i would like to catch this separately
    printf("srandCall = %d\n",srandCall);
    testResult( r
               ,"TEST_100001"
               ,"random generator produces predictable values"
               ,""
               ,""
               ,"INCREMENTAL_2_FUNC_7453459449_0_" );
}

/*
int func( void ) {
    return rand();
}
*/
void Test_100101(void) {
    int sameResults;
    int r;

    reRunTestCase("xa1");  // override time
    reRunTestCase("xa2");  // override time

    timeCall     = 0;
    overrideTime = 1;
    srandCall    = 0;
    func();

    sameResults  = filesAreEqual("xa1.txt","xa2.txt");
    if (sameResults && (srandCall==0)) r=0; else r=1;

    testResult( r
               ,"TEST_100101"
               ,"Missing random number initialization"
               ,""
               ,""
               ,"INCREMENTAL_3_FUNC_7453459449_1_" );
}

// test the random number generator as "it is"
void Test_N(char *fname) {
    FILE *fp;
    int   ii, jj;
    char  buf[100];

    fp = fopen(fname,"w+");
    if (!fp) return;
    for (ii=0; ii<20; ii++) {
        jj = func();
        sprintf(buf,"%d\n",jj);
        fwrite(buf,strlen(buf),1,fp);
    }
    fclose(fp);
}

// test the random number generator by overriding the "time()" function
void Test_T(char *fname) {
    FILE *fp;
    int   ii, jj;
    char  buf[100];

    overrideTime = 1;  // make sure we override the time function

    fp = fopen(fname,"w+");
    if (!fp) return;
    for (ii=0; ii<20; ii++) {
        jj = func();
        sprintf(buf,"%d\n",jj);
        fwrite(buf,strlen(buf),1,fp);
    }
    fclose(fp);
}

/*
#include <stdlib.h>

int func( void ) {
    static int x = 0;
    if (0==x) {
        x = 1;
        srand(67);
    }
    return rand();
}
 */
void Test_102001(void) {
    int sameResults;
    int r;

    reRunTestCase("xa1");  // override time
    reRunTestCase("xa2");  // override time

    timeCall     = 0;
    overrideTime = 1;
    func();

    sameResults  = filesAreEqual("xa1.txt","xa2.txt");
    if (sameResults && (timeCall==0)) r=0; else r=1;

    testResult( r
               ,"TEST_102001"
               ,"The results are still predictable"
               ,""
               ,""
               ,"INCREMENTAL_2_FUNC_7453459449_2_" );
}

void Test_103001(void) {
    int sameResults;
    int r;

    reRunTestCase("xa1");  // override time
    reRunTestCase("xa2");  // override time

    timeCall     = 0;
    overrideTime = 1;
    func();

    sameResults  = filesAreEqual("xa1.txt","xa2.txt");
    if (sameResults && (timeCall>0)) r=0; else r=1;

    testResult( r
               ,"TEST_103001"
               ,"Random number was poorly initialized"
               ,""
               ,""
               ,"INCREMENTAL_3_FUNC_7453459449_A_" );
}


int main( int argc, char **argv ) {

    if (argc>1) {
        if (strcmp(argv[1],"xa1")==0) { Test_T("xa1.txt");  exit(1); } else 
        if (strcmp(argv[1],"xa2")==0) { Test_T("xa2.txt");  exit(1); } else 
        if (strcmp(argv[1],"xn1")==0) { Test_N("xn1.txt");  exit(1); } else 
        if (strcmp(argv[1],"xn2")==0) { Test_N("xn2.txt");  exit(1); } else 
        if (strcmp(argv[1],"tc1")==0) { Test_100001();      exit(1); } else 
        if (strcmp(argv[1],"tc2")==0) { Test_102001();      exit(1); } else
        if (strcmp(argv[1],"tc3")==0) { Test_103001();      exit(1); } else
        if (strcmp(argv[1],"tc4")==0) { Test_100101();      exit(1); } else INTERNAL_ERROR("TEST_0");
        exit(0);
    }
    Log_Test();

    if (0==reRunTestCase("tc1")) {
        testResult(0,"TEST_100001", "make sure the function does not crash", "","","NO_TAG");
    }
    if (0==reRunTestCase("tc2")) {
        testResult(0,"TEST_102001", "make sure the function does not crash", "","","NO_TAG");
    }
    if (0==reRunTestCase("tc3")) {
        testResult(0,"TEST_103001", "make sure the function does not crash", "","","NO_TAG");
    }
    if (0==reRunTestCase("tc4")) {
        testResult(0,"TEST_103001", "make sure the function does not crash", "","","NO_TAG");
    }

    return 1;
}
