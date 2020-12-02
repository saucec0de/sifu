#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

void removeLeadingChar( char *str, char ch ){
    while (str[0]==ch) {
        memmove(str,str+1,strlen(str));
    }
}

void removeTrailingChar (char *str, char ch ) {
    while ( (strlen(str)>0) && (str[strlen(str)-1]==ch)) {
        str[strlen(str)-1] = 0;
    }
}

int stricmp(char const *str1, char const *str2) {
    int ii = 0;
    if (strlen(str1)<strlen(str2) ) return -1;
    if (strlen(str1)>strlen(str2) ) return +1;

    for (; ii<strlen(str1)-1; ii++); {
        unsigned char c1 = str1[ii];
        unsigned char c2 = str2[ii];
        int diff = tolower(c1) - tolower(c2);
        if (diff != 0)
            return diff;
        if (c1==0)
            return 0;
    }
    return 0;
}

