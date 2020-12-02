#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
from   flask import escape
import schema as db
import subprocess
import pathlib
import shutil
import pprint
import utils
import json
import yaml
import glob
import uuid
import sys
import os
import re

# challenge types
import c_makefile

allChallenges = {}
allTags       = {}
idToKey       = {}
keyToID       = {}
currDir       = pathlib.Path(__file__).parent.absolute()
configFile    = os.path.join(currDir,"challenges.yaml")
tagsFile      = os.path.join(currDir,"tags.yaml")

def cResp(testNr, passFail, msg, wish="", seen="", x="", key=0, prevR=None):
    if (prevR==None):
        r = {}
    else:
        r = prevR
    r[key]         = {}
    r[key]["nr"]   = testNr
    r[key]["pass"] = passFail
    r[key]["msg"]  = msg
    r[key]["wish"] = wish
    r[key]["seen"] = seen
    r[key]["x"]    = x
    return r

def getChalConfig(chalID):
    #print("getChalConfig:",chalID)
    #print(allChallenges)
    chalKey = idToKey[chalID]
    chalCfg = allChallenges[chalKey]
    return chalCfg


################################################################################
################################################################################
################################################################################
################################################################################

def loadAIResult(tmpPath,headerLen):
    try:
      AIfile   = "{}/{}/ai.json".format(tmpPath,utils.resultsDir)
      AIresult = json.loads( open(AIfile,"r").read() )
      if len(AIresult)!=1:
          return None
      AIresult = AIresult[0]
      msg      = AIresult["msg"]
    except Exception as e:
        e=str(e)
        e = re.sub(r"/sifu_results/ai.json","",e)
        return {"msg":"Failure loading AI: "+e,'tag': 'NO_TAG', 'result': 'FAIL'}
    return AIresult

