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

import pexpect as pexp
# Note: findings shall not repeat themselves, if found more than once
findings = {}

# function that adds a potential new finding to the findings database
# result=False: FAIL
# result=True:  PASS
def addFinding(finding, result=0, tag="", tc="TEST_100"):
    if type(result)==type(1):
        r = 0 if result==0 else 1;
    elif type(result)==type(True):
        r = 0 if result==False else 1;
    else:
        print("ERROR ERROR ERROR ERROR ERROR ERROR")
        print("ERROR ERROR ERROR ERROR ERROR ERROR")
        print("ERROR ERROR ERROR ERROR ERROR ERROR")
        sys.exit(0)
    flag1 = not(finding in findings)
    flag2 = False
    if not(flag1): flag2 = (r==0)

    if flag1:
        findings[finding]           = {}
        findings[finding]["tag"]    = tag
        findings[finding]["tc"]     = tc
        findings[finding]["result"] = r
    if flag2:
        try:
            lastTC = findings[finding]["tc"]
            lastR  = findings[finding]["result"]
            m = re.match(".*_(.*)",lastTC)  # FIXME: is this a good way to extract the priority?
            lastPrio = int(m.group(1))
            m = re.match(".*_(.*)",tc)      # FIXME: is this a good way to extract the priority?
            newPrio = int(m.group(1))
            if (newPrio<lastPrio) or (lastR==1):  # update if changing to FAIL or if prio is higher (lower value)
                # replace current finding, since its prio is higher
                findings[finding]           = {}
                findings[finding]["tag"]    = tag
                findings[finding]["tc"]     = tc
                findings[finding]["result"] = r
        except Exception as e:
            print("ERROR: could not add finding - "+str(e))
            sys.exit(0)

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

def nrFunctionSteps(fileName, lineNumber):
    firstLine      = fileName+":"+str(lineNumber)
    secondLine     = fileName+":"+str(lineNumber+1)
    firstLineAddr  = None
    secondLineAddr = None
    print("FROM        :",firstLine)
    #print("TO          :",secondLine)
    #timeout needed for long algorithms 
    child = pexp.spawn("gdb ./main", timeout=60)
    child.expect("\(gdb\) ")
    child.sendline("set style enabled off")

    child.expect("\(gdb\) ")

    #For a more precise instruction count use stepi, but it takes forever
    child.sendline("""define do_count\r\n
      set pagination off\r\n
      set $count=0\r\n
      while ($pc != $arg0)\r\n
          step\r\n
          set $count = $count+1\r\n
      end\r\n
      print $count\r\n
    end""")
    child.expect("\(gdb\) ")
    child.sendline("break main")
    child.expect("\(gdb\) ")
    child.sendline("run")
    child.expect("\(gdb\) ")

    ####### Get Address of firstLine
    child.sendline("info line "+firstLine)
    child.expect("\(gdb\) ")
    s = "".join(child.before.decode("utf-8").split("\r\n"))
    # Line 32 of "test.c" starts at address 0x55555555472b <main+41> and ends at 0x555555554748 <main+70>.
    m = re.search(r"starts at address ([0-9a-fx]+)",s)
    if m:
        firstLineAddr  = m.group(1)
    else:
        print("ERROR: could not determine address of "+firstLine)
        sys.exit(0)
    #print("First Line  :",firstLineAddr)
    
    ####### Get Address of secondLine
    child.sendline("info line "+secondLine)
    child.expect("\(gdb\) ")
    s = "".join(child.before.decode("utf-8").split("\r\n"))
    # Line 32 of "test.c" starts at address 0x55555555472b <main+41> and ends at 0x555555554748 <main+70>.
    m = re.search(r"starts at address ([0-9a-fx]+)",s)
    if m:
        secondLineAddr = m.group(1)
    else:
        print("ERROR: could not determine address of "+secondLine)
        sys.exit(0)
        
    child.sendline("break *"+firstLineAddr)
    child.expect("\(gdb\) ")
    
    child.sendline("continue")
    child.expect("\(gdb\) ")

    child.sendline("do_count "+secondLineAddr)
    child.expect("\(gdb\) ")

    #Save to be able to analyse the gdb output
    #file = open('Failed.txt', 'w')
    #file.write(str(child.before.decode("utf-8").split("\r\n")))
    #file.close()
    line = child.before.decode("utf-8").split("\r\n")[-2]

    m = re.search(" = (\d+)",line)
    _nrFunctionSteps = 0
    if m:
        _nrFunctionSteps = m.group(1)
        #print("nr Steps    :",_nrFunctionSteps)
        #print(_nrFunctionSteps)
    
    #child.interact()
    return _nrFunctionSteps


