#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# How sending test cases to main works for this challenge:
# we call main like this:
# ./main 1 infile.txt outfile.txt
# infile.txt will contain something like

# <number>\n
# <string of bytes>

# for example:

# 124
# jaljlsjd&*#@JDA
# alfjdadfkaj
# lajfdl'adf'adfj2!#$aldk23

# main will first redirect the stdin stream to read from infile.txt
# main will then read the first number from stdin (i.e. infile.txt)
# and store it (say in variable count)
# then it will call the test function (the one in func.c) count times.
# each time the test function is called, the return value is written to outfile.txt

# note: so the contents of infile.txt will always start with a number followed by a newline
# afterwards, we can have any number of bytes in the file
# the first number can be smaller, larger or equal to the number of bytes after the first line


import random
import string
import re

import util

test_function_filename = './func.c'
output_filename = './main'

compiler = 'make'
# compiler_args = ['COMPILER=clang', 'clean', 'main']
compiler_args = ['clean', 'inject', 'main']

timeout = 3 # 3 seconds

def check_for_output_match(output, test_suite):
    """Return bool list with a True item for each output matching expected output.
       Return None if the functions suspects user tried to print something when
       they should not have."""

    # requirement for this challenge
    if len(test_suite) != 1:
        raise Exception('ERROR IN TEST SUITE. Number of test cases not equal to 1')
    test_case = test_suite[0]

    correct_outputs = test_case['output'].splitlines()
    exe_outputs = output.splitlines()

    if len(exe_outputs) != len(correct_outputs):
        return None # the user printed something

    for exe_output, correct_output in zip(exe_outputs, correct_outputs):
        # check if exe_output has format "RESULT: <integer>"
        prefix = "RESULT: "
        if (not exe_output.startswith(prefix)):
            return None # the user printed something
        exe_value = exe_output[len(prefix):]
        try:
            int(exe_value)
        except ValueError:
            return None # the user printed something
        
        if (correct_output != exe_value):
            return [False]

    return [True]

    
def get_test_suite_input_for_stdin(test_suite):
    """Return test_suite in a format expected by main.c as stdin input.
    

   test_suite is in the same format as returned by get_test_suite(). Note this ignores the
    output key from test_suite.
    """
    # requirement for this challenge
    if len(test_suite) != 1:
        raise Exception('ERROR IN TEST SUITE. Number of test cases not equal to 1')
    test_case = test_suite[0]

    # get number/count as string and convert it to bytes
    count = bytes(test_case['input'][0], 'ascii')
    block_of_bytes = test_case['input'][1]
    return count + b'\n' + block_of_bytes


def get_test_suite():
    """Yield test suite as a list of dict (with keys 'input' and 'output').

    
    Calling it again will yield the next set of test cases (test suite).
    
    The 'input' key maps to a list of strings which form the input of one test case and
    the 'output' maps to the expected answer. All values are strings.
    
    Example of how it may look like (not necessarily for this challenge):
    [{'input': ['quickbrownfox?', '14', ','], 'output': '-1'},
    {'input': ['fellow;a3', '8', '3'], 'output': '8'}]
    """
    MAX_COUNT = 3000
    EOF = -1

    count = 23
    block_of_bytes = b'hi, how are\nyou?'
    suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
    yield suite

    count = 300
    block_of_bytes = bytes([n for n in range(256)])
    suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
    yield suite

    for count in [1, 2, 10]:
        block_of_bytes = b''
        suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
        yield suite

    # count = 1
    # for i in list(range(0, 30)) + list(range(70, 75)) + list(range(100, 104)) \
    #     + list(range(251, 255)):
    #     block_of_bytes = bytes([i])
    #     suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
    #     yield suite

    for count in [2, 3, 127, 128, 129, 254, 255, 256, 260]:
        alist = [n for n in range(256)]
        random.shuffle(alist)
        block_of_bytes = bytes(alist)
        suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
        yield suite

    for count in [2, 5, 127, 255, 300, 1000, 2000]:
        alist = [n for n in range(256)]*3
        random.shuffle(alist)
        block_of_bytes = bytes(alist)
        suite = get_one_suite(count, block_of_bytes, MAX_COUNT, EOF)
        yield suite


# utility functions
# =================
def get_correct_answer(count, block_of_bytes, MAX_COUNT, EOF):
    if count < 1 or count > MAX_COUNT:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")

    output_list = []
    for i in range(count):
        if i >= len(block_of_bytes):
            output_list.append(EOF)
        elif ord(b'a') <= block_of_bytes[i] <= ord(b'z') \
             or ord(b'A') <= block_of_bytes[i] <= ord(b'Z'):
                output_list.append(1)
        else:
            output_list.append(0)


    return '\n'.join([str(e) for e in output_list])
    

def get_one_suite(count, block_of_bytes, MAX_COUNT, EOF):
    suite = []

    suite.append(dict(input=[str(count), block_of_bytes],
                      output=get_correct_answer(count, block_of_bytes, MAX_COUNT, EOF)))
    return suite

