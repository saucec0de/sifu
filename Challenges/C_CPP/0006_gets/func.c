#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int get_y_no( void ) {
    char b[3];

    if (!gets(b)) {
        return 0;
    } else {
        if ( (b[0]=='y') || (b[0]=='Y') ) {
            return 1;
        }
        free(b);
    }
    return 0;
}
