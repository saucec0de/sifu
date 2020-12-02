unsigned get_sum_safely(unsigned x, unsigned y) {
    if (x + y < x) {
        printf("Overflow in function get_sum_safely!");
        return 0;
    }

    return x + y;
}
