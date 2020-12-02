#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# NOTE this was tested on Python 3.6.9
# NOTE subprocess seems to return empty stdout when ASan reports an error

import sys
import os
import os.path
import signal
import subprocess
import uuid
import re
from pprint import pprint as pp

import util
import results
import config

def check():
    """Check security issues according to config and pass results to next tools."""
    
    overall_report = dict()

    # source code analysis
    # ====================
    # currently empty
    
    # compile
    # =======
    ret_makefile = subprocess.run([config.compiler] + config.compiler_args, # command
                                  stdout=subprocess.PIPE, # capture stdout
                                  stderr=subprocess.PIPE, # capture stderr
                                  universal_newlines=True) # use text mode for std* file objects
    overall_report['makefile'] = ret_makefile
    
    # runtime analysis
    # ================
    with open('compile.txt', 'r') as f:
        if 'error' not in f.read().lower(): # if compilation succeeded
            overall_report, test_case_report_list = runtime_analysis(config, overall_report)
            
    # pass this info to next tools for subsequent processing
    # ======================================================
    pp(overall_report)
    # results from runtime analysis
    if 'runtime_analysis_done' in overall_report:
        success_count = 0
        for report in test_case_report_list:
            if 'timeout' in report:
                util.addFinding("Time limit exceeded!", 0, "", "TEST_080006")
            elif report['return_code'] != 0:
                if report['stderr_stream'] != '': # ASan/LeakSan/Stack protector probably reported something
                    pass # but these findings will be added by analyze.py
                else:
                    util.addFinding("It seems your program might have crashed.", 0,"","TEST_100006")
            # output_match == None means the user might have tried to print to outfile
            elif report['stdout_stream'] != '' or report['output_match'] is None:
                util.addFinding("A test case failed! Make sure you are not trying to print something.",
                                0,"","TEST_100006")
            elif isinstance(report['output_match'], str):
                if report['output_match'] == 'dangerous_command_executed':
                    util.addFinding("The code has a dangerous vulnerability.", 0, "INCREMENTAL_4_COMMAND_INJECTION__VULNERABILITY_", "TEST_100004")
            elif not all(report['output_match']): # not all test cases passed
                util.addFinding("A test case failed!", 0, "", "TEST_100006")
            else:
                success_count += 1

            with open('stderr.txt', 'a') as f:
                f.write(report['stderr_stream'])
            with open('stdout.txt', 'a') as f:
                f.write(report['outfile'])

        if success_count == len(test_case_report_list):
            util.addFinding("Program behaves as expected!", 1, "CHALLENGE_PASS", "TEST_900006")
            
    util.dumpFindings()
        
    # next tools
    subprocess.run(["./analyse.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["./ai.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    
    
def runtime_analysis(config, overall_report):
    """Run test suites on executable and return a list containing the result of each test suite.

    Each list item is a dictionary describing the result of running that test suite.
    """
    test_case_report_list = []
    
    for test_suite in config.get_test_suite():
        report = dict()
        report['stdout_stream'] = ''
        report['stderr_stream'] = ''
        report['outfile'] = ''

        input_for_stdin = config.get_test_suite_input_for_stdin(test_suite)
        # using Popen instead of run because I need access to the pid
        # See comment under "except subprocess.TimeoutExpired:"
        infile = "xinfile_" + uuid.uuid4().hex[0:16] + ".txt"
        outfile = "xoutfile_" + uuid.uuid4().hex[0:16] + ".txt"
        p = subprocess.Popen(['./run_jail.sh',
                              config.output_filename,
                              str(len(test_suite)), infile, outfile], # command
                             stdout=subprocess.PIPE, # capture stdout
                             stderr=subprocess.PIPE, # capture stderr
                             stdin=subprocess.PIPE, # capture stdin
                             universal_newlines=True, # use text mode for std* file objects
                             start_new_session=True, # otherwise killing the process group will also kill the Python interpreter
        )

        try:
            # send test suite input
            with open(infile, "w") as f:
                f.write(input_for_stdin)
            (stdout_stream, stderr_stream) = p.communicate(timeout=config.timeout)
            
            report['return_code'] = p.returncode
            report['stderr_stream'] += stderr_stream
            report['stdout_stream'] += stdout_stream
            with open(outfile, "r") as f:
                current_outfile = f.read()
                report['outfile'] += current_outfile
                
            # check if test cases passed
            ret_output_match = config.check_for_output_match(current_outfile, test_suite)
            report['test_suite'] = test_suite
            report['output_match'] = ret_output_match
            
        except subprocess.TimeoutExpired:
            # kill the process group so that all child processes spawned by the process are also killed
            # The child need to be killed because, in addition to wasting CPU cycles,
            # it can hold stdout and then Python will wait indefinitely even if the timeout is expired
            os.killpg(os.getpgid(p.pid), signal.SIGKILL) 
            report['timeout'] = True
        finally:
            test_case_report_list.append(report)
        
    overall_report['runtime_analysis_done'] = True

    return overall_report, test_case_report_list


if __name__ == '__main__':
    try:
        check() # run checker
    except Exception as e:
        print("EXCEPTION IN CHECKER: " + str(e))
        util.dumpFindings();
    
