#ifndef __GUARD__DEPRECATED_H__
#define __GUARD__DEPRECATED_H__
/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/


// inspired in https://stackoverflow.com/questions/295120/c-mark-as-deprecated

////////////////////////////////////////////////////////////////////////////////////////////
//                       Deprecated functions - should not be used                        //
////////////////////////////////////////////////////////////////////////////////////////////
char *strcpy(char *dest, const char *src) __attribute__ ((deprecated));

#endif
