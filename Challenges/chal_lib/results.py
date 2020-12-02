#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
#
# This file implements a standardized way to communicate TC pass/fail to the Sifu backend infrastructure
#

import pprint
import base64
import json
import os

rDBFile = "sifu_results/unit_test.json"

def loadResults():
    """ loadResults()

        loads and returns the current JSON results file

        NOTE: file name of the JSON results file is given by internal variable rDBFile
    """
    r = []
    try:
        with open(rDBFile) as f:
            lines = f.read()
        r = json.loads(lines)
    except:
        pass
    return r

def addResult(rDB, passFail, tcName, desc, expect, seen, tag, identifier=None):
    """ addResult()

        adds a new result to the existing database

        Variable  |  Description
        ----------+--------------------------------------------------------------------------------
        rDB       |  memory-cached results DB variable (list of dictionaries)
        passFail  |  int = 0 (fail) or = 1 (pass)
        tcName    |  string of type ABC_nn, where ABC is a test indicator and nn is the priority
        expect    |  results that the TC was expecting
        seen      |  results that were observed by the TC
        tab       |  additional information to the TC
        identifier|  can be optionally added (for e.g. to allow run.py/checker.py to label a finding that feedback.py will pick up)

        NOTE: file name of the JSON results file is given by internal variable rDBFile
    """
    r           = {}
    r["tc"]     = tcName
    r["msg"]    = desc
    r["expect"] = str( base64.b64encode(expect.encode("utf-8")), "utf-8" )
    r["seen"]   = str( base64.b64encode(seen.encode("utf-8")), "utf-8" )
    r["tag"]    = tag
    r["result"] = "OK" if (passFail==1) else "FAIL"

    if identifier is not None:
        r["identifier"] = identifier

    rDB.append(r)
    return rDB

def saveResults(rDB):
    """ addResult()

        saves the localy memory-cached results database into the JSON results file

        Variable  |  Description
        ----------+--------------------------------------------------------------------------------
        rDB       |  memory-cached results DB variable (list of dictionaries)

        NOTE: file name of the JSON results file is given by internal variable rDBFile
    """
    try:
        os.mkdir("sifu_results")
    except:
        pass
    with open(rDBFile,"w+") as f:
        f.write( json.dumps(rDB, indent=2) )
        f.write("\n") # make sure we have a new-line at the end-of-file (important for C-routines)

