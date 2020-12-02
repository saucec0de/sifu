if ((a > INT_MAX - b && b > 0) || (a < INT_MIN - b && b < 0)) {
    // handle overflow
    // ...
} else {
    int c = a + b;
    // ...
}
