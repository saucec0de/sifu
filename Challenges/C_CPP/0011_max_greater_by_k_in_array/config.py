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
       they should not have.
    
    It can also return a string that indicates what kind of problem was there.
"""
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

    # indices of failed test cases
    false_indices = [i for i, success in enumerate(result) if not success]
    all_failed_had_single_element_array = True
    if not false_indices:
        all_failed_had_single_element_array = False
    else:
        for i in false_indices:
            tc = test_suite[i]
            length = int(tc['input'][0])
            if length != 1:
                all_failed_had_single_element_array = False
    if all_failed_had_single_element_array:
        return "all_failed_test_cases_had_single_element_array"

    # otherwise just return the list of success/fails
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

    # first BATCH of test suites
    # the number of test suites equals len([0, 1, 2, 3, 4, 7, ...., UINT_MAX])
    # (see the "for k in ..." loop for the list):
    arr_list = \
               [
                   [1, 2, 3, 4, 5],
                   [5, 4, 3, 2, 1],
                   [2, 5, 4, 0, 1],
                   [2, 3, 1, 2, 1, 0, 0, 2],

                   [1, 2, 3, 4, 6],
                   [6, 4, 3, 2, 1],
                   [2, 6, 4, 0, 1],

                   [1, 7, 3, 4, 6],
                   [6, 4, 3, 7, 1],
                   [7, 6, 4, 0, 1],

                   [0, 1, 2],
                   [2, 1, 0],
                   [0, 1, 0, 2],
                   [1, 0, 2],
               ]

    for k in [0, 1, 2, 3, 4, 7, 10, 100, \
              UINT_MAX//2, UINT_MAX//2 + 1, UINT_MAX - 2, UINT_MAX - 1, UINT_MAX]:
        k_list = [k]*len(arr_list)
        suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
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

    for k in [0, 1, 7, 10, 100, \
              UINT_MAX//2, UINT_MAX//2 + 1, UINT_MAX - 2, UINT_MAX - 1, UINT_MAX]:
        k_list = [k]*len(arr_list)
        suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
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
    for k in [0, 1, 7, 10, 100, \
              UINT_MAX//2, UINT_MAX//2 + 1, UINT_MAX - 2, UINT_MAX - 1, UINT_MAX]:
        k_list = [k]*len(arr_list)
        suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
        yield suite


    # next test suite
    arr_list = []
    k_list = []
    for _ in range(20): # 20 test cases
        k_list.append(random.randint(UINT_MAX//2 + 1, UINT_MAX))
        temp = []
        for _ in range(30): # make array of length 30
            temp.append(random.randint(0, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
    yield suite


    # next test suite
    arr_list = []
    k_list = []
    for _ in range(30): # 30 test cases
        k_list.append(random.randint(UINT_MAX//2 + 1, UINT_MAX))
        temp = []
        for _ in range(25): # make array of length 25
            temp.append(random.randint(UINT_MAX//2 + 1, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
    yield suite


    # next test suite
    arr_list = []
    k_list = []
    for _ in range(15): # 15 test cases
        k_list.append(random.randint(0, UINT_MAX))
        temp = []
        for _ in range(random.randint(1, MAX_LEN)): # random array length
            temp.append(random.randint(0, UINT_MAX))
        arr_list.append(temp)
    suite = get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN)
    yield suite
    

# utility functions
# =================
def get_correct_answer(length, arr, k, UINT_MAX, MAX_LEN):
    if length != len(arr):
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    if length > MAX_LEN or length <= 0:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    if k > UINT_MAX or k < 0:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")

    if length == 1:
        return arr[0]

    max_num = -1
    second_max_num = -1
    for num in arr:
        if num > UINT_MAX or num < 0:
            raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
        if num > max_num:
            second_max_num = max_num
            max_num = num
        elif num > second_max_num:
            second_max_num = num

    if max_num - second_max_num >= k:
        return max_num
    else:
        return 0
    

def get_one_suite(arr_list, k_list, UINT_MAX, MAX_LEN):
    suite = []

    if len(arr_list) != len(k_list):
        raise Exception("CONFIG TEST SUITE ERROR: incorrect test suite values")

    len_list = [len(arr) for arr in arr_list]
    for length, arr, k in zip(len_list, arr_list, k_list):
        suite.append(dict(input=[str(length)] + [str(num) for num in arr] + [str(k)],
                          output=str(get_correct_answer(length, arr, k, UINT_MAX, MAX_LEN))))
    return suite

