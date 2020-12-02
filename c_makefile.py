#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# YAML Configuration for this checked
#
#     key          |  example               |   description
#     -------------|------------------------|--------------------------------------------------------------------
#     description: |  Challenge nr 1        |   challenge description
#     directory:   |  Challenges/chal_0001  |   directory where the source files for the challenge are stored
#     file:        |  func.c                |   main file that will be replaced by the user
#     chal_id:     |  000000000000          |   unique challenge id (see gen_id.py)
#     root:        |  template              |   get root_file from template directory (i.e. it is a template)
#     root_file:   |  chal.html             |   name of the template to provide to the user
#     run:         |  make                  |   command to run the unit tests (note: it will be sandboxed)
#     filter_files:|  main, *.s, *.o        |   files which are excluded from the copy
#     flag:        |  0000-0000-0000-0000   |   unique flag for the challenge
#     type:        |  c_makefile            |   type of analysis to do (i.e. C/C++ makefile)
#
import challenges as ch
import subprocess
import pprint
import shutil
import utils
import glob
import json
import uuid
import sys
import os
import re

funcHeaderAdd = [ '#define __OVERWRITE\n',
                  '#include "utils.h"\n',
                  '#include "deprecated.h"\n',
                  '#include "redirect.h"\n',
                  '#include "log.h"\n',
                  '\n'
                ]

def evalChal(userName, cfg, chalPath, chalFileContents, chalXtraFileContents):
    # TODO:
    #   the initChallenge should go to the challenges.py
    #   it makes no sense to be here.
    #   idea: the extra header can be either given by a function that
    #         this class returns back to the challenges.py OR
    #         it can be part of the YAML configuration OR
    #         it can be a special file located in the original challenge dir
    #
    print("c_makefile")
    userChalPath = ch.initChallenge(userName, cfg, chalPath, chalFileContents, funcHeaderAdd, chalXtraFileContents)
    # run checkFile
    checkFile = cfg["run"]
    result = utils.executeOS( userChalPath, checkFile )
    #pprint.pprint(result)

    # load results
    resultsDir = os.path.join( userChalPath, utils.resultsDir )
    if not(os.path.isdir(resultsDir)):
        # results directory was not found
        r = ch.cResp("1","FAIL", "Could not find results folder")
        return (False,r, userChalPath)
    resultsFiles = glob.glob( resultsDir+"/*.json" )

    if (0==len(resultsFiles)):
        # no results have been found
        # TODO: this might not be a fail, if we have more than one check...
        r = ch.cResp("1","FAIL", "no results have been found")
        return (False, r, userChalPath)

    allResults = []
    for resultFile in resultsFiles:
        try:
            results = json.loads( open(resultFile,"r").read() )
            allResults.extend(results)
        except:
            r = ch.cResp("1","FAIL", "Error while reading results")
            return (False, r, userChalPath)

    print("allResults:",allResults)
    r         = {}
    foundFail = False
    runningIndex = 1
    for t in allResults:
        print(t)
        if t["result"]!="OK":
            foundFail = True
        try:
            # Convert TEST_nn -> int(nn)
            prioPos = t["tc"].find("_")
            prio    = t["tc"][prioPos+1:]
        except:
            r = ch.cResp("1","FAIL", "Priority was not defined! ")
            return (False, r, userChalPath)
        msg     = t["msg"]
        r = ch.cResp( testNr   = prio,
                      passFail = t["result"],
                      msg      = msg,
                      wish     = t["expect"],
                      seen     = t["seen"],
                      x        = t["tag"],
                      key      = t["tc"]+"_"+str(runningIndex),
                      prevR    = r )
        runningIndex = runningIndex + 1

    return (not(foundFail),r,userChalPath)
