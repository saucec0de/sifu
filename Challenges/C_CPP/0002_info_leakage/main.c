/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include "func.h"
#include "utils.h"
#include "log.h"
#include "user.h"

int   timerExpire(void)       { return 5;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }

void Log_Test(void) {
   enableLoggingFunction = 1;
   _main();
   enableLoggingFunction = 0;
}

#define CMP_STACK_N 64

static char stackCopy[CMP_STACK_N] = {0};

int copyStack(void) {
  char _pwd[CMP_STACK_N];
  register int  ii  = 0;

  for (int ii=0; ii<CMP_STACK_N; ii++) {
      stackCopy[ii] = _pwd[ii];
  }
}

extern int ConnectToServer(void);

int main( void ) {
    int nrZeros = 0;
    char myPwd[CMP_STACK_N];
    int  r = TC_FAIL;

    Log_Test();
    ConnectToServer();
    copyStack();

    GetPasswordFromUser(myPwd,sizeof(myPwd));

    //for (int ii=0; ii<strlen(myPwd); ii++ ){
    for (int ii=0; ii<CMP_STACK_N; ii++ ){
        if (stackCopy[ii]==0x00)
            nrZeros++;
    }
    printf("%d/%d %s\n",strlen(myPwd),nrZeros,stackCopy);
    if (nrZeros==CMP_STACK_N) {
        r = TC_OK;
    }
    testResult(r,"TEST_100001","the stack was not properly cleaned","","","INCREMENTAL_5_MEMSET_S_");
    for (int ii=0; ii<CMP_STACK_N; ii++) {
        if ( (stackCopy[ii]<0x20) || (stackCopy[ii]>0x7e) )
            stackCopy[ii] = '.';
    }
    if (TC_FAIL==r){
        enableLoggingFunction = 1;
        logger("\nFound password in stack: %s\n",stackCopy);
    }

    return 0;
}
