/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include "user_mgmt.h"

HASH simpleHash(char *str) {
    // inspired in https://stackoverflow.com/questions/7666509/hash-function-for-string
    unsigned long hash = 5381;
    int c;

    while (c = (unsigned char)*str++)
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */

    return hash;
}

HASH getUserPassHash( int id ) {
    if (id<0)
        return 1;
    switch (id) {
        case 0: return simpleHash("3380355_FIXED_SALT_2794089::passWord..");
        case 1: return simpleHash("3380355_FIXED_SALT_2794089::$blaBLA$");
        case 2: return simpleHash("3380355_FIXED_SALT_2794089::Viking4Free");
        case 3: return simpleHash("3380355_FIXED_SALT_2794089::3mptyNess00");
        default: return 0;
    }
    return 0;
}

