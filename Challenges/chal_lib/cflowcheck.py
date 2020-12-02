#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import os
import re
import subprocess


DEFAULT_ARGUMENTS = ['--omit-symbol-names', '--omit-arguments']
DEFAULT_TIMEOUT = 3


def check_if_called_by(source_files_list, parent_function_name, function_name, depth=0):
    """Return True iff parent_function_name calls function_name.
    
    By default (depth=0), it checks whether the function is called directly AND indirectly.
    Thus f calling f1 calling f2 (where f1 does not call f2 directly) will still return True.
    However, this will only happen if the definitions of f, f2 and f3 are present in
    the source_files_list.
    If, for example, the definition of f2 is not present, then it will return False
    since there is no way to know whether f2 calls f3 or not.

    Example call:
        check_if_called_by("func.c", "func", "malloc"):
    will return True iff func calls malloc
    (directly or indirectly; see depth parameter to change this)
    
    Parameters:
    source_file_list: name of source file OR list of names of source files
    parent_function_name: name of parent function/caller function
    function_name: name of function that might be called by the parent function
    depth: maximum depth to search for a call to function inside the parent function
    depth of 0 means to search entire call tree starting at parent function
    NOTE: depth of 1 will not return the parent function name only.
    So depth should always be either >= 2 or = 0
    Example:
    Inside main.c:
        main calls func (and does not call malloc directly)
    Inside func.c:
        func calls malloc
    Then:
        check_if_called_by(["main.c" "func.c"], "main", "malloc", 2):
    will return False
    but
        check_if_called_by(["main.c" "func.c"], "main", "malloc", 3):
    will return True
    """

    args_list = ['--depth='+str(depth)]
    cflow_output = run_cflow_on_function(source_files_list, parent_function_name, args_list)
    # print(cflow_output)

    # check for failure
    if not isinstance(cflow_output, str):
        return cflow_output

    search_string = "(    )+" + function_name + r"\(\)"
    match = re.search(search_string, cflow_output)
    if match:
        return True
    else:
        return False

    

# inspired in https://stackoverflow.com/questions/22549478/parsing-nested-indented-text-into-lists
def get_list_representation(cflow_output):
    """Return a list object representation of the output from cflow

    Example:
    If cflow_output is:
    main() <int () at main.c:18>:
        f() <int () at main.c:4>:
            malloc()
            printf()

    Then this function will return:
    ['main() <int () at main.c:18>:',
    ['f() <int () at main.c:4>:', ['malloc()', 'printf()']]]
    
    Parameters:
    cflow_output: string
    """
    from tokenize import NEWLINE, INDENT, DEDENT, tokenize
    import io

    stack = [[]]
    lastindent = len(stack)

    def push_new_list():
        stack[-1].append([])
        stack.append(stack[-1][-1])
        return len(stack)

    readl = io.BytesIO(cflow_output.encode('utf-8')).readline
    for t in tokenize(readl):
        if t.type == NEWLINE:
            if lastindent != len(stack):
                stack.pop()
                lastindent = push_new_list()
            stack[-1].append(t.line.strip()) # add entire line to current list
        elif t.type == INDENT:
            lastindent = push_new_list()
        elif t.type == DEDENT:
            stack.pop()
    return stack[-1]



def run_cflow_on_function(source_files_list, function_name, args_list=None):
    """Return output of running cflow on source_files_list starting at function_name

    Thus the call tree in the output will have function_name at its root.
    
    See run_cflow for more details on the parameters.
    """

    if args_list is None:
        args_list = ['--main', function_name]
    else:
        args_list = ['--main', function_name] + args_list

    return run_cflow(source_files_list, args_list)


def run_cflow(source_files_list, args_list=None, timeout=DEFAULT_TIMEOUT):
    """Return output of running cflow on source_files_list
    
    Example call:
        run_cflow("func.c")
    will return the output of running "cflow func.c"
    Another example:
        run_cflow(["main.c", "func.c"])
    will return the output of running "cflow main.c func.c"
    
    If an error occurs, a dictionary is returned containing
    the details of the error.
    Hence a successful call can be checked by
        ret = cflow("main.c")
        if isinstance(ret, str):
            print("success! cflow output: {}".format(ret))
    

    Parameters:
    source_files_list: name of source file or list of names of source files
    args_list: list of extra arguments to pass to cflow
    timeout: how many seconds to wait before killing cflow and returning
    """

    if isinstance(source_files_list, str):
        source_files_list = [source_files_list]
    if args_list is None:
        args_list = []

    command = ['cflow'] + DEFAULT_ARGUMENTS + args_list + source_files_list

    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE, # capture stdout
                         stderr=subprocess.PIPE, # capture stderr
                         stdin=subprocess.PIPE, # capture stdin
                         universal_newlines=True, # use text mode for std* file objects
                         start_new_session=True, # otherwise killing the process group will also kill the Python interpreter (we need to do this when timeout occurs)
    )

    try:
        (stdout_stream, stderr_stream) = p.communicate(timeout=timeout)

        # check for failure
        if p.returncode != 0:
            report = {}
            report['stderr_stream'] = stderr_stream
            report['stdout_stream'] = stdout_stream
            report['exit_code'] = p.returncode

    # check for failure
    except subprocess.TimeoutExpired:
        # kill the process group so that all child processes spawned by the process are also killed
        # The child needs to be killed because, in addition to wasting CPU cycles,
        # it can hold stdout and then Python will wait indefinitely even if the timeout is expired
        os.killpg(os.getpgid(p.pid), signal.SIGKILL) 
        report = {'timeout': True}
        return report

    # success!
    else: 
        return stdout_stream
