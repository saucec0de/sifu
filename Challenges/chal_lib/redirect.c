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
#include <time.h>

char **printString   = NULL;
int    nPrintString  = 0;
char **formatString  = NULL;
int    nFormatString = 0;
int    overrideTime  = 0;
int    timeCall      = 0;
int    randCall      = 0;
int    overrideSrand = 0;
int    srandCall     = 0;
int    nGetS         = 0;


void addString(const char *s) {
    if (NULL==printString) {
        printString = (char **)malloc(sizeof(char*));
    } else {
        printString = (char **)realloc(printString,(1+nPrintString)*sizeof(char*));
    }
    printString[nPrintString] = (char*)malloc(1+strlen(s));
    strncpy(printString[nPrintString],s,1+strlen(s));
    nPrintString++;
}


void addFormatString(const char *fmt) {
    if (NULL==formatString) {
        formatString = (char **)malloc(sizeof(char*));
    } else {
        formatString = (char **)realloc(formatString,(1+nFormatString)*sizeof(char*));
    }
    formatString[nFormatString] = (char *)malloc(1+strlen(fmt));
    strncpy(formatString[nFormatString],fmt,1+strlen(fmt));
    nFormatString++;
}

int original_printf(const char * format, ...) {
    char* outstr = 0;
    va_list ap;
    va_start(ap, format);
    int result = vasprintf(&outstr, format, ap);
    va_end(ap);
    if(result < 0)
        return result;
    printf("%s",outstr);
    free(outstr);
    return result;
}

int redirected_printf(const char * format, ...) {
    char* outstr = 0;
    va_list ap;
    va_start(ap, format);
    int result = vasprintf(&outstr, format, ap);
    va_end(ap);
    if(result < 0)
        return result;
    printf("%s",outstr);
    addString(outstr);
    addFormatString(format);
    free(outstr);
    return result;
}

time_t redirected_time(time_t *tloc) {
    timeCall++;
    if (overrideTime) {
        return 4444;
    } else {
        return time(tloc);
    }
}

int redirected_rand(void) {
    randCall++;
    return rand();
}

void redirected_srand(unsigned int seed) {
    srandCall++;
    if (overrideSrand) {
    } else {
        srand(seed);
    }
}

char *redirected_gets( char *str ) {
    nGetS++;
    return fgets(str, 4096*256, stdin);
}


