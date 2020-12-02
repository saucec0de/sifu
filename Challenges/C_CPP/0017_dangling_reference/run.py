#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
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


#Check if the srcFile still has the required interface
def check_interface(reqx, srcFile, msg, tag = "FUNC_NOT_FOUND"):
    r = {}
    r['tc'] = 'TEST_30'
    r['tag'] = tag
    r['result'] = "FAIL"
    rx = "^\s*void\s+empty\s*\(\s*\)\s*;?$"
    found=searchSource(srcFile,reqx)
    r['msg'] = msg
    if found == 0:
        allResults.append(r)

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
# Step 1. Compile the project
#         Note: this step will "make clean"
ret    = subprocess.run(["make clean"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 
ret    = subprocess.run(["make inject"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 
ret    = subprocess.run(["make main"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

# Step 2. Run in jail
ret    = subprocess.run(["make jail"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

###################################################################################################
#                                 My own tests                                                    #
###################################################################################################


# Add the results to unit_test.json
allResults = results.loadResults()
for finding in findings:
    tag        = findings[finding]["tag"]
    res        = findings[finding]["result"]
    allResults = results.addResult(allResults,res,"TEST_90",finding,"","",tag)
results.saveResults(allResults)


###################################################################################################
# Run Analyse, i.e. collect results from compilation error and ASAN
#              Note: 1) analyse needs at least ONE TC that is OK or FAIL, otherwise it "thinks" that
#                       the challenge is broken!
#                    2) analyse.py will add ASAN and compiler errors to the unit_test.json
ret = subprocess.run(["make analyse"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

# re-load the results which now contain ASAN and compiler errors
allResults = results.loadResults()
for r in allResults:
    errorMsg = r["msg"]
    m = re.search(r"ERROR in line \d+: Null pointer access",errorMsg)

    if m:
        # overwrite that with my own tag in allResults
        r["tag"] = "NO_TAG"
    if "memory leak" in errorMsg:
        r["tag"] = "INCREMENTAL_2_FACTORY_COMPLEX_DEALLOCATION_"


with open("stderr.txt") as f:
    errLinesAll = f.read()
    errLines = errLinesAll.split("\n")

for line in errLines:
    r = {}

    r['tc'] = 'TEST_50'
    r['msg'] = line
    r['tag'] = 'no tag'
    r['result'] = "FAIL"
    #Get all errors for factoryCOmpelx files
    m = re.search(r"^factoryComplex\.(.*?)\:(.*?)$",line)
    if m:
        allResults.append(r)



   
    if "runtime error" in line:
        if "load of null pointer" in line:
            r['tc'] = 'TEST_80'
            r['tag'] = 'INCREMENTAL_3_FACTORY_COMPLEX_INDEX_'
            allResults.append(r)

        if "FactoryComplex::get(int)" in errLinesAll and "reference binding to null pointer of type" in line:
            
            r['tc'] = 'TEST_50'
            r['tag'] = 'INCREMENTAL_3_FACTORY_COMPLEX_INDEX_'
            allResults.append(r)

        elif "reference binding to null pointer of type" in line:
            r['tag'] = 'INCREMENTAL_3_FACTORY_COMPLEX_ALLOCATION_'
            r['msg'] = 'Error is caused by a READ memory access. Address points to the zero page.'
            allResults.append(r)


    #Cover possible AddressSanitizer errors, so that the message is customized
    #with an appropriate tag/hint if necessary
    if "AddressSanitizer: heap-buffer-overflow on address" in line:
        r['msg'] = 'Heap-buffer-overflow....'
        allResults.append(r)
    if 'AddressSanitizer: attempting double-free' in line:
        r['msg'] = 'Attempting double-free'
        r['tag'] = 'FACTORY_COMPLEX_DEALLOCATION_DOUBLE'
        allResults.append(r)
    if 'AddressSanitizer: alloc-dealloc-mismatch' in line:

        r['msg'] = "Alloc-dealloc-mismatch, allocation of a singel element and an array don't have the same deallocation expression"
        r['tag'] = 'FACTORY_COMPLEX_DEALLOCATION_MISSMATCH'
        allResults.append(r)
    if 'AddressSanitizer: heap-use-after-free' in line:
        r['msg'] = "RUNTIME ERROR: heap-use-after-free"
        r['tag'] = 'NO_TAG'
        allResults.append(r)
    

#Check if the class interface has changed, base requierements

#    void empty();
sourceFile = "factoryComplex.h"
msg = "ERROR: could not find the 'Empty' function declaration"
check_interface("^\s*void\s+empty\s*\(\s*\)\s*;?$", sourceFile,msg)

#    std::complex<int> &get(int index);
msg = "ERROR: could not find the 'Get' function declaration"
check_interface("^\s*std::complex<int>\s*&\s*get\s*\(\s*int\s+index\s*\)\s*;?$", sourceFile,msg)


#   std::complex<int> &create(int x, int y);
msg = "ERROR: could not find the 'Create' function declaration"
check_interface("^\s*std::complex<int>\s*&\s*create\s*\(\s*int\s+x\s*,\s*int\s+y\s*\)\s*;?$", sourceFile,msg)

#    std::complex<int>* complexContainer;
tag = 'NO TAG'
msg = "ERROR: could not find the complexContainer with required type!"
check_interface("^\s*std::complex<int>\s*\*\s*complexContainer\s*;\s*$", sourceFile,msg, tag)


#Save all results
results.saveResults(allResults)



# Perform the "ladddering techinique"
ret = subprocess.run(["make ai"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 


