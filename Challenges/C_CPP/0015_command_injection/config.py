# HOW THIS CHALLENGE WORKS
# 1. main.c will call func.c with different input arguments as sent by checker.py.
# 2. main.c also knows the expected output and will change the value of the global
# variable accordingly to an executable that returns 0 (success) only when called
# correctly with the current input
# 3. main.c writes the return value from the function to the output file which is read
# by checker.py
# 4. checker.py tries different test cases. These include test cases which try command injection


import os
import os.path
import random
import string
import re

import util

test_function_filename = './func.c'
output_filename = './main'

compiler = 'make'
compiler_args = ['clean', 'inject', 'main']

timeout = 3 # 3 seconds

TOUCH_FILE_PREFIX = "xDANGEROUS_INJECTION_"
TOUCH_FILE_SUFFIX = ".txt"

def check_for_output_match(output, test_suite):
    """Return bool list with a True item for each output matching expected output.
    Return None if the functions suspects user tried to print something when
    they should not have.
    It can also return a string indicating the problem instead.
    
    For this challenge, it also checks if an unintended command was executed.
"""
    if was_dangerous_command_executed():
        return "dangerous_command_executed"

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
    
   test_suite is in the same format as returned by get_test_suite().
    """
    input_alist = [string for test_case in test_suite for string in test_case['input']]
    output_alist = [string for test_case in test_suite for string in test_case['output']]

    # add newlines between each char and at end too
    return '\n'.join([inp + '\n' + outp for inp, outp in zip(input_alist, output_alist)]) + '\n'


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
    COLOURS = ["red", "green", "blue"]

    # first test suite
    colours = COLOURS*2
    outputs = [0, 0, 0, 1, 1, 1]
    suite = get_one_suite(colours, outputs, MAX_LEN)
    yield suite

    # second test suite
    colours = []
    outputs = []
    for _ in range(100):
        colr = random.choice(COLOURS)
        colours.append(colr)
        outp = random.randint(0, 1)
        outputs.append(outp)
    suite = get_one_suite(colours, outputs, MAX_LEN)
    yield suite

    # third test suite
    # trying command execution
    command_chain_operators = [";", "|", "||", "&&"]
    colours = []
    outputs = []
    for colr in COLOURS:
        for opr in command_chain_operators:
            dangerous = colr + " " + opr + " " + get_touch_command()
            colours.append(dangerous)
            outputs.append(1)
    suite = get_one_suite(colours, outputs, MAX_LEN)
    yield suite

    # fourth test suite
    # more ways of command execution
    colours = []
    outputs = []
    for colr in COLOURS:
        for dangerous in [colr + " `" + get_touch_command() + "`", \
                            colr + " $(" + get_touch_command() + ")"]:
            colours.append(dangerous)
            outputs.append(1)
    suite = get_one_suite(colours, outputs, MAX_LEN)
    yield suite

    # now try large values to cause stack overflow
    colours = []
    outputs = []
    for _ in range(10):
        size = random.randint(101, 600)
        colr = get_random_string(size, chars=string.ascii_letters+string.digits)
        colours.append(colr)
        outputs.append(1)
    suite = get_one_suite(colours, outputs, MAX_LEN)
    yield suite


# utility functions
# =================
def get_one_suite(colours, outputs, MAX_LEN):
    suite = []

    if len(colours) != len(outputs):
        raise Exception("CONFIG TEST SUITE ERROR: incorrect test case values")

    for colour, output in zip(colours, outputs):
        if output not in [0, 1]:
            raise Exception("CONFIG TEST SUITE ERROR: incorrect test case values")
        if len(colour) > MAX_LEN:
            raise Exception("CONFIG TEST SUITE ERROR: incorrect test case values")
        suite.append(dict(input=[colour], output=str(output)))

    return suite

def was_dangerous_command_executed():
    files_and_dirs = os.listdir(os.curdir)
    ret = False
    for x in files_and_dirs:
         if x.startswith(TOUCH_FILE_PREFIX) and x.endswith(TOUCH_FILE_SUFFIX):
             old_name = os.path.join(os.curdir, x)
             # to keep track of files that we have found
             new_name = os.path.join(os.curdir, "xDETECTED_" + x)
             os.rename(old_name, new_name)
             ret = True
    return ret

def get_touch_command():
    return "touch " + get_touch_filename()

def get_touch_filename():
    size = random.randint(10, 20)
    return TOUCH_FILE_PREFIX + get_random_string(size, chars=string.ascii_letters) + ".txt"


def get_random_string(size, chars=string.ascii_letters+string.digits+' '):
    if size == 0:
        return ''
    else:
        return ''.join(random.choice(chars) for _ in range(size))
