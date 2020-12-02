#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#           tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import subprocess
import yaml
import sys
import os

inFileName  = "inject.yaml"

def loadYamlFile(inFile):
    _inDict = {}
    try:
        with open(inFile) as f:
            _inDict = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        #print("WARNING: "+str(e))
        pass
    return _inDict

def wasInjected(inFile,lines):
    nLines = 0
    with open(inFile,"r") as f:
        fLines = f.readlines()
        nEqual = 0
        for inLine in lines:
            l       = fLines[nLines].rstrip("\n")
            nLines += 1
            if inLine==l: nEqual+=1
    return nEqual==len(lines)

def injectFile(inFile, newLines):
    tmpFile = inFile+".tmp"
    with open(tmpFile,"w") as fOut:
        for l in newLines: fOut.write(l+"\n")
        with open(inFile,"r") as fIn:
            fLines = fIn.readlines()
            for l in fLines: fOut.write(l)
    os.remove(inFile)
    os.rename(tmpFile,inFile)

####################################################################################################
#                                            Main Function                                         #
####################################################################################################
try:
    with open(inFileName, 'r') as f:
        pass
except OSError as e:
    print("Nothing to do...")
    sys.exit(0)

I = loadYamlFile(inFileName)

for fileName in I:
    if not wasInjected(fileName,I[fileName]):
        print("Injecting %s..." %(fileName,))
        injectFile(fileName,I[fileName])
