Expected behaviour of get_max_greater_by_k_in_array:

Return maximum number in the array only if
the maximum is larger than all other numbers by
at least k.
Else return 0.

E.g.
With arr being {1, 2, 3, 4, 6}
    get_max_greater_by_k_in_array(arr, 5, 2)
will return 6
but with arr being {1, 2, 3, 4, 5},
it will return 0.

Similarly,
    get_max_greater_by_k_in_array(arr, len, 1)
will only return a non-zero value if there is only
one maximum in the array (unless the maximum
itself happens to be 0).

    get_max_greater_by_k_in_array(arr, len, 0)
The above will simply return the maximum value in the
array.

If arr has just one element
    get_max_greater_by_k_in_array(arr, 1, k)
will return that element regardless of the
value of k.


