#!/usr/bin/env python3

import sys
sys.path.append('..')

from   multiprocessing import Process, Queue, cpu_count
from   colored         import fg, bg, attr, style
import challenges        as   ch                  #pylint: disable=import-error
import pprint
import getopt
import shutil
import utils                                      #pylint: disable=import-error
import core                                       #pylint: disable=import-error
import time
import glob
import copy
import re
import os

# Global variables
gConfig          = None               # configuration file
gChallenges      = None               # all challenges
gRegressionTests = []                 # contains information about all the projects' regression tests
gWarnings        = False              # display warnings
gWarningIsError  = False              # stop execution at warnings
gConfigFileName  = "challenges.yaml"  # default configuration file is challenges.yaml
gFilterChalName  = ""                 # do not filter on challenge ID
gChalBaseFolder  = ".."               # base location of the challenges folder
gkeep            = False              # do not clean the testrun folder
gClean           = False              # clear out the testrun folder
gUtDiff          = False              # do not track unit test changes
gNProcs          = cpu_count()        # default value = 1 (i.e. single processing)
gQueue           = Queue()            # this queue will contain the results of running the TCs
gNoColor         = False              # by default use colors
CYAN             = fg('cyan')
RED              = fg('red')
BLUE             = fg('blue')
GREEN            = fg('green')
YELLOW           = fg('yellow')
WHITE            = fg('white')
RESET            = attr('reset')
BOLD             = attr('bold')

def runSingleTestCase(kwargDict, queue, ii):
    chalName       = kwargDict["chalName"]
    tcName         = kwargDict["tcName"]
    userName       = kwargDict["userName"]
    userIP         = kwargDict["userIP"]
    chalID         = kwargDict["chalID"]
    chalFiles      = kwargDict["chalFiles"]
    pathRoot       = kwargDict["pathRoot"]
    testing        = kwargDict["testing"]
    chalBaseFolder = kwargDict["chalBaseFolder"]
    origDir        = kwargDict["origDir"]
    baselineDir    = kwargDict["baselineDir"]

    print ('[       %sRUN%s]: %s/%s' % (CYAN,RESET,chalName,tcName))

    r = ch.evalChalFromDirStruct( userName,
                                  userIP,
                                  chalID,
                                  chalFiles,
                                  pathRoot       = pathRoot,
                                  testing        = testing,
                                  chalBaseFolder = chalBaseFolder,
                                  origDir        = origDir
                                )

    testResult = { "chalName"   : chalName,
                   "tcName"     : tcName,
                   "outcome"    : "tbd" if r["regression"]=="done" else "empty",
                   "tcResults"  : pathRoot,
                   "baselineDir": baselineDir
                 }

    queue.put(testResult)

