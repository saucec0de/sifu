#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
#
import subprocess
import pprint as p
import results
import shutil
import regex
import sys
import re
import os

# Note: findings shall not repeat themselves, if found more than once
findings = {}

# function that adds a potential new finding to the findings database
# result=False: FAIL
# result=True:  PASS
def addFinding(finding, result=0, tag=""):
    if not(finding in findings):
        findings[finding]        = {}
        findings[finding]["tag"] = tag
        if result==False:
            findings[finding]["result"] = 0
        else:
            findings[finding]["result"] = 1

# injectFunction = """
# int inspectStack(void) {
#   char _pwd[64];
#   register int  ii  = 0;
#   register int  cnt = 0;
#   for (int ii=0; ii<21; ii++) {
#       cnt += _pwd[ii]==0?1:0;
#   }
#   printf("Nr zeros %d\\n",cnt);
# }
# """
# 
# injectFunctionCall = """
#   inspectStack();
# """

def searchSource(srcFile, regx):
    nHits = 0
    try:
        with open(srcFile,"r") as f:
            lines = f.read().split("\n")
            for line in lines:
                if re.search(regx,line):
                    nHits = nHits + 1
    except:
        pass
    return nHits

def injectCodeBefore(srcFile, destFile, regx, code):
    try:
        flag = False
        with open(destFile,"w+") as w:
            with open(srcFile,"r") as f:
                lines = f.read().split("\n")
                for line in lines:
                    if re.search(regx,line):
                        w.write(code)
                        w.write(line+"\n")
                        flag = True
                    else:
                        w.write(line+"\n")
        return flag
    except:
        return False
    return False

def searchFunctionString(fString, regx):
    nHits = 0
    try:
        lines = fString.split("\n")
        for line in lines:
            if re.search(regx,line):
                nHits = nHits + 1
    except:
        pass
    return nHits

def extractFunctionFromCode(srcFile, funcRegEx):
    try:
        with open(srcFile,"r") as f:
            lines = f.read()
        m = regex.search(funcRegEx,lines)
        if m:
            cutString = lines[ m.end(): ]
            # inspired in https://stackoverflow.com/questions/26385984/recursive-pattern-in-regex
            rx = r'\n?\s*{([^{}]*+(?:(?R)[^{}]*)*+)}'
            m = regex.findall(rx,cutString,regex.DOTALL + regex.MULTILINE)
            if m:
                return m[0]
            else:
                return ""
    except:
        pass
    return ""


###################################################################################################
#                                 Code Tests Start Here                                           #
###################################################################################################

# +---------------------------------------------------------+
# | check lines of code that need to be present in the code |
# +---------------------------------------------------------+

###################
#         int   ConnectToServer    (   void    )   {
rx = "^\s*int\s+ConnectToServer\s*\(\s*void\s*\)\s*{$"
r=searchSource("func.c",rx)
finding = "ERROR: could not find the 'ConnectToServer' function declaration"
addFinding(finding,not(r==0),"FUNC_NOT_FOUND")
finding = "ERROR: found too many 'ConnectToServer' function declarations"
addFinding(finding,not(r>1))

###################
#         int   _main              (   void    )   {
rx = "^\s*int\s+_main\s*\(\s*void\s*\)\s*{$"
r=searchSource("func.c",rx)
finding = "ERROR: could not find the '_main' function declaration"
addFinding(finding,not(r==0))
finding = "ERROR: found too many '_main' function declarations"
addFinding(finding,not(r>1))


###################
#                                                 int    main    (   void    )
f_ConnectToServer = extractFunctionFromCode( "func.c", r"int\s+ConnectToServer\s*\(\s*void\s*\)\s*" )
finding = "ERROR: could not find 'ConnectToServer' function declaration"
addFinding(finding,not(f_ConnectToServer==""))
###################
#         char pwd[64]; // do not change this line
rx = "^\s*char\s+pwd\[64\];\s*// do not change this line$"
r=searchFunctionString(f_ConnectToServer,rx)
finding = "ERROR: line with pwd variable has been changed"
addFinding(finding,not(r==0))
finding = "ERROR: there are several pwd variables defined"
addFinding(finding,not(r>1))

###################
#                                                 int    main    (   void    )
f_main = extractFunctionFromCode( "func.c", "int\s+_main\s*\(\s*void\s*\)\s*" )
finding = "ERROR: could not find '_main' function declaration"
addFinding(finding,not(f_main==""))

#         return 0; // _main: do not change this line
rx = "^\s*return 0; // _main: do not change this line\s*$"
r=searchFunctionString(f_main,rx)
finding = "ERROR: could not find return from '_main' function"
addFinding(finding,not(r==0))
finding = "ERROR: found too many returns from '_main' function"
addFinding(finding,not(r>1))

# "make" will clean the project
ret = subprocess.run(["COPTS='' make"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

# Add the results to unit_test.json
r = results.loadResults()
for finding in findings:
    tag = findings[finding]["tag"]
    res = findings[finding]["result"]
    r   = results.addResult(r,res,"TEST_90",finding,"","",tag)
results.saveResults(r)

# re-run ai.py to take our results into consideration
ret = subprocess.run(["./ai.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 
