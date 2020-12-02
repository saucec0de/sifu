#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import subprocess
import config
import pprint
import getopt
import sys

def getSingleTool(toolName):
    try:
        allTools = config.cfg.get("Tools",None)
        toolCfg  = allTools.get(toolName,None)
        return toolCfg
    except:
        return None

def getListOfTools():
    try:
        allTools    = config.cfg.get("Tools",None)
        listOfTools = []
        for k in allTools.keys():
            if allTools[k].get("enabled",False):
                listOfTools.append(k)
        return listOfTools
    except:
        return None

def startTool(toolName):
    thisTool    = getSingleTool(toolName)
    startScript = thisTool["start"]
    ret         = subprocess.run(startScript,shell=True)

def stopTool(toolName):
    thisTool   = getSingleTool(toolName)
    stopScript = thisTool["stop"]
    ret        = subprocess.run(stopScript,shell=True)

if __name__ == '__main__':
    print("")
    print("(C) 2020, Siemens AG")
    print("          tiago.gasiba@gmail.com")
    print("")

    allTools = getListOfTools()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "huU", [])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    for o, a in opts:
        if (o == "-h"):
            print("Command line arguments:")
            print("")
            print("  Argument       Parameter  Default    Description")
            print("  [-h|--help]                          get this help")
            print("  [-u|-U]                              start (-U) or do not start (-u) external tools")
            print("")
            sys.exit()
        if (o == "-u"):
            for tool in allTools:
                stopTool(tool)
        elif (o == "-U"):
            for tool in allTools:
                startTool(tool)
        else:
            assert False, "unhandled option"
