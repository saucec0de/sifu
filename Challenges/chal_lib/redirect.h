/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#ifndef __REDIRECT_H__
#define __REDIRECT_H__
#include <time.h>

extern char **printString;
extern int    nPrintString;
extern char **formatString;
extern int    nFormatString;
extern int    overrideTime;
extern int    randCall;
extern int    overrideSrand;
extern int    nGetS;

#define printf redirected_printf
int redirected_printf(const char * format, ...);
int original_printf(const char * format, ...);

#define time redirected_time
time_t redirected_time(time_t *tloc);

#define rand redirected_rand
int redirected_rand(void);

#define srand redirected_srand
void redirected_srand(unsigned int seed);

#define gets redirected_gets
char *redirected_gets( char *str );

#endif
