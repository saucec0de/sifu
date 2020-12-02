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
import shutil
import util
import sys
import re
import os

print("Start Test")
#####################################################################################
################## 32-bit w/o stack protection + Address Sanitizer ##################
#####################################################################################
# make main
ret = subprocess.run(["M32=yes SPECIAL=yes make clean inject main"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

p = pexpect.spawn("./run_jail.sh ./main a")
p.delaybeforesend=0.001
p.logfile = sys.stdout.buffer
try:
    p.expect("END TEST",timeout=2)
except:
    p.kill(9)
stdout = p.before.decode("utf-8")
with open("stderr.txt","w+") as f:
    f.write(stdout)

#####################################################################################
################# 64-bit w/ stack protection & w/ Address Sanitizer #################
#####################################################################################
# make main
ret = subprocess.run(["M32=no SPECIAL=no REM_TEST=no make clean main"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 

p = pexpect.spawn("./run_jail.sh ./main b")
p.delaybeforesend=0.001
p.logfile = sys.stdout.buffer
try:
    p.expect("END TEST",timeout=2)
except:
    p.kill(9)
stdout = p.before.decode("utf-8")
with open("stderr.txt","w+") as f:
    f.write(stdout)

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
