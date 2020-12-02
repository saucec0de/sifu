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

        
def get_test_suite():
    """Yield test suite as a list of dict (with keys 'input' and 'output').

    
    Calling it again will yield the next set of test cases (test suite).
    
    The 'input' key maps to a list of strings which form the input of one test case and
    the 'output' maps to the expected answer. All values are strings.
    
    Example of how it may look like:
    [{'input': ['quickbrownfox?', '14', ','], 'output': '-1'},
    {'input': ['fellow;a3', '8', '3'], 'output': '8'}]
    """
    # first test suite
    suite = []
    strings = ['hi, how are you?',
               'the quick brown fox',
               'friends',
               '3.a.z.@#23j adksf',
               '',
               '   ',
               'abckd3rfji2kcdi3',
               'Ujfak3ja9scmaX']
    chars = ['h', ' ', 's', '3', 'y', '.', 'x', 'U']

    for s, c in zip(strings, chars):
        suite.append(dict(input=[s, str(len(s)), c],
                          output=str(s.rfind(c))))
    yield suite

    # second test suite
    suite = []
    for length in range(1, 101, 10):
        # be careful of using string.printable since that also includes newline
        s = get_random_string(length) # input string
        
         # pick char from input string 50% of the time.
         # pick from the entire printable character set the other 50% of the time.
        if (random.randint(0, 1)):
            c = random.choice(s)
        else:
            c = random.choice(string.ascii_letters+string.digits+' ')
            
        output = str(s.rfind(c)) # output

        suite.append(dict(input=[s, str(length), c],
                          output=output))

    yield suite


# utility function
def get_random_string(size, chars=string.ascii_letters+string.digits+' '):
    if size == 0:
        return ''
    else:
        return ''.join(random.choice(chars) for _ in range(size))