if __name__ == '__main__':

    t_start = time.time()

    print("")
    print("(C) 2020, Siemens AG")
    print("          tiago.gasiba@gmail.com")
    print("")

    # default configurations
    l_filterChalName = ""              # do not filter on challenge ID
    l_filterChalType = "c_makefile"    # filter to select challenge types
    l_chalBaseFolder = ".."            # base location of the challenges folder
    l_keep           = False           # do not clean the testrun folder

    # check the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:b:nwW", ["help","config","filter_chalname=","filter_type=","keep", "unit_diff", "clean", "nprocs="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if (o == "-h") or (o=="--help"):
            print("Command line arguments:")
            print("")
            print("  Argument             Parameter  Default           Description")
            print("  [-b]                 STRING     ..                base folder of the challenges")
            print("  [-c|--config]        STRING     challenges.yaml   use a different configuration file")
            print("  [-n]                                              do not use colors")
            print("  [-w]                                              display warnings")
            print("  [-W]                                              treat warnings as errors (turns on -w)")
            print("  [--unit_diff]                                     track for changes in generated unit_test.json files")
            print("  [--filter_chalname]  STRING     ''                comma separated values with challenge ids REs")
            print("  [--filter_type]      STRING     'c_makefile'      comma separated values with types as REs")
            print("  [--keep]                                          keep test execution folder contents")
            print("  [--clean]                                         shorthand for 'rm -rf Challenges/reg_run/*'")
            print("  [--nprocs]                      [core_count]      runs regression on specified number of parallel processes")
            sys.exit()
        if (o == "-c") or (o=="--config"):
            gConfigFileName = a
        if (o=="--filter_chalname"):
            gFilterChalName = a
        if (o == "-b"):
            gChalBaseFolder = a
        if (o == "-n"):
            CYAN     = ""
            RED      = ""
            BLUE     = ""
            GREEN    = ""
            YELLOW   = ""
            WHITE    = ""
            RESET    = ""
            BOLD     = ""
            gNoColor = True
        if (o == "-w"):
            gWarnings = True
        if (o == "-W"):
            gWarnings = True
            gWarningIsError = True
        if (o == '--keep'):
            gkeep = True
        if (o == '--clean'):
            gClean = True
        if (o == '--unit_diff'):
            gUtDiff = True
        if (o == '--nprocs'):
            try:
                gNProcs = int(a)
                if gNProcs < 1:
                    print ('[     %sERROR%s]: --nprocs accepts only integers >1 !' % (RED,RESET))
                    sys.exit()
            except ValueError:
                print ('[     %sERROR%s]: --nprocs accepts only integers >1 !' % (RED,RESET))
                sys.exit()
            print ('[      %sINFO%s]: Running on %s parallel processes (%s cores available).' % (BLUE,RESET, gNProcs, cpu_count()))
    # there may be the case that cpu_count() fails on some systems.
    if gNProcs == 1: 
        print('[%s WARNING  %s]: Unable to determine available core count. Running regression as a single process.' % (YELLOW, RESET))
        print ('              Use --nprocs option to specify desired number of parallel processes.')
    else:
        print ('[      %sINFO%s]: Running on %s parallel processes (%s cores available).' % (BLUE,RESET, gNProcs, cpu_count()))
    
    
    # Step 0: ensure TestRunDir is clean (i.e. ../Challenges/reg_run is empty)
    l_baseTestRunDir = os.path.join(gChalBaseFolder,"Challenges","reg_run")

    if gClean:
        for d in [os.path.join(l_baseTestRunDir, d)
                    for d in os.listdir(l_baseTestRunDir)
                        if os.path.isdir(os.path.join(l_baseTestRunDir, d))]:
            # print ('[      %sINFO%s]: Deleting: %s' % (BLUE,RESET, d))
            shutil.rmtree(d)
    elif len(os.listdir(l_baseTestRunDir)) > 1:
            print ('[     %sERROR%s]: Test execution directory in unclean state!' % (RED,RESET))
            print ('                  Run again with --clean to clear out contents.')
            sys.exit()
    else:
        pass # reg_run clean, --clean not set, nothing to do.

    # Step 1: load configuration
    gConfig = utils.loadYamlFile(gConfigFileName)
    if not gConfig:
        utils.fatalError("Could not properly load the file "+str(gConfigFileName))
    gChallenges = ch.loadChallengesConfig(gConfigFileName)

    # filter on challenge types
    l_allNames    = list(gChallenges.keys())
    tmpChallenges = {}
    for chalName in gChallenges:
        for chalTypeRe in core.splitCSVStringToList(l_filterChalType):
            chalType =  gChallenges[chalName].get("type",None)
            if chalType:
                if re.search(chalTypeRe,chalType):
                    tmpChallenges[chalName] = copy.deepcopy(gChallenges[chalName])
            else :
                if chalTypeRe=="none":
                    tmpChallenges[chalName] = copy.deepcopy(gChallenges[chalName])
    gChallenges = tmpChallenges

    # Step 2: filter challenges based on user filters
    # filter on challenge names
    l_allNames    = list(gChallenges.keys())
    tmpChallenges = {}
    for chalNameRe in core.splitCSVStringToList(gFilterChalName):
        l_FilterNames = core.filterListOnRe(l_allNames,chalNameRe)
        if len(l_FilterNames)>0:
            for chalName in l_FilterNames:
                if None==tmpChallenges.get(chalName,None):
                    tmpChallenges[chalName] = copy.deepcopy( gChallenges[chalName]  )
        else:
            if gWarnings:
                print('[%s WARNING  %s]: No challenges found for name filter: %s' % (YELLOW, RESET, l_filterChalName))
                if gWarningIsError: sys.exit(0)
    gChallenges = tmpChallenges

    # TODO properly catch errors from eval function => report TC as failure (??)

    # create a list of processes to execute afterwards
    taskList = []

    # check unit test files for changes (once per challenge)
    if gUtDiff:
        unitTestList = []

    # Step 3:   Walk over the challenges to generate said task list
    # Step 3.5: if gUtDiff -> save path pairs to unittest.json for later

    for chalName in gChallenges:
        firstTest    = True
        l_ChalConfig = gChallenges[chalName]
        l_ChalDir    = os.path.join(gChalBaseFolder,l_ChalConfig["directory"])
        l_ChalRegDir = os.path.join(l_ChalDir,"regression")
        l_ChalID     = l_ChalConfig["chal_id"]
        l_regBaseDir = os.path.join(l_baseTestRunDir,
                                    l_ChalDir.replace("/","_").lstrip(".").lstrip("_"))
        if not os.path.isdir(l_ChalRegDir):
            gRegressionTests.append({"chalName":chalName,"outcome":"empty"})
            if gWarnings:
                print ('[%s WARNING  %s]: No regression suite defined for %s' % (YELLOW, RESET,chalName))
                if gWarningIsError: sys.exit(0)
            continue
        chalTests = core.getAllSubfolders(l_ChalRegDir)
        if not chalTests:
            gRegressionTests.append({"chalName":chalName,"outcome":"empty"})
            if gWarnings:
                print ('[%s WARNING  %s]: No regression suite defined for %s' % (YELLOW, RESET,chalName))
                if gWarningIsError: sys.exit(0)
            continue
        print ('[%s%sREGRESSION%s]: Running regression for %s' % (WHITE, BOLD, RESET,chalName))
        allTests = list(chalTests.keys())
        allTests.sort()
        for tcName in allTests:
            tcDir   = l_regBaseDir+"_"+tcName
            origDir = os.path.join(l_ChalRegDir,tcName) # where are my regression files located?
            # Hurray, we can finally run a testcase!
            #print("origDir ",origDir)    # where are my regression files?
            #print("pathRoot",tcDir)   # destination folder where the TC will be run
            #print("baseFolder",gChalBaseFolder)  # where to find the "Challenges" folder
            # print ('[       %sRUN%s]: %s/%s' % (CYAN,RESET,chalName,tcName))
            
            # Pass respective database input to each testcase
            if os.path.exists(origDir+"/input/database.json"):
                ch.db.dbFileName = origDir+"/input/database.json"
            else:
                if tcName.endswith('base') or not tcName.endswith('noDb'):
                    if gWarnings:
                        print ('[%s WARNING  %s]: No database file for %s - %s' % (YELLOW, RESET,chalName, tcName))
                        if gWarningIsError: sys.exit(0)
                    #continue

            processStructure = { 'userName'      : "darthVader",  # come with me and together we shall rule the universe!
                                 'userIP'        : "127.0.0.1",   # look mom, i'm at home!
                                 'chalID'        : l_ChalID,
                                 'chalFiles'     : None,
                                 'pathRoot'      : tcDir,
                                 'testing'       : True,
                                 'chalBaseFolder': gChalBaseFolder,
                                 'origDir'       : origDir+"/input",
                                 'baselineDir'   : origDir,
                                 'chalName'      : chalName,
                                 'tcName'        : tcName
                               }
            taskList.append(processStructure)
            
            # the step 3.5 shenanigans
            # (kept here to avoid having this Chal/Test doubleloop again)
            if gUtDiff:
                if firstTest:
                    pathExp = os.path.join(origDir,"input/unit_test.json")
                    pathReg = os.path.join(tcDir,"sifu_results/unit_test.json")
                    unitTestList.append({'chalName': chalName,
                                    'tcName'  : tcName,
                                    'pathExp' : pathExp,
                                    'pathReg' : pathReg
                                    })
                    firstTest = False

    # iterate over the tasks I want do do
    allFinished = False
    taskNr      = 0
    lastTaskNr  = len(taskList)
    processList = [None] * gNProcs
    nFinished   = 0

    if lastTaskNr==0:
        print ('[     %sERROR%s]: No tasks to run. Exiting...'% (RED,RESET))
        sys.exit(0)

    n = 0
    while not allFinished:
        time.sleep(0.01) # polling delay on process list
        currentTask = taskList[taskNr] if (taskNr<lastTaskNr) else None
        n += 1
        for ii in range(gNProcs):
            slotII = processList[ii]
            if currentTask and (not slotII): # ii'th slot free
                p = Process( target = runSingleTestCase,
                             args   = (currentTask,
                                       gQueue,
                                       taskNr)
                           )
                processList[ii] = p
                taskNr += 1
                currentTask = None
                p.start()
            elif slotII and (not processList[ii].is_alive()):
                result = gQueue.get()    # prints "[42, None, 'hello']"
                gRegressionTests.append(result)
                p.join()
                processList[ii] = None # free the slot
                nFinished += 1
            allFinished = nFinished>=lastTaskNr
            if allFinished: break

    # Step 3.5 strikes back
    # check if unit-test.json matches (from previously collated list)
    if gUtDiff:
        for unitTest in unitTestList:
            hashExp = utils.fileHash( unitTest['pathExp'] )
            hashReg = utils.fileHash( unitTest['pathReg'] )
            if not hashExp:
                if gWarnings:
                    print ('[%s WARNING  %s]: unit_test.json expected but not present. %s - %s' % (YELLOW, RESET, unitTest['chalName'], unitTest['tcName']))
                    if gWarningIsError: sys.exit(0) 
            elif not hashReg:
                if gWarnings:
                    print('[%s WARNING  %s]: %s - no unit_test.json produced by test.' % (YELLOW, RESET, unitTest['chalName'] ))
                    if gWarningIsError: sys.exit(0) 
            elif hashExp != hashReg:
                if gWarnings:
                    print('[%s WARNING  %s]: unit_test.json changed. Time to write more tests for %s?' % (YELLOW, RESET, unitTest['chalName']))
                    if gWarningIsError: sys.exit(0) 

    print("")
    print("")

    # Step 4: Walk over the regression results
    nrTotal   = 0
    nrTotalFail = 0
    print("Results:")
    for result in gRegressionTests:
        #pprint.pprint(result)
        if result["outcome"]!="tbd":
            result["outcome"] = "UNKNOWN"
            continue
        result["outcome"]  = "UNKNOWN"
        chalName           = result["chalName"]
        resultDir          = result["tcResults"]    + "/sifu_results"
        baselineDir        = result["baselineDir"]  + "/output"
        tcName             = result["tcName"]
        baseFiles          = glob.glob(baselineDir+"/**", recursive=True) #this syntax should scan for subfolders
        nrTotal            += 1
        nrFail             = 0
        if len(baseFiles)==0: continue
        for baseFile in baseFiles:
            if os.path.isdir(baseFile): continue
            # specify extra .regex extension on output files that
            # should allow predictable variance and still pass
            if os.path.splitext(baseFile)[1] == ".regex":
                with open (baseFile, "r") as f:
                    rExp = f.read()
                regressionFile = os.path.join( resultDir, os.path.split(baseFile)[-1][:-6] ) # cut out regex extension
                try:
                    with open (regressionFile, 'r') as f:
                        regressionFileContents = f.read()
                        cmpResult              = type(re.search(rExp, regressionFileContents)) == re.Match
                except FileNotFoundError as e:
                   print ('[%sError/FAIL%s]: %s - %s\n\t[ %s ]\n' % (RED, RESET,chalName, tcName, e)) 
                   cmpResult = None    
            else:
                regressionFile = os.path.join( resultDir, os.path.split(baseFile)[-1] )
                hashBaseline   = utils.fileHash( baseFile )
                if os.path.exists(regressionFile):
                    hashRegression = utils.fileHash( regressionFile )
                    cmpResult      = (hashBaseline == hashRegression)
                else:
                    print ('[%sError/FAIL%s]: %s - %s\n\t[ No such file: %s ]\n' % (RED, RESET,chalName, tcName, regressionFile)) 
                    cmpResult      = None
            if not cmpResult:  nrFail = nrFail + 1
        if (nrFail > 0):
            result["outcome"]  = "FAIL"
            print ('[      %sFAIL%s]: %s - %s' % (RED, RESET,chalName, tcName))
        else:
            result["outcome"]  = "PASS"
            print ('[      %sPASS%s]: %s - %s' % (GREEN, RESET,chalName, tcName))
        nrTotalFail += nrFail   
        #print("")
    
    if nrTotal>0:
        fmt_passPercent = "%.2f %%"%(100.0 - nrTotalFail / nrTotal * 100,)
        fmt_resultColor = 'black' if (nrTotalFail==0) else 'white'
        fmt_bgColor     = 'green' if (nrTotalFail==0) else 'red'
        fmt_resultText  = 'PASS'  if (nrTotalFail==0) else 'FAIL'
    else:
        fmt_passPercent = "? %"
        fmt_resultColor = 'blue'
        fmt_bgColor     = 'yellow'
        fmt_resultText  = "UNK"

    if gNoColor:
        fmt_resultColor = ""
        fmt_bgColor     = ""
    else:
        fmt_resultColor = fg(fmt_resultColor)
        fmt_bgColor     = bg(fmt_bgColor)
    print("\n\n%s%s|===================[ %s (%s) ]===================|%s"
          %
          (fmt_resultColor, fmt_bgColor, fmt_resultText, fmt_passPercent ,RESET)
         )
    # Print total run time.
    print ("[===%sDONE%s===]: Total regression process time: %.2f s." % (GREEN,RESET, time.time() - t_start))
    
    # perform cleanup if --keep isn't set
    if not gkeep:
        print ('[      %sINFO%s]: Cleaning up %s/* ...' % (BLUE,RESET, l_baseTestRunDir))
        for d in [os.path.join(l_baseTestRunDir, d)
                    for d in os.listdir(l_baseTestRunDir)
                        if os.path.isdir(os.path.join(l_baseTestRunDir, d))]:
            # print ('[      %sINFO%s]: Deleting: %s' % (BLUE,RESET, d)) # no need to spell them all out loud
            shutil.rmtree(d)
    else:
        print ('[      %sINFO%s]: The --keep option was set.' % (BLUE,RESET))
        print ('              Results left in ../Challenges/reg_run/[ChalName]_[TcName]')
    print ("")
    print ("")
    
