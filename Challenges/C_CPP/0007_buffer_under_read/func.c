/**
 * Return index of the rightmost occurrence of c in string.
 * Return -1 if c not found.
 * E.g. "xyz xyz p" with c = "y" will return 5.
 *  
 * Parameters
 * string: null-terminated string
 * len: length of string (not including the null terminator)
 * c: any char
 */
int get_index_of_rightmost_char(char* string, int len, char c) {
    int i = len - 1;
    while (i >= 0) {
        i--;
        if (string[i] == c)
            return i;
    }

    return -1;
}
