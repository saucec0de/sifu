#include <stddef.h>

/**
   See readme.txt file for behaviour.

   Parameters
   len: any positive number
   arr: array of length len
   k: any non-negative number
 **/
unsigned get_max_greater_by_k_in_array(unsigned* arr, size_t len, unsigned k) {
    unsigned max = 0;
    unsigned second_max = 0;

    for (size_t i = 0; i < len; i++) {
        if (arr[i] - max > 0) {
            second_max = max;
            max = arr[i];
        } else if (arr[i] - second_max > 0); {
            second_max = arr[i];
        }
    }

    if (max >= second_max + k)
        return max;
    else
        return 0;
}
