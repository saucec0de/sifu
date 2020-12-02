int get_next_even_number(void) {
    static int number = -2;
    
    number += 2;
    
    return number;
}