#
# evalChalFromDirStruct()
#   This function takes user input, creates a temporary project,
#   runs the challenge main file and collects the feedback output
#   to send back to the user
#
# Parameters
#   userName  - user name of the requester
#   userIP    - IP address of the user
#   chalID    - challenge identifier
#   chalFiles - user input coming from the browser
#
# Returns
#   result    - result message to send back to the user
#   logger    - print out from logger function
#   tmpDir    - folder where the temporary files are stored
#
# TODO: make sure run_jail is copied? Is this really necessary?
def evalChalFromDirStruct( userName,
                           userIP,
                           chalID,
                           chalFiles,
                           testing=False,
                           chalBaseFolder=".",
                           pathRoot='.',
                           origDir=None,
                           testwip=False      # flag for testiomaker 
                         ):
    _result = "FAIL: error while processing the challenge"
    _logger = ""
    tmpPath = ""
    try:
        nrHeader = 0                                  # remember the nr of header lines added
        if not(chalID in idToKey):
            return {"result":"Challenge not found", "logger":_logger, "solve":"false"}
        cfg     = getChalConfig(chalID)               # fetch the challenge configuration
        if not testing:
            newUUID = str(uuid.uuid4())                   # Generate new random UUID
            tmpPath = os.path.join(pathRoot,'upload',newUUID)
        else:
            tmpPath = pathRoot # NOTE: I take directly the "root path" pathRoot
        #print("TMP Challenge Path: ",tmpPath)
        copyFrom = os.path.join(chalBaseFolder,cfg["directory"])
        #print("Copy from",copyFrom," to ",tmpPath)
        if not testwip:                           # (testbuilding happens elsewhere)
            shutil.copytree(copyFrom,tmpPath)     # Recursively copy all files
        if not testing:
            #print("Copied files from",cfg["directory"])
            for f in chalFiles:                           # save all user files to temp folder
                fullPath = os.path.normpath(os.path.join(tmpPath,f))
                with open(fullPath,"w+") as o:            # make sure we overwrite the file
                    o.write(chalFiles[f])                 # write the user content to the file
            uHints = db.getUserHints(userName,chalID)     # load used hints by the user
            fNH    = os.path.join(tmpPath,"used_hints")   # generate path of dest. file name
            with open(fNH,"w+") as f:
                f.write(json.dumps(uHints))               # write used hints to file
            try:
                fName = os.path.join(tmpPath,"chal_info.json")
                #print("CHAL_INFO: "+fName)
                with open(fName,"w+") as f:
                    f.write(json.dumps({"chal_id":cfg["chal_id"]}))
            except Exception as e:
                print("ERROR in evalChalFromDirStruct: "+str(e))
        else :
            # just copy / override the regresion input files
            utils.copyTree(origDir,tmpPath)
        #print("Running", tmpPath)
        checkFile = cfg["run"]                        # retrieve command to evaluate challenge
        result = utils.executeOS( tmpPath, checkFile )# ... and run that command
        if not testing:
            AIr    = loadAIResult(tmpPath,nrHeader)       # load the result from the AI machinery
            _l1    = collectChallengeEvalLogs(tmpPath)    # collect the challenge log from logger to _l1 temp var
            _l2    = []                                   # _l2: temp var containing all lines
            for s in _l1:                                 # loop through all logger lines
                _l2.append( escape(s) )                   # escape the text (prevent XSS)
            _logger = "<br>".join(_l2)                    # add HTML code for new line
            if (None==AIr):                               # if the AI engine did not return any result...
                _result = "FAIL: no results were found"   # bail out with an error message tha no results are found
                if not testing:
                    db.addInteraction(userName, chalID, "FAIL", _result, tmpPath, userIP)
                return { "result"    : _result,
                         "logger"    : _logger,
                         "tmpDir"    : tmpPath,
                         "regression": "none",
                         "solve"     : "false" }
            tag    = AIr["tag"]                           # retrieve the AI tag for hints
            #print("AI Result:")                          # debugging output. to be removed
            #pprint.pprint(AIr)                           # debugging output. to be removed
            if tag in allTags:                            # does the tag match any known tag?
                myTag    = allTags[tag]                   # retrieve the dictionary (from YAML)
                tagDesc  = myTag["description"]           # required key = description (main tag)
                hintHtml = tagDesc.format(**myTag)        # perform string interpolation to generate HTML code
                if not testing:
                    db.addHintTag(userName,chalID,tag,hintHtml,userIP) # add hint to database
            if False:                                     # this is only for testing purposes
                myTag    = allTags["TEST_TAG"]            # the YAML file can contain a TEST_TAG for simple tests
                tagDesc  = myTag["description"]
                hintHtml = tagDesc.format(**myTag)
                if not testing:
                    db.addHintTag(userName,chalID,"TEST_TAG",hintHtml,userIP)
            if AIr["result"]=="OK":                       # if the AI engine states that all TCs have passed, then give the flag
                flag = str(cfg.get("flag","!!! HELP !!! UNDEFINED !!! HELP !!!")) # has the flag been defined in the YAML file?
                _result = "Well done, here is your flag: " + flag
                if cfg.get("unlocks",False):
                    next_challenge = str(cfg.get("unlocks",""))
                    _result += " You have unlocked a new <a href='/challenge/"+next_challenge+"' target='_blank'>challenge</a>" # TODO: consider adding the flag as an hint!

                if not testing:
                    db.addInteraction(userName, chalID, "SOLVE", _result, tmpPath, userIP)
                return { "result"    : _result,
                         "logger"    : _logger,
                         "tmpDir"    : tmpPath,
                         "regression": "none",
                         "solve"     : "true" } # return the flag to the user; this is where the function exists in case of OK
            else:                                         # the user failed the challenge...
                _result = "FAIL: "+AIr["msg"]             # give back the user message from the AI engine
                if not testing:
                    db.addInteraction(userName, chalID, "FAIL", _result, tmpPath, userIP)
                return { "result"     : _result,
                         "logger"     : _logger,
                         "tmpDir"     : tmpPath,
                         "regression" : "none",
                         "solve"      : "false" } # return FAIL to the user. this is where the function exists in case of FAIL
        else:
            return { "regression" : "done" }
    except Exception as e:
        _result = "UGLY ERROR: "+str(e)               # something very wrong happen, if we are here!
        print("UGLY ERROR: "+str(e))
        sys.exit(0)
    if not testing:
        db.addInteraction(userName, chalID, "FAIL", _result, tmpPath, userIP)
    return { "result"     : _result,
             "logger"     : _logger,
             "tmpDir"     : tmpPath,
             "regression" : "fail",
             "solve"      : "false" } # the function should normally not exit here!

