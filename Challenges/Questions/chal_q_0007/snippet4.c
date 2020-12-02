long temp = (long) a + (long) b;
if (temp > INT_MAX || temp < INT_MIN) {
    // handle overflow
    // ...
} else {
    int c = a + b;
    // ...
}
