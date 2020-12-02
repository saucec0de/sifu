#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "user_mgmt.h"

bool checkUserLogin( int userID, char *userPass ) {
    HASH computeUserPassHash = 0;
    HASH fromDBUserPassHash  = 0;
    bool canLogin            = false;
    char genPass[100];

    memset(genPass,0,sizeof(genPass));
    strcat(genPass,"3380355_FIXED_SALT_2794089::");
    strncat(genPass,userPass,sizeof(genPass));
    computeUserPassHash = simpleHash(genPass);
    fromDBUserPassHash  = getUserPassHash(userID);
    if (computeUserPassHash==fromDBUserPassHash)
        canLogin = true;
    return canLogin;
}
