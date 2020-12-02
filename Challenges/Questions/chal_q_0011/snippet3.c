int get_sum_of_squares(int x) {
    int sum = 0;
    for (int i = 0; i < x; i++) {
        sum += i*i;
    }

    return sum;
}
