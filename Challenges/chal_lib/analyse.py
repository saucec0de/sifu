#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#           tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# This file implements analysis of stderr
#
import results
import json
import yaml
import sys
import re

injectFileName = "inject.yaml"

def call_analyse(identifier = None, fname = "func"):
    # Note: findings shall not repeat themselves, if found more than once
    findings = {}

    # function that adds a potential new finding to the findings database
    def addFinding(finding, tag=""):
        if not(finding in findings):
            findings[finding] = tag

    def loadYamlFile(inFile):
        _inDict = {}
        try:
            with open(inFile) as f:
                _inDict = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            #print("WARNING: "+str(e))
            pass
        return _inDict

    nLinesInjected = {}
    I = loadYamlFile(injectFileName)
    for fName in I:
        nLinesInjected[fName] = len(I[fName])

    chalConfig = loadYamlFile("config.yaml")
    ##########################################################################
    #                                 Main                                   #
    ##########################################################################
    #fNameR = r"func(?:_\d+)?\.cp?p?"
    challengeFiles = chalConfig["files"]
    if type(challengeFiles) is str:
        challengeFiles = [challengeFiles]
    for fname in challengeFiles:
        # NOTE: we need to split this for loop - it is now very big...!
        fNameR = fname
        # +------------------------------------------+
        # |        Process compilaton errors         |
        # +------------------------------------------+
        print("Search file:", fNameR)
        try:
            with open("compile.txt") as f:
                errLines = f.read().split("\n")
            lineNum = 0
            while (lineNum<len(errLines)):
                errLine = errLines[lineNum]
                if re.search("redirected_",errLine): errLine = re.sub("redirected_","",errLine)
                # search for messages related only to the user file

                # Errors that can be bypassed
                if re.match(r"^collect2: error: ld returned 1 exit status$",errLine):
                        finding    = "Linking failed!"
                        addFinding(finding)
                #if re.search(r"\.o: No such file or directory$",errLine):
                #        finding    = "File or directory missing!"
                #        addFinding(finding)

                # deal with redirected funtions
                # redirect.h:17:14: error: too few arguments to function ‘redirected_time’
                m = re.match(r"^"+fNameR+r":(\d+):(\d+): error: (.*)",errLine)
                if m:
                    lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                    colNumber  = int(m.group(2))
                    errMsg     = m.group(3)
                    m          = re.search("redirected_",errMsg)
                    if m:
                        errMsg = re.sub("redirected_","",errMsg)
                        # continue searching for the line number
                        # func_7453459449.c:21:19: note: in expansion of macro ‘time’
                        while (lineNum<len(errLines)):
                            errLine = errLines[lineNum]
                            lineNum = lineNum + 1
                            m = re.search(fNameR+ r":(\d+):(\d+): note: in expansion of macro (.*)",errLine)
                            if m:
                                lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                                finding    = "ERROR ({fileName},{lineNumber}): {errMsg}".format(fileName=fNameR,lineNumber=lineNumber,errMsg=errMsg)
                                addFinding(finding)
                                break

                #
                # TODO: capture name of file and compare to our files that we are searching for...
                #       if not in our dictionary, then this is a "Yikes" error
                #
                #### # Compiler error in a file not func*
                #### # This needs to be improved here...
                #### m = re.match(r"^((?!" + fNameR + r")).*error:.*",errLine)
                #### if m:
                ####     print("Yikes: ("+str(m.groups()))+")",errLine)
                ####     finding    = "ERROR in project! Help, Hurry ... call someone!?!?! Yikes!"
                ####     addFinding(finding)

                # Compiler error in func.c or func.cpp - Type 1 (line number + column number)
                # func.c:12:5: error: implicit declaration of function ‘xstrcpy’; did you mean ‘strcpy’? [-Werror=implicit-function-declaration]
                m = re.search(fNameR+ r":(\d+):(\d+): error: (.*)",errLine)
                if m:
                    lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                    colnNumber = int(m.group(2))
                    errorMsg   = m.group(3)
                    finding    = "ERROR ({fileName},{lineNumber}): {errMsg}".format(fileName=fNameR,lineNumber=lineNumber,errMsg=errorMsg)
                    addFinding(finding)

                # Compiler error in func.c or func.cpp - Type 2 (only line number)
                m = re.search(fNameR+ r":(\d+): error: (.*)",errLine)
                if m:
                    #print("BBB",errLine)
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colnNumber = int(m.group(2))
                        errorMsg   = m.group(3)
                        finding    = "ERROR ({fileName},{lineNumber}): {errMsg}".format(fileName=fNameR,lineNumber=lineNumber,errMsg=errorMsg)
                        addFinding(finding)

                # Compiler error in func.c or func.cpp - Type 3 (fatal error + line number + column number)
                m = re.search( fNameR + r":(\d+):(\d+): fatal error: (.*)",errLine)
                if m:
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colnNumber = int(m.group(2))
                        errorMsg   = m.group(3)
                        finding    = "ERROR ({fileName},{lineNumber}): {errMsg}".format(fileName=fNameR,lineNumber=lineNumber,errMsg=errorMsg)
                        addFinding(finding)

                # Usage of deprecated functions
                m = re.search( fNameR+ r":(\d+):(\d+): warning: ‘(.*)’ * is deprecated \[-Wdeprecated-declarations\]", errLine)
                if m:
                    lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                    colnNumber = int(m.group(2))
                    funcName   = m.group(3)
                    finding    = "WARNING ({fileName},{lineNumber}): {errMsg}".format(fileName=fNameR,lineNumber=lineNumber,errMsg=errorMsg)
                    addFinding(finding)

                # func.c:28:9: warning: format not a string literal and no format arguments [-Wformat-security]
                if 'format not a string literal and no format arguments [-Wformat-security]' in errLine:
                    # func.c:22:14: runtime error: signed integer overflow: 244140625 * 25 cannot be represented in type 'int'
                    m = re.search( fNameR + r":(\d+):(\d+):", errLine)
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colNumber  = int(m.group(2))
                        finding    = "WARNING ({fileName},{lineNumber}): A format string attack is possible".format(fileName=fNameR,lineNumber=lineNumber)
                        addFinding(finding)

                lineNum = lineNum + 1

        except Exception as e:
            print("Exception: "+str(e))

        # +------------------------------------------+
        # |       Process findings from stderr       |
        # +------------------------------------------+
        try:
            with open("stderr.txt") as f:
                errLines = f.read().split("\n")

            lineNum = 0
            found_asan = False
            added_asan_finding = False
            while (lineNum<len(errLines)):
                errLine = errLines[lineNum]
                if "runtime error: signed integer overflow" in errLine:
                    # func.c:22:14: runtime error: signed integer overflow: 244140625 * 25 cannot be represented in type 'int'
                    m = re.search(fNameR+ r":(\d+):(\d+): runtime error: signed integer overflow", errLine)
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colNumber = int(m.group(2))
                        finding = "ERROR ({fileName},{lineNumber}): There is a signed integer overflow vulnerability".format(fileName=fNameR,lineNumber=lineNumber)
                        addFinding(finding)

                if "runtime error: division by zero" in errLine:
                    # func.c:25:17: runtime error: division by zero
                    m = re.search(fNameR+ r":(\d+):(\d+): runtime error: division by zero", errLine)
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colNumber = int(m.group(2))
                        finding = "ERROR ({fileNamer},{lineNumber}): There is a division-by-zero vulnerability".format(fileName=fNameR,lineNumber=lineNumber)
                        addFinding(finding)

                
                if "runtime error: reference binding to null pointer of type" in errLine:
                    m = re.search(fNameR+ r":(\d+):(\d+): runtime error: member call on null pointer of type \.*", errLine)
                    if m:
                        lineNumber = int(m.group(1)) - nLinesInjected.get(fNameR,0)
                        colNumber = int(m.group(2))
                        finding = "ERROR ({fileName},{lineNumber}): Null pointer access".format(fileName=fNameR,lineNumber=lineNumber)
                        addFinding(finding)

                # findings by AddressSanitizer and LeakSanitizer
                # ==============================================
                if re.search(r"AddressSanitizer: ",errLine):
                    found_asan = True
                # search for AddressSanitizer: buffer overflow
                if re.search(r"AddressSanitizer: stack-buffer-overflow on address",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        m = re.search(r"'(.*?)'.*<== Memory access at offset \d+ overflows this variable",errLine)
                        if m:
                            varName = m.group(1)
                            finding = "Stack overflow on variable '{varName}'".format(varName=varName)
                            addFinding(finding)
                            added_asan_finding = True
                            break
                        m = re.search(r"'(.*?)'.*<== Memory access at offset \d+ underflows this variable",errLine)
                        if m:
                            varName = m.group(1)
                            finding = "Stack underflow on variable '{varName}'".format(varName=varName)
                            addFinding(finding)
                            added_asan_finding = True
                            break

                        lineNum = lineNum + 1
                # search for AddressSanitizer: buffer overflow
                elif re.search(r"^\*\*\* stack smashing detected \*\*\*",errLine):
                    finding = "Possible stack smashing was detected"
                    addFinding(finding)
                # Example: ==4==ERROR: AddressSanitizer: SEGV on unknown address 0x5566f04f9933 (pc 0x5566f04db4d6 bp 0x7ffe1f0c2eb0 sp 0x7ffe1f0c2df0 T0)
                elif re.search(r"^==\d+==ERROR: AddressSanitizer: SEGV on unknown address",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        # #0 0x557a3f99c4d5 in func /home/gasiba/Git/sifu/upload/edbd33d4-6ece-4cec-9da9-4b66084db79e/func.c:13
                        m = re.search(r"^.*in (.*) .*\/" + fNameR + r":(.*?)$",errLine)
                        if m:
                            functionName = m.group(1)
                            lineNumber = int(m.group(2)) - nLinesInjected.get(fNameR,0)
                            finding = "ERROR ({fileName},{lineNumber}): Segmentation fault".format(fileName=fNameR,lineNumber=lineNumber)
                            addFinding(finding)
                            added_asan_finding = True
                            break
                        lineNum = lineNum + 1
                # search for AddressSanitizer: heap-buffer-overflow
                # Example: ==2==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000015 at pc 0x55b9ad0e93fd bp 0x7ffce65329b0 sp 0x7ffce65329a0
                elif re.search(r"^==\d+==ERROR: AddressSanitizer: heap-buffer-overflow",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        # #0 0x55b9ad0e93fc in func /home/gasiba/Git/sifu/upload/51b30a8b-acde-4bf3-8c64-8d2f88fd932c/func.c:14
                        m = re.search(r"^in (.*) .*\/" + fNameR + r".cp?p?:(.*?)$",errLine)
                        if m:
                            functionName = m.group(1)
                            lineNumber = int(m.group(2)) - nLinesInjected.get(fNameR,0)
                            finding = "ERROR ({fileName},{lineNumber}): Heap Buffer Overflow/Underflow".format(fileName=fNameR,lineNumber=lineNumber)
                            addFinding(finding)
                            added_asan_finding = True
                            break
                        lineNum = lineNum + 1
                # search for memory leaks
                # Example: ==2==ERROR: LeakSanitizer: detected memory leaks
                elif re.search(r"==\d+==ERROR: LeakSanitizer: detected memory leaks",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        # #1 0x5602ed79db34 in get_filled_buffer /home/gasiba/Git/sifu/Challenges/test/chal_0007/func.c:25
                        m = re.search(r"^.*in (.*) .*\/"+fNameR+":(.*?)$",errLine)
                        if m:
                            functionName = m.group(1)
                            lineNumber = int(m.group(2)) - nLinesInjected.get(fNameR,0)
                            finding = "ERROR ({fileName},{lineNumber}): Memory leak".format(fileName=fNameR,lineNumber=lineNumber)
                            addFinding(finding)
                            break
                        # SUMMARY: AddressSanitizer: 120 byte(s) leaked in 1 allocation(s).
                        m = re.search(r"SUMMARY: AddressSanitizer: \d+ byte\(s\) leaked in \d+ allocation\(s\).$",errLine)
                        if m:
                            addFinding("Detected memory leak")
                            break
                        lineNum = lineNum + 1
                # search for free memory that was not malloc'ed
                # Example: AddressSanitizer: attempting free on address which was not malloc()-ed: 0x7ffffa10fcd0 in thread T0
                #          #0 0x560d6e9f491f in __interceptor_free (/home/gasiba/Git/sifu/Challenges/test/chal_0007/main+0x10591f)
                #          #1 0x560d6ea42783 in get_y_no /home/gasiba/Git/sifu/Challenges/test/chal_0007/func.c:17
                #          #2 0x560d6ea4191b in Test_Main /home/gasiba/Git/sifu/Challenges/test/chal_0007/main.c:49
                #          #3 0x560d6ea41ae1 in main /home/gasiba/Git/sifu/Challenges/test/chal_0007/main.c:73
                #          #4 0x7fe368b1cb96 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21b96)
                #          #5 0x560d6e90b449 in _start (/home/gasiba/Git/sifu/Challenges/test/chal_0007/main+0x1c449)
                elif re.search(r"AddressSanitizer: attempting free on address which was not malloc",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        # #1 0x560d6ea42783 in get_y_no /home/gasiba/Git/sifu/Challenges/test/chal_0007/func.c:17
                        m = re.search(r"^.*in (.*) .*\/"+fNameR+":(.*?)$",errLine)
                        if m:
                            functionName = m.group(1)
                            lineNumber = int(m.group(2)) - nLinesInjected.get(fNameR,0)
                            finding = "ERROR ({fileName},{lineNumber}): Trying to free memory that was not malloc'ed".format(fileName=fNameR,lineNumber=lineNumber)
                            addFinding(finding)
                            added_asan_finding = True
                            break
                        lineNum = lineNum + 1
                # ==2==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000000 (pc 0x55daab485ac3 bp 0x7ffd89bea910 sp 0x7ffd89bea860 T0)
                # ==2==The signal is caused by a READ memory access.
                # ==2==Hint: address points to the zero page.
                #     #0 0x55daab485ac2 in get_y_no /home/gasiba/Git/sifu/upload/a4438855-2f36-4c53-9e1f-52e6a46f3b24/func.c:36
                #     #1 0x55daab484b9e in Test_Main /home/gasiba/Git/sifu/upload/a4438855-2f36-4c53-9e1f-52e6a46f3b24/main.c:49
                #     #2 0x55daab484d96 in main /home/gasiba/Git/sifu/upload/a4438855-2f36-4c53-9e1f-52e6a46f3b24/main.c:74
                #     #3 0x7f60b21b6b96 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21b96)
                #     #4 0x55daab34e6c9 in _start (/chal/main+0x1c6c9)
                elif re.search(r"AddressSanitizer: SEGV on unknown address",errLine):
                    lineNum = lineNum + 1
                    while (lineNum<len(errLines)):
                        errLine = errLines[lineNum]
                        # #0 0x55daab485ac2 in get_y_no /home/gasiba/Git/sifu/upload/a4438855-2f36-4c53-9e1f-52e6a46f3b24/func.c:36
                        m = re.search(r"^.*in (.*) .*\/"+fNameR+":(.*?)$",errLine)
                        if m:
                            functionName = m.group(1)
                            lineNumber = int(m.group(2)) - nLinesInjected.get(fNameR,0)
                            finding = "ERROR ({fileName},{lineNumber}): segmentation fault".format(fileName=fNameR,lineNumber=lineNumber)
                            addFinding(finding)
                            added_asan_finding = True
                            break
                        lineNum = lineNum + 1
                lineNum = lineNum + 1
            if found_asan and not added_asan_finding:
                addFinding("There is a security vulnerability with your code.")
                #TODO: report to ourselves

        except Exception as e:
            print("Exception: "+str(e))

    # Dump the results to the Sifu backend
    r = results.loadResults()
    for finding in findings:
        tag = findings[finding]
        r   = results.addResult(r,0,"TEST_100",finding,"","",tag, identifier)

    # in the end, if we have no results, something wrong or very bad has happen!
    if len(r)==0:
        r = results.addResult(r,0,"TEST_0","This challenge seems to be broken!","","","NO_TAG")

    results.saveResults(r)

    # Done.

if __name__ == '__main__':
    call_analyse()
    
    


