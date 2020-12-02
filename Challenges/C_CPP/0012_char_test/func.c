#include <stdio.h>

/**
   Return 1 if the next character on stdin is a letter.
   If not, return 0. If end-of-file is reached, return -1.
 **/
int is_letter() {
    char c = getchar();

    if ('a' <= c <= 'z' || 'A' <= c <= 'Z')
        return 1;
    else if (c = EOF)
        return -1;
    else
        return 0;
}
