#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#           tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# This file implements the AI machinery that
# is responsible to give a single feedback to the user
#
from   datetime import datetime, timedelta
import results
import shutil
import json
import re
import subprocess

inFileName  = "sifu_results/unit_test.json"
outFileName = "sifu_results/ai.json"
#HINT_DELAY  = 60*4  # 4 minutes
HINT_DELAY  = 2     # ... seconds   (use only for Debugging purposes!)


# first run feedback.py if it exists
# ==================================
try:
    with open('feedback.py', 'r') as f:
        subprocess.run(["./feedback.py"])
except OSError as e:
        pass # OK, it does not exist


def loadUsedHints():
    _usedHints = []
    try:
        with open("used_hints","r") as f:
            _r = f.read()
            _usedHints = json.loads(_r)
    except Exception as e:
        pass
        #print("Exception: "+str(e))
    return _usedHints

def timDiff( t1, t2 ):
    diff = 1e90
    try:
        diff = (t1-t2).total_seconds()
    except:
        pass
    return diff

currTime  = datetime.now()
usedHints = loadUsedHints()
hintList  = []
timeHint  = {} 
for h in usedHints:
    hintList.append( h["hint"] )
    t = h["ts"]
    d = datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")
    timeHint[ h["hint"] ] = d

try:
    ################################################################
    # Step 1: Process the used hints
    ################################################################
    currResults = results.loadResults()
    # FIXME: filter already used hints
    for result in currResults:
        if (result["tag"] in hintList) and (result["result"]=="FAIL"):
            result["tag"] = ""

    # process INCREMENTAL_n_<tag>
    for result in currResults:
        m = re.match("^INCREMENTAL_(\d)+_(.*)",result["tag"])
        if m:
            maxTags = int(m.group(1))
            tag     = m.group(2)
            nTagsAlreadySent = 0
            for h in hintList:
                if re.match("^"+tag+"\d+",h):
                    nTagsAlreadySent = nTagsAlreadySent + 1
            if nTagsAlreadySent<maxTags:
                try:
                    td = timDiff(currTime,timeHint[tag+str(nTagsAlreadySent)])
                except:
                    td = 1e90
                if td>HINT_DELAY: # only provide a new hint after 4 minutes of last hint !
                    result["tag"] = tag+str(nTagsAlreadySent+1)
                else:
                    result["tag"] = ""

    results.saveResults(currResults)

    ################################################################
    # Step 2: Process the unit_test.json to a single ai.json file
    ################################################################
    unitTests = []
    with open(inFileName,"r") as f:
        unitTests = json.loads(f.read())

    finalTC   = None
    foundPass = False
    currPrio  = 9999999999
    for t in unitTests:
        tcName   = t["tc"]
        tcResult = t["result"]
        (tcType,tcPrio) = tcName.split("_")
        try:
            tcPrio = int(tcPrio)
        except:
            tcPrio = 10
        if tcResult=="OK": foundPass = True
        if tcResult=="FAIL":
            if (finalTC is None):
                finalTC  = t
                currPrio = tcPrio
            else:
                if tcPrio < currPrio:
                    finalTC  = t
                    currPrio = tcPrio
    if (foundPass==True) and (None is finalTC):
        # no TC has failed and at least one has passed this means that the overall status is OK
        finalTC = {'tc': 'TEST_0', 'msg': "Well done!", 'expect': '', 'seen': '', 'tag': '', 'result': 'OK'}
    if (foundPass==False) and (None is finalTC):
        # no TC has failed and no OK was found - this should never happen!
        finalTC = {'tc': 'TEST_0', 'msg': "Zero does not bring you anywhere!", 'expect': '', 'seen': '', 'tag': '', 'result': 'FAIL'}

except Exception as e:
    msg = "AI FAIL: "+str(e)
    print(msg)
    finalTC = {'tc': 'TEST_0', 'msg': msg, 'expect': '', 'seen': '', 'tag': '', 'result': 'FAIL'}

finalReport = json.dumps([finalTC],indent=4)
with open(outFileName,"w+") as f:
    f.write(finalReport)