################################################################################
################################################################################
################################################################################
################################################################################

#  origChalPath     - path from where the files will be copied
#  userChalPath     - temporary path where the files will be copied to
#  chalFileContents - contents of the challenge-specific file
#  chalFileName     - name of the challenge file
#  excludeLogic     - function that will filter copied files based on file name
#  headerAdd        - list of strings to add to the header of the challenge file
def prepareChallenge(origChalPath, userChalPath, chalFileContents, chalFileName, excludeLogic=lambda f:False, headerAdd=[]):
    # Step 1: Copy all challenge files, excluding what "should be excluded"
    origFiles = os.listdir(origChalPath)
    for fileName in origFiles:
        fullFileName = os.path.join(origChalPath, fileName)
        if os.path.isfile(fullFileName):
            if not( excludeLogic(fullFileName) ):
                #print("COPY "+fullFileName+" to "+userChalPath)
                shutil.copy(fullFileName, userChalPath)
    # Step 2: make sure we copy the run_jail.sh script
    fullFileName = "Challenges/chal_lib/run_jail.sh"
    shutil.copy(fullFileName, userChalPath)
    #print("COPY "+fullFileName+" to "+userChalPath)
    # Step 3: add the user-specific contents (header+user)
    chalFile = open(os.path.join(userChalPath, chalFileName), "w")
    for l in headerAdd:
        chalFile.write(l)
    chalFile.write(chalFileContents)
    chalFile.close()

##########################################################################################
# this function does the following:
#       1) create a random UUID
#       2) use UUID to create temporary folder to hold user solution to challenge
#       3) determine all the files to be excluded from initialization (based on config)
#       4) prepare the challenge by copying the files
#       5) generate a used_hints file in the challenge folder
#
# Input
#   userName              user name for which the challenge with be evaluated
#   cfg                   challenge configuration
#   chalPath              path of the original challenge
#   chalFileContents      player-specific contents of the challenge file
#   headerAdd             list of strings to add to the challenge file
#   chalXtraFileContents  player-specific contents of the challenge file
##########################################################################################
def initChallenge(userName, cfg, chalPath, chalFileContents, headerAdd, chalXtraFileContents):
    # Generate new random UUID
    newUUID = str(uuid.uuid4())
    # Create temporary directory
    userChalPath = os.path.join('upload',newUUID)
    os.mkdir(userChalPath)
    ##################
    try:
      xList = map(lambda s: s.strip(), cfg["filter_files"].split(","))
    except:
      xList = []
    chalFile = cfg["file"]
    xFiles   = [ os.path.join(chalPath,chalFile)]
    for x in xList:
        xPath = os.path.join(chalPath,x)
        xxList = glob.glob(xPath)
        xFiles.extend(xxList)
    prepareChallenge( chalPath,                   # orifinal challenge files
                      userChalPath,               # dir where to evaluate the tests
                      chalFileContents,           # player-specific content for challenge file
                      chalFile,                   # file name of challenge file
                      lambda fn: (fn in xFiles),  # copy-exclude logic
                      headerAdd )                 # header to add to challenge file
    try:
        fName = os.path.join(userChalPath,"chal_info.json")
        #print("CHAL_INFO: "+fName)
        with open(fName,"w+") as f:
            f.write(json.dumps({"chal_id":cfg["chal_id"]}))
    except Exception as e:
        print("ERROR in initChallenge / chal info: "+str(e))
    usedHints = db.getUserHints(userName,cfg["chal_id"])
    try:
        fName = os.path.join(userChalPath,"used_hints")
        with open(fName,"w+") as f:
            f.write(json.dumps(usedHints))
    except Exception as e:
        print("ERROR in initChallenge / usedHints: "+str(e))
    userExtraInputFileName = None
    try:
        userExtraInputFileName = cfg["input_file"]
    except:
        pass
    if not(userExtraInputFileName is None):
        try:
          fName = os.path.join(userChalPath,userExtraInputFileName)
          with open(fName,"w+") as f:
              f.write(chalXtraFileContents)
        except Exception as e:
            print("ERROR in initChallenge / chalXtraFileContents: "+str(e))
    return userChalPath

