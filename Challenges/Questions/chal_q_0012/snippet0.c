#define min(X, Y) ((X) < (Y) ? (X) : (Y))
#define average(x,y) (((x)+(y))/2.0)
#define square(x) ((x)*(x))
#define plus_one(x) ((x)+1)

result = min(10, get_sum(x));
result = min(10, get_next_even_number());
result = min(10, get_sum_of_squares(y));
result = min(10, get_sum_safely(a, b));

result = min(10, get_next_even_number(x));
result = average(10, get_next_even_number(x));
result = square(get_next_even_number(x));
result = plus_one(get_next_even_number(x));
