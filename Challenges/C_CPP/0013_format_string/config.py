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

    list_of_string_lists = []
    list_of_string_lists.append(["Test", "Test", "Congratulations!", "Try again!"])
    list_of_string_lists.append(["Test", "Different", "Well done!", "Oh no!"])
    list_of_string_lists.append(["Test", "TestTest", "Good", "Sorry"])
    list_of_string_lists.append(["TestTest", "Test", "Good", "Sorry"])
    list_of_string_lists.append(["Stockholm", "Oslo", "Nice", "Sorry"])
    list_of_string_lists.append(["Oslo", "Oslo", "Nice", "Sorry"])
    list_of_string_lists.append(["Stockholm", "Stockholm", "Nice", "Sorry"])
    list_of_string_lists.append(["", "Stockholm", "Nice", "Sorry"])
    list_of_string_lists.append(["", "", "Nice", "Sorry"])
    suite = get_one_suite(list_of_string_lists, MAX_LEN)
    yield suite

    # second test suite
    list_of_string_lists = []
    for i in range(1, 60):
        user_answer = get_random_string(i)

        dice_roll = random.randint(1, 6)
        if dice_roll == 1:
            expected_answer = user_answer
        elif dice_roll == 2:
            expected_answer = user_answer
        elif dice_roll == 3:
            try:
                expected_answer = user_answer[:-2]
            except IndexError:
                expected_answer = user_answer
        elif dice_roll == 4:
            expected_answer = user_answer + get_random_string(1)
        elif dice_roll == 5:
            expected_answer = user_answer + get_random_string(2)
        elif dice_roll == 6:
            expected_answer = get_random_string(i)

        list_of_string_lists.append([user_answer,
                                     expected_answer,
                                     "Congratulations!",
                                     "Try again!"])
    suite = get_one_suite(list_of_string_lists, MAX_LEN)
    yield suite
        


# utility functions
# =================
def get_correct_answer(string_list, MAX_LEN):
    if len(string_list) != 4:
        raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")
    for string in string_list:
        if len(string) > MAX_LEN:
            raise Exception("CONFIG TEST CASE ERROR: incorrect test case values")

    if string_list[0] == string_list[1]:
        return string_list[2]
    else:
        return string_list[3]
    

def get_one_suite(list_of_string_lists, MAX_LEN):
    suite = []

    for string_list in list_of_string_lists:
        suite.append(dict(input=string_list,
                          output=get_correct_answer(string_list, MAX_LEN)))
    return suite


def get_random_string(size, chars=string.ascii_letters+string.digits+' '):
    if size == 0:
        return ''
    else:
        return ''.join(random.choice(chars) for _ in range(size))
