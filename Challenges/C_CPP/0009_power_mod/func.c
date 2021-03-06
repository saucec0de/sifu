#include <stdint.h>

/**
 * Return a^p (mod n). Return -1 if answer is undefined (for e.g. 0^0).
 * 
 * Parameters
 * 0 <= a <= INT32_MAX
 * 0 <= p
 * 0 <= n <= sqrt(INT32_MAX) (rounded down)
 */
int32_t get_power_mod(int32_t a, int32_t p, int32_t n) {
    if (a == 0 && p == 0)
        return -1;

    int prod = 1;
    for (int i = 0; i < p; i++) {
        prod *= a;
    }

    return prod % n;
}
