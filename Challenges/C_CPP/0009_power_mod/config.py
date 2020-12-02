# TODO
# will probably use classes later. enums can help too
# allow for a default config file
import random
import string
import re
from math import sqrt, floor

import util

filenames = ['./main.c',
             './func.c',
             './utilities.c']
output_filename = './main'

compiler = 'make'
compiler_args = ['clean', 'inject', 'main']

timeout = 3 # 3 seconds

def check_for_output_match(output, test_suite):
    """Return bool list with a True item for each output matching expected output.
       Return None if the functions suspects user tried to print something when
       they should not have."""
    output_lines = output.splitlines()
    if len(output_lines) != len(test_suite):
        return None # number of outputs != number of test cases
    
    result = list()
    for exe_output, test_case in zip(output_lines, test_suite):
        # check if exe_output has format "RESULT: <integer>"
        prefix = "RESULT: "
        if (not exe_output.startswith(prefix)):
            return None # the user printed something
        exe_value = exe_output[len(prefix):]
        try:
            int(exe_value)
        except ValueError:
            return None # the user printed something
        
        int(exe_value)
        if (test_case['output'] == exe_value):
            result.append(True)
        else:
            result.append(False)
    return result

    
def get_test_suite_input_for_stdin(test_suite):
    """Return test_suite in a format expected by main.c as stdin input.
    

   test_suite is in the same format as returned by get_test_suite(). Note this ignores the
    output key from test_suite.
    """
    alist = [string for test_case in test_suite for string in test_case['input']]
    return '\n'.join(alist) + '\n' # add newlines between each char and at end too

# def get_test_suite():
#     MAX = 2**31 - 1 # INT32_MAX, max value for a and p
#     sqrt_MAX = floor(sqrt(MAX)) # max for n
#     
#     a_list = [1, 2, 3, 4, 0]
#     p_list = [5, 3, 3, 3, 0]
#     n_list = [7, 2, 2, 1, 3]
#     
#     yield get_one_suite(a_list, p_list, n_list, MAX, sqrt_MAX)
        
def get_test_suite():
    """Yield test suite as a list of dict (with keys 'input' and 'output').

    
    Calling it again will yield the next set of test cases (test suite).
    
    The 'input' key maps to a list of strings which form the input of one test case and
    the 'output' maps to the expected answer. All values are strings.
    
    Example of how it may look like (not necessarily for this challenge):
    [{'input': ['quickbrownfox?', '14', ','], 'output': '-1'},
    {'input': ['fellow;a3', '8', '3'], 'output': '8'}]
    """
    # max for a and p
    MAX = 2**31 - 1 # INT32_MAX, max value for a and p
    sqrt_MAX = floor(sqrt(MAX)) # max for n
    
    # first test suite
    a_list = [0, 0, 0, 1, 1, 2, 7, 2, 1, 0, 0, 3, 1, 0, 0, 0, 1]
    p_list = [5, 3, 3, 0, 0, 0, 8, 1, 1, 0, 0, 0, 0, 1, 2, 0, 1]
    n_list = [7, 2, 2, 7, 3, 3, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 1]

    suite = get_one_suite(a_list, p_list, n_list, MAX, sqrt_MAX)
    yield suite
    
    # second test suite
    a_list = [3,  5, 23, 25, 100, 200,      MAX, MAX-1,  MAX]
    p_list = [10, 5, 23, 25, 100, 200,     1000,   100,  500]
    n_list = [23, 1,  0,  7,   1, 100, sqrt_MAX,     3,   23]
    
    suite = get_one_suite(a_list, p_list, n_list, MAX, sqrt_MAX)
    yield suite

    # third test suite
    a_list = []
    p_list = []
    n_list = []

    # keep a = 0
    for _ in range(10):
        a_list.append(0)
        p_list.append(random.randint(0, 5000))
        n_list.append(random.randint(0, sqrt_MAX))
    # keep p = 0
    for _ in range(10):
        a_list.append(random.randint(0, MAX))
        p_list.append(0)
        n_list.append(random.randint(0, sqrt_MAX))
    # keep n = 0
    for _ in range(10):
        a_list.append(random.randint(0, MAX))
        p_list.append(random.randint(0, 5000))
        n_list.append(0)
    # keep a = 0 and p = 0
    for _ in range(10):
        a_list.append(0)
        p_list.append(0)
        n_list.append(random.randint(0, sqrt_MAX))
    # keep all non-zero
    for _ in range(30):
        a_list.append(random.randint(0, MAX))
        p_list.append(random.randint(0, 5000))
        n_list.append(random.randint(0, sqrt_MAX))

    suite = get_one_suite(a_list, p_list, n_list, MAX, sqrt_MAX)
    yield suite
    
                      
# utility functions
# =================
def get_correct_answer(a, p , n, MAX, sqrt_MAX):
    if (a < 0 or a > MAX) \
       or (p < 0 or p > MAX) \
       or (n < 0 or n > sqrt_MAX):
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    
    if n == 0:
        return -1

    if a == 0 and p == 0:
        return -1
    
    return pow(a, p, n) # a^p mod n
    

def get_one_suite(a_list, p_list, n_list, MAX, sqrt_MAX):
    suite = []
    for a, p, n in zip(a_list, p_list, n_list):
        suite.append(dict(input=[str(a), str(p), str(n)],
                          output=str(get_correct_answer(a, p, n, MAX, sqrt_MAX))))
    return suite