# This function will find out the challenge type and, based on that,
# run appropriate measures to execute the unit tests, etc...
#
# Parameters
#   userName             - user name of the requester
#   chalID               - challenge identifier
#   chalFileContents     - user input coming from the browser
#   chalXtraFileContents - user file coming from the browser
#
def evalChalFromString(userName,chalID,chalFileContents,chalXtraFileContents):
    if chalID in idToKey:
        cfg = getChalConfig(chalID)
    else:
        r = cResp(1,"FAIL", "Challenge not found")
        return (False,r,"")
    chalPath = cfg["directory"]
    dAll = {}
    if utils.debugMode:
        print("CHALLENGE TYPE: "+cfg["type"])
    testPassResult = True
    tcDir          = ""
    # FIXME: tcDir should not be created by the evaluators, but it should be
    #        a unique folder created here!
    for t in cfg["type"].split(","):
        cType = t.strip()
        if utils.debugMode:
            print("PROCESS TYPE: "+cType)
        testPass = True
        if cType=="c_makefile":
            (testPass,d,tcDir) = c_makefile.evalChal(userName,cfg,chalPath,chalFileContents,chalXtraFileContents)
        else:
            r = cResp(1,"FAIL", "Challenge type - "+cType+" - is unknown")
            return (False,r,"")
        if utils.debugMode==False:
            if None!=tcDir: shutil.rmtree(tcDir)
        if testPass==False:
            testPassResult = False
            #return (False,d)
        for k in d:
            dAll[str(t)+"_"+str(k)] = d[k]
    return (testPassResult,dAll,tcDir)

def collectChallengeEvalLogs(chalFolder):
    filePath = os.path.join(chalFolder,"sifu_results/log.txt")
    resultStrings = []
    try:
        with open(filePath,"r",encoding="utf8", errors='ignore') as f:
            lines = f.read().split("\n")
            foundStart = False
            for line in lines:
                if ("---- START Logging ----"==line):
                    if foundStart==True: # only capture the first "START Logging" line
                        break            # if "START Logging" is seen a 2nd time -> break (i.e. exit loop)
                    else:
                        foundStart=True  # signal that we observed the first "START Logging" line
                else:
                    resultStrings.append(line)
    except Exception as e:
        pass
        #print("EXCEPTION reading file: "+str(e))
    return resultStrings

def loadChallengesConfig(configFile):
  global allChallenges
  global idToKey
  global keyToID
  try:
      with open(configFile) as f:
          _allChallenges = yaml.load(f, Loader=yaml.FullLoader)
  except Exception as e:
      print("ERROR: "+str(e))
  allChallenges = {}
  idToKey       = {}
  keyToID       = {}
  try:
      for chal in _allChallenges:
          skipLoad = False
          try:
              disableChallenge = _allChallenges[chal]["disable"]
              if True==disableChallenge:
                  skipLoad = True
          except:
              pass
          if skipLoad==False:
              #print("Loading Challenge...: ",chal)
              allChallenges[chal] = _allChallenges[chal]
              chalKey = allChallenges[chal]["chal_id"]
              if chalKey in idToKey:
                  print("ERROR: key", chalKey," already exists")
                  os._exit(0)
              idToKey[chalKey] = chal
              keyToID[chal]    = chalKey
  except:
      print("ERROR: could not parse the YAML file correctly")
      sys.exit(0)
  return allChallenges

def loadTagsFile(tagsFile):
    _inDict = {}
    try:
        with open(tagsFile) as f:
            _allTags = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        print("ERROR: "+str(e))
    return _allTags

if __name__=="challenges":
    allChallenges = loadChallengesConfig(configFile)
    allTags       = loadTagsFile(tagsFile)
