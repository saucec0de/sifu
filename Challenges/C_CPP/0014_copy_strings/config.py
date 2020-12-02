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
    MAX_LEN = 1024

    # first test suite
    # NOTE: we need at least one test suite
    # that contains no n=0 case
    # if the n=0 hint is to work reliably.
    src_list = ["hello world", "the quick brown fox", "String No. 3", "another one", "another string", "league", "not so random text", "horse"]
    n_list = [len(src) for src in src_list[:3]]
    n_list += [len(src)-3 for src in src_list[3:6]]
    n_list += [len(src)+4 for src in src_list[6:]]
    suite = get_one_suite(n_list, src_list, MAX_LEN)
    yield suite

    # second test suite
    src_list = ["more strings", "254", "a", "3R", " ", "?"]
    n_list = [len(src) for src in src_list[:3]]
    n_list += [0 for src in src_list[3:]]
    suite = get_one_suite(n_list, src_list, MAX_LEN)
    yield suite

    # third test suite
    src_list = []
    n_list = []
    for _ in range(100):
        size = random.randint(1, 100)
        src = get_random_string(size)
        src_list.append(src)
        n_list.append(size)
        size = random.randint(101, 200)
        src = get_random_string(size)
        src_list.append(src)
        n_list.append(size)
    # set about 30 to 40 numbers in n_list to 0
    set_to_0_indices = random.sample(range(len(n_list)), random.randint(30, 40))
    for i in set_to_0_indices:
        n_list[i] = 0
    suite = get_one_suite(n_list, src_list, MAX_LEN)
    yield suite


# utility functions
# =================
def get_correct_answer(n, src, MAX_LEN):
    if n < 0:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    if len(src) == 0:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    if len(src) > MAX_LEN:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")

    if n == 0:
        return ""
    elif len(src) < n-1:
        return src
    else:
        return src[:n - 1]
    

def get_one_suite(n_list, src_list, MAX_LEN):
    if len(n_list) != len(src_list):
        raise Exception("CONFIG TEST SUITE ERROR: incorrect test case values")

    suite = []
    for n, src in zip(n_list, src_list):
        suite.append(dict(input=[str(n), src],
                          output=get_correct_answer(n, src, MAX_LEN)))
    return suite


def get_random_string(size, chars=string.ascii_letters+string.digits+' '):
    if size == 0:
        return ''
    else:
        return ''.join(random.choice(chars) for _ in range(size))
