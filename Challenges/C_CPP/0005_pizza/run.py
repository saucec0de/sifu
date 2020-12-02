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
# make clean
ret = subprocess.run(["make clean"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# make main
ret = subprocess.run(["make main"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout = ret.stdout.decode("utf-8") 


##########################################################################################################################################
# EXP15-C. Do not place a semicolon on the same line as an if, for, or while statement
# https://wiki.sei.cmu.edu/confluence/display/c/EXP15-C.+Do+not+place+a+semicolon+on+the+same+line+as+an+if%2C+for%2C+or+while+statement
# Fix the bug in line "for (; ii<strlen(str1)-1; ii++); {" of utilities.c
##########################################################################################################################################
#
# Line to search for:
#    for (; ii<strlen(str1)-1; ii++); {
nHits = util.searchSource("utilities.c.pp","^\s*for.*;\s*{\s*$")
if nHits>0:
    util.addFinding("Program does not behave as expected",0,"INCREMENTAL_2_FUNC_1362465447_","TEST_100001")
    util.dumpFindings()
    # run analysis
    ret = subprocess.run(["./analyse.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # run AI
    ret = subprocess.run(["./ai.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.exit(0)

os.remove("pizzas.txt")
shutil.copyfile("pizzas.ok.txt","pizzas.txt")

p = pexpect.spawn("./run_jail.sh ./main")
p.logfile = sys.stdout.buffer
p.sendline("help")
p.sendline("napoli")
p.sendline("crudo")
p.sendline("view")
p.sendline("checkout")
p.sendline("carbonara")
p.sendline("napoli")
p.sendline("romana")
p.sendline("checkout")
p.sendline("view")
p.sendline("checkout")
p.sendline("exit")
try:
    p.expect("Thank you and goodbye!",timeout=1)
except:
    p.kill(9)
B = p.before.decode("utf-8")
# with open("expect_result.txt","w+") as f:
#     f.write(B)
# print("'"+p.before.decode("utf-8")+"'" )
# p.expect(pexpect.EOF)
expectResult = ""
with open("expect_result.txt","rb") as f:
    l = f.read()
    expectResult = l.decode("utf-8")
print(expectResult)
okFail = 1 if (expectResult==B) else 0
util.addFinding("Program is behaving as expected",okFail,"","TEST_900001")

##########################################################################################################################################
# EXP02-C. Be aware of the short-circuit behavior of the logical AND and OR operators
# https://wiki.sei.cmu.edu/confluence/display/c/EXP02-C.+Be+aware+of+the+short-circuit+behavior+of+the+logical+AND+and+OR+operators
# make sure that the participant rewrites the (1==nOrder) && printf as an if statement
##########################################################################################################################################
#
# Lines to search for:
#       (1==nOrder) && printf("You have ordered 1 pizza.\n");
#       (1<nOrder)  && printf("You have ordered %d pizzas.\n",nOrder);
#
nHits = util.searchSource("main.c.pp","^\s*\(1==nOrder\)\s*&&\s*printf")
okFail = 1
if nHits>0:
    okFail = 0
else:
    nHits = util.searchSource("main.c.pp","^\s*\(1<nOrder\)\s*&&\s*printf")
    if nHits>0:
        okFail = 0
    else:
        okFail = 1
util.addFinding("Bad coding style present in the code",okFail,"NO_TAG","TEST_101001")

##########################################################################################################################################
# STR05-C. Use pointers to const when referring to string literals
# https://wiki.sei.cmu.edu/confluence/display/c/STR05-C.+Use+pointers+to+const+when+referring+to+string+literals
# make sure the participant adds "const" to the string "pizzaFileName"
##########################################################################################################################################
# Lines to for:
#       char *pizzaFileName = "pizzas.txt";
#
nHits = util.searchSource("pizza.c.pp","^\s*const\s+char\s*\*\s*pizzaFileName\s*=\s*\"pizzas\.txt\"\s*;\s*$")
okFail = 0 if (nHits==0) else 1;
util.addFinding("Watch out for string literals",okFail,"NO_TAG","TEST_102001")

##########################################################################################################################################
# ERR01-C. Use ferror() rather than errno to check for FILE stream errors
# https://wiki.sei.cmu.edu/confluence/display/c/ERR01-C.+Use+ferror%28%29+rather+than+errno+to+check+for+FILE+stream+errors
# remove any checks with errno
##########################################################################################################################################
# Lines to for:
#       if (errno!=0) {
#
nHits = util.searchSource("pizza.c.pp","^\s*if\s*\(\s*errno")
okFail = 1 if (nHits==0) else 0;
util.addFinding("Using outdated error checking mechanism",okFail,"NO_TAG","TEST_103001")

##########################################################################################################################################
# ERR07-C. Prefer functions that support error checking over equivalent functions that don't
# https://wiki.sei.cmu.edu/confluence/display/c/ERR07-C.+Prefer+functions+that+support+error+checking+over+equivalent+functions+that+don%27t
# Developer should not use atoi()
##########################################################################################################################################
nHits = util.searchSource("pizza.c.pp","^.*=\s*atoi\s*\(pizzaCost\s*\)\s*;\s*$")
okFail = 1 if (nHits==0) else 0;
util.addFinding("Some possible errors are not being checked",okFail,"NO_TAG","TEST_104001")

##########################################################################################################################################
# INT08-C. Verify that all integer values are in range
# https://wiki.sei.cmu.edu/confluence/display/c/INT08-C.+Verify+that+all+integer+values+are+in+range
# Make sure the user handles potential integer overflow when addind a pizza to the basket
# How to check: replace cost in pizzas.txt with large amount and order two pizzas. the program should not "crash"
##########################################################################################################################################
stdout = ret.stdout.decode("utf-8") 
os.remove("pizzas.txt")
shutil.copyfile("pizzas.bad.txt","pizzas.txt")
p = pexpect.spawn("./run_jail.sh ./main")
p.logfile = sys.stdout.buffer
p.sendline("margherita")
p.sendline("margherita")
p.sendline("view")
p.sendline("checkout")
p.sendline("exit")
try:
    p.expect("Thank you and goodbye!",timeout=1)
except:
    p.kill(9)
B = p.before.decode("utf-8")
hitFlag = 1
for line in B.split("\n"):
    # main.c:31:11: runtime error: signed integer overflow: 2147480047 + 2147480047 cannot be represented in type 'int'
    if re.search(r"runtime error:",line) and re.search(r"signed integer overflow",line):
        hitFlag = 0
util.addFinding("There are integer handling issues in this program",hitFlag,"NO_TAG","TEST_120001")

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
