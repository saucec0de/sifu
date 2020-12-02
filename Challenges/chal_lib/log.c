#define _GNU_SOURCE
/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int enableLoggingFunction = 0;

void logger(const char * format, ...) {
    static int logStart = 0;
    size_t ii;

    if (1==enableLoggingFunction) {
        char* outstr = 0;
        FILE *fp;
        va_list ap;
        va_start(ap, format);
        int result = vasprintf(&outstr, format, ap);
        va_end(ap);
        if(result < 0)
            return;
        fp = fopen("sifu_results/log.txt","a+");
        if (fp==NULL)
            return;
        if (logStart==0) {
            logStart = 1;
            fwrite("---- START Logging ----\n",24,1,fp);
        }

        for (ii=0; ii<strlen(outstr); ii++){
          if ( ! ((outstr[ii]>=32) && (outstr[ii]<=126)) )  {
            outstr[ii] = '.';
          }
        }
        fwrite(outstr,strlen(outstr),1,fp);
        if (outstr[strlen(outstr)-1]!='\n') fwrite("\n",1,1,fp);
        fclose(fp);
        free(outstr);
    }
}

