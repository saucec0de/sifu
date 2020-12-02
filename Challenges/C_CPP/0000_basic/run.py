#!/usr/bin/python3
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
            # taken from: https://stackoverflow.com/questions/26385984/recursive-pattern-in-regex
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
ret    = subprocess.run(["make compile"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

# Step 2. Run in jail
ret    = subprocess.run(["make jail"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = ret.stdout.decode("utf-8")

###################################################################################################
#                                 My own tests                                                    #
###################################################################################################
addFinding("This finding is a test",True,"INCREMENTAL_2_TEST_INC_")


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
    # ERROR in line 5: Memory leak
    errorMsg = r["msg"]
    m = re.search(r"ERROR in line \d+: Memory leak",errorMsg)
    if m:
        # overwrite that with my own tag in allResults
        r["tag"] = "FUNC_NOT_FOUND"
results.saveResults(allResults)

# Perform the "ladddering techinique"
ret = subprocess.run(["make ai"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 


