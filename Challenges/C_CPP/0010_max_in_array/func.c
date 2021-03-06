#include <stddef.h>

/**
  Return maximum number in the array
  
  Parameters
  len: any positive number
  arr: array of length len
**/

unsigned get_max_in_array(unsigned* arr, size_t len ) {
    unsigned max = 0;
    for (size_t i = 0; i < len; i++) {
        if (arr[i] - max > 0)
            max = arr[i];
    }

    return max;
}
