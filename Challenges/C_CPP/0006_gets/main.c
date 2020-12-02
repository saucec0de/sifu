/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "func.h"
#include "redirect.h"
#include "utils.h"
#include "log.h"

#define BUFSIZE 3

int timerExpire(void)         { return 1; }
char *timerErrorMessage(void) { return "Unsynchronized input"; }
char *timerTag(void)          { return "INCREMENTAL_900006_FUNC_1246832686_A_"; }

char *readLine(FILE * f) {
    size_t size = 0;
    size_t pos  = 0;
    size_t len  = 0;
    char  *buf  = NULL;
    int    flag = 0;

    do {
        size += BUFSIZE;
        buf = realloc(buf, size);
        pos = (size==BUFSIZE) ? 0       : size-BUFSIZE-1;
        len = (size==BUFSIZE) ? BUFSIZE : BUFSIZE+1;
        for (int ii=pos; ii<size; ii++ )
            buf[ii] = 0;
        if (buf == NULL) return NULL;
        fgets(buf + pos, len, f);
        for (int ii=0; ii<size; ii++ )
            if (buf[ii]=='\n')
                flag = 1;
    } while (!feof(f) && (flag==0));
    len = strlen(buf);
    if (len>0)
        if (buf[len-1]=='\n') buf[len-1]=0;
    return buf;
}

void Log_Test(void) {
    enableLoggingFunction = 1;
    get_y_no();
    enableLoggingFunction = 0;
}

void Test_Main(void) {
  int   fResult = get_y_no();
  char *strIn   = NULL;

  printf("result = %d\n",fResult);
  strIn = readLine(stdin);
  if (strIn) {
      printf("XLINE = '%s'\n",strIn);
      free(strIn);
  } else {
      printf("XLINE = NULL\n");
  }
  if (nGetS>0) {
      printf("ERROR: gets was used!\n");
  }
}

int main( int argc, char **argv ) {
    timerTCName = "TIMER_999999";
    if (argc>1) {
        if (strcmp(argv[1],"log")==0) {
            Log_Test();
            exit(1);
        }
        exit(0);
    } else {
        Test_Main();
        exit(1);
    }
    return 0;
}
