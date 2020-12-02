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
def addFinding(finding, result=0, tag="", tc="TEST_100"):
    if not(finding in findings):
        findings[finding]        = {}
        findings[finding]["tag"] = tag
        findings[finding]["tc"]  = tc
        if result==False:
            findings[finding]["result"] = 0
        else:
            findings[finding]["result"] = 1

def searchSource(srcFile, regx):
    nHits = 0
    try:
        with open(srcFile,"r") as f:
            lines = f.read().split("\n")
            for line in lines:
                #print("LINE:",nHits, regx, line)
                if re.search(regx,line):
                    nHits = nHits + 1
    except Exception as e:
        print("ISSUE: "+str(e))
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


# Dump the results to the Sifu backend
def dumpFindings():
    r = results.loadResults()
    for finding in findings:
        tag = findings[finding]["tag"]
        res = findings[finding]["result"]
        tc  = findings[finding]["tc"]
        r   = results.addResult(r,res,tc,finding,"","",tag)
    results.saveResults(r)
