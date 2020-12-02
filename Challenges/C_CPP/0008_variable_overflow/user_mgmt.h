/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#ifndef __USER_MANAGEMENT__
#define __USER_MANAGEMENT__

typedef unsigned long HASH;

HASH simpleHash(char *str);
HASH getUserPassHash( int id );

#endif
