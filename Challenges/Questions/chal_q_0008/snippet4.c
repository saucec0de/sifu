unsigned long temp = (unsigned long) a + (unsigned long) b;
if (temp > UINT_MAX) {
    // handle overflow
    // ...
} else {
    unsigned c = a + b;
    // ...
}
