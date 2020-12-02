#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import random
import string
import re

import util

test_function_filename = './func.c'
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


def get_test_suite():
    """Yield test suite as a list of dict (with keys 'input' and 'output').

    
    Calling it again will yield the next set of test cases (test suite).
    
    The 'input' key maps to a list of strings which form the input of one test case and
    the 'output' maps to the expected answer. All values are strings.
    
    Example of how it may look like (not necessarily for this challenge):
    [{'input': ['quickbrownfox?', '14', ','], 'output': '-1'},
    {'input': ['fellow;a3', '8', '3'], 'output': '8'}]
    """
    # TODO portably find UINT_MAX
    UINT_MAX = 2**32 - 1
    MAX_LEN = 1000

    # first test suite
    arr_list = \
               [
                   [1, 2, 3, 4, 5],
                   [0, 1, 2]
               ]

    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite
    
    # second test suite
    arr_list = \
             [
                 [0],
                 [1],
                 [UINT_MAX],
                 [UINT_MAX-1],
                 [UINT_MAX//2],
                 [0]*2,
                 [1]*2,
                 [UINT_MAX]*2,
                 [UINT_MAX-1]*2,
                 [UINT_MAX//2]*2,
                 [0]*5,
                 [1]*5,
                 [UINT_MAX]*5,
                 [UINT_MAX-1]*5,
                 [UINT_MAX//2]*5,
             ]
    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite

    # third test suite
    arr_list = \
             [
                 [2, 5, 1, 0],
                 [0, 0, 2, 5, 5],
                 [UINT_MAX, UINT_MAX, UINT_MAX - 1],
                 [UINT_MAX, 0, 0],
                 [UINT_MAX - 1, 0, 0],
                 [UINT_MAX - 1, 0, 0, UINT_MAX],
                 [UINT_MAX//2, UINT_MAX],
             ]
    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite

    # fourth test suite
    arr_list = []
    for _ in range(20): # 20 test cases
        temp = []
        for _ in range(30): # make array of length 30
            temp.append(random.randint(0, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite


    # fifth test suite
    arr_list = []
    for _ in range(30): # 30 test cases
        temp = []
        for _ in range(25): # make array of length 25
            temp.append(random.randint(UINT_MAX//2 + 1, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite


    # sixth test suite
    arr_list = []
    for _ in range(20): # 20 test cases
        temp = []
        for _ in range(random.randint(1, MAX_LEN)): # random array length
            temp.append(random.randint(0, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, UINT_MAX, MAX_LEN)
    yield suite
    

# utility functions
# =================
def get_correct_answer(length, arr, UINT_MAX, MAX_LEN):
    if length != len(arr):
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    if length > MAX_LEN or length <= 0:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")

    max_num = 0
    for num in arr:
        if num > UINT_MAX or num < 0:
            raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
        if num > max_num:
            max_num = num

    return max_num
    

def get_one_suite(arr_list, UINT_MAX, MAX_LEN):
    suite = []

    len_list = [len(arr) for arr in arr_list]
    for length, arr in zip(len_list, arr_list):
        suite.append(dict(input=[str(length)] + [str(num) for num in arr],
                          output=str(get_correct_answer(length, arr, UINT_MAX, MAX_LEN))))
    return suite

