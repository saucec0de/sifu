#include <stdio.h>
#include <stdlib.h>

int main( void ) {
    void *p = malloc(100);
    free(p);
    return 0;
}
