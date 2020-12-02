#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import subprocess
import results
import pexpect
import random
import string
import shutil
import util
import sys
import re
import os

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def runTestAndMatch( expect, strIn, strMatch, fileOut=None, debug=False):
    foundMatch = 0
    p = None
    try:
        p = pexpect.spawn("./run_jail.sh ./main")
    except:
        return False
    try:
        p.delaybeforesend=0.001
        rString = randomString(44)
        if debug: p.logfile = sys.stdout.buffer
        p.sendline(strIn)
        p.expect(expect)
        p.sendline(rString)
        p.expect(pexpect.EOF, timeout=5)
        B = p.before.decode("utf-8")
        p.kill(9)
        _lines = map (lambda s: s.rstrip("\r"), B.split("\n"))
        lines = []
        for line in _lines:
            lines.append(line)
            if (re.search(strMatch,line)):
                foundMatch = foundMatch + 1
            if (re.search("^XLINE = '"+rString+"'$",line)):
                foundMatch = foundMatch + 1
        if debug: print("----END----")
        if debug: print("")
        return (foundMatch==2)
    except Exception as e:
        #print("WARNING:",str(e))
        return False
    finally:
        if fileOut:
            B = p.before.decode("utf-8")
            _lines = map (lambda s: s.rstrip("\r"), B.split("\n"))
            with open(fileOut,"a+") as f:
                for line in _lines:
                  f.write(line+"\n")
    return (foundMatch==2)



print("Start Test")
# make clean
ret = subprocess.run(["make clean"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# make inject
ret = subprocess.run(["make inject"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# make main
ret = subprocess.run(["make main"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8")

okFail = 1
if runTestAndMatch("result = ","n","^ERROR: gets was used!$","stderr.txt"):
    okFail = 0
util.addFinding("Usage of dangerous function",okFail,"INCREMENTAL_2_FUNC_1246832686_B_","TEST_100000")

okFail = 1
if runTestAndMatch("result = ","y","^ERROR: gets was used!$","stderr.txt"):
    okFail = 0
util.addFinding("Usage of dangerous function",okFail,"INCREMENTAL_2_FUNC_1246832686_B_","TEST_100000")

okFail = 0
if runTestAndMatch("result = ","y","^1$","stderr.txt"):
    okFail = 1
util.addFinding("Program is not behaving as expected",okFail,"","TEST_900001")

okFail = 0
if runTestAndMatch("result = ","Y","^1$","stderr.txt"):
    okFail = 1
util.addFinding("Program is not behaving as expected",okFail,"","TEST_900002")

okFail = 0
if runTestAndMatch("result = ","n","^0$","stderr.txt"):
    okFail = 1
util.addFinding("Program is not behaving as expected",okFail,"","TEST_900003")

okFail = 0
if runTestAndMatch("result = ","N","^0$","stderr.txt"):
    okFail = 1
util.addFinding("Program is not behaving as expected",okFail,"","TEST_900004")

okFail = 0
if runTestAndMatch("result = ","X","^0$","stderr.txt"):
    okFail = 1
util.addFinding("Program is not behaving as expected",okFail,"","TEST_900005")

okFail = 0
if runTestAndMatch("result = ","X"*90000,"^0$","stderr.txt"):
    okFail = 1
util.addFinding("Reading STDIN not in synch with other reads",okFail,"INCREMENTAL_4_FUNC_1246832686_A_","TEST_900006")


############################################
############################################
############################################
############################################
############################################
util.dumpFindings()
# run analysis
ret = subprocess.run(["./analyse.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# run AI
ret = subprocess.run(["./ai.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
