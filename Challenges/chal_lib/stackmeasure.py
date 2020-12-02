#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import os
import os.path

# To generate an .su file for stack usuage analysis, you can add
# -fstack-usage
# to the gcc options while compiling
# See:
# https://gcc.gnu.org/onlinedocs/gnat_ugn/Static-Stack-Usage-Analysis.html


# NOTE
# ====
# It seems sometimes the .su files contain the full function signature
# while other times they contain just the function names.
# My guess is that function signatures appear only when compiling with g++.
#
# example output with: gcc -fstack-usage test.c -o main.out
# test.su contents
# ----------------
# test.c:5:5:func	16	static
# test.c:10:5:main	16	static
#
# example output with: g++ -fstack-usage cpptest.cpp -o cppmain.out
# cpptest.su contents
# -------------------
# cpptest.cpp:4:5:int mycppfunc(int)	16	static
# cpptest.cpp:13:9:int Cat::getx()	16	static
# cpptest.cpp:18:5:int main()	32	static
# cpptest.cpp:24:1:void __static_initialization_and_destruction_0(int, int)	32	static
# cpptest.cpp:24:1:cpp)	16	static

def get_function_stack_usage(function_sig):
    """Return list of dictionaries containing stack usage info for function_sig.

    All .su files are searched for the function_sig in the current directory 
    
    Example call: 
    ret = get_function_stack_usage('int func(int)')
    possible return vaue:
    [{'size': 16, 'type': 'static', 'filename': 'test2.c', 'row': 1, 'col': 12},
     {'size': 16, 'type': 'static', 'filename': 'test.c', 'row': 5, 'col': 5}]

    Another example call:
    ret = get_function_stack_usage('int Cat::getx()')
    possible return value:
    [{'size': 16, 'type': 'static', 'filename': 'cpptest.cpp', 'row': 13, 'col': 9}]


    Parameters:
    function_sig: the signature of the function like 'int func(int)'.
    Note: always pass the signature of the function. This function
    takes care of the case where -fstack-usage outputs .su files without
    function signatures

    Return value:
    Each dictionary in the returned list has the following keys:
    size, type, filename, row, col,
    A list is returned because there could be multiple function definitions.
    """
    su_entries = parse_su_files()

    return_list = []
    for entry in su_entries:
        # example entry:
        # ['test.c:3:5:func', '432', 'static']
        # another example entry:
        # ['test.cpp:14:13:int Cat::getx()', '16', 'static'],
        d = dict()
        name_list = entry[0].split(':', maxsplit=3)
        d['size'] = int(entry[1])
        d['type'] = entry[2]
        d['filename'] = name_list[0]
        d['row'] = int(name_list[1])
        d['col'] = int(name_list[2])

        # since it is possible for there to be no signature:
        # ['test.c:3:5:func', '432', 'static']
        # and also a signature:
        # ['test.cpp:14:13:int Cat::getx()', '16', 'static'],
        # we handle both cases
        entry_function_name = name_list[3]
        entry_function_name_list = entry_function_name.split()
        if len(entry_function_name_list) == 1:
            # example entry_function_name: 'func'

            # function_sig might look like
            # 'int func(char, int)'
            # from this we extract
            # 'func'
            function_name = function_sig.split()[1].rpartition('(')[0]
            if entry_function_name == function_name:
                return_list.append(d)
        else:
            # example entry_function_name: 'int Cat::getx()'

            # in this case we can directly compare with function_sig
            if entry_function_name == function_sig:
                return_list.append(d)

    return return_list


def parse_su_file(su_filepath):
    """Return a list representation of the .su file.

    Assumes current directory by default.

    Example:
        parse_su_file('test.su')
    Possible return value:
        [['test.c:3:5:func', '432', 'static'],
         ['test.c:9:5:main', '16', 'static']]

    Another example (for file "test.cpp"):
        parse_su_file('test.su')
    Possible return value:
    [['test.cpp:5:5:int func()', '16', 'static'],
     ['test.cpp:14:13:int Cat::getx()', '16', 'static'],
     ['test.cpp:20:5:int main()', '32', 'static']]
    """
    alist = []
    with open(su_filepath) as f:
        for line in f:
            alist.append(line.strip('\n').split('\t'))

    return alist


def parse_su_files():
    """Return list representation of all .su files in current directory.

    Example return value:
    [['test2.c:1:12:func', '16', 'static'],
     ['test2.c:5:5:anotherfunc', '16', 'static'],
     ['test.c:5:5:func', '16', 'static'],
     ['test.c:10:5:main', '16', 'static']]
    
    See parse_su_file() for more details.
    """
    # files in current directory
    files = [f for f in os.listdir(os.curdir) if os.path.isfile(f)]
    # .su files in current directory
    su_files = [f for f in files if os.path.splitext(f)[1] == '.su']

    alist = []
    for su_file in su_files:
        alist += parse_su_file(os.path.join(os.curdir, su_file))

    return alist
