#include <stddef.h>

/***
   Copy the first n-1 chars from src to dest,
   if the string src has length at least n-1.
   Then add a null terminator as the nth char.
   If src has length less than n-1, copy the
   entire string src (including the '\0')
   to dest

   Note: the length of a string is the number
   of chars in the string before the '\0' character.

   Parameters:
   n: any non-negative number
   src: a string
   dest: an array of size at least n
*/
void copy_strings(size_t n, char* dest, char* src) {
    size_t i;

    for (i = 0; src[i] && (i < n - 1); i++) {
        dest[i] = src[i];
    }

    dest[i] = '\0';
}

