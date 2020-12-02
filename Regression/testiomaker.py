#!/usr/bin/env python3

import sys
sys.path.append('..')

from   colored    import fg, bg, attr, style
import challenges as ch 
import getopt
import shutil
import pprint
import utils
import core
import glob
import copy
import re
import os

# opts/args initialisation
gChal            = False           # mandatory
gTest            = False           # mandatory
gDb              = False           # default: no input database
gOverwrite       = False           # default: keep stuff in the folder
# -- Config shenanigans
gConfigFileName  = "challenges.yaml"   # default configuration file is challenges.yaml
gConfig          = None            # configuration object loaded from file
# -- Path shenanigans
gChalBaseFolder  = ".."            # base location of the challenges folder
gWorkRootDir      = "IO"            # where the magic happends
# -- Usecases
gInit            = False
gForce           = False
gRun             = False
gExport          = False
gCustomOut       = False
gOutFiles        = ['ai.json']
gFail            = False
gDel             = False
def print_help():
    print("")
    print("  Argument             Parameter  Default           Description")
    print("  [-c|--challenge]     STRING     ''                target challenge name")
    print("  [-t|--test]          STRING     ''                target test name")
    print("  [--db]                                            specify which database file to use")
    print("  [--config]           STRING     challenges.yaml   use a different configuration file")
    print("  [-i|init]                                         pull challenge files into ./IO/[chalName]_[testName]/input")
    print("  [-f|--force]                                      overwrite files if needed")
    print("  [-r|--run]                                        run input to generate output")
    print("  [-e|--export]                                     move files to Challenges/[chalName]/regression/[testName]")
    print("  [-o|--output=]                 'ai.json'          csv with generated output files of interest")
    print("  [--fail]                                          mark test as expected to fail")
    print("  [-d|--delete]                                     remove one/all tests for challenge")

def print_usage():
    print("\n|======================[ USAGE ]======================|")
    print("\n a. Pull needed challenge files into IO/input\n")
    print("\t testiomaker -i [-f|--force] -c chalName -t testName [--db=dbFile] [--config=configFile]")
    print("")
    print("\n b. Run challenge with current inputs, to generate and capture output \n")
    print("\t testiomaker -r -c chalName -t testName [--db=dbFile] [--config=configFile]")
    print("")
    print("\n c. Export testcase to Challenges/[chalName]/regression/[testName] \n")
    print("\t testiomaker -e -c chalName -t testName [--db=dbFile] [--config=configFile] [--fail]")
    print("")
    print("\n d. Delete one or all testcases for specified challenge, or delete all with '--force' \n")
    print("\t testiomaker -d -c chalName [-t testName]")
    print("\t testiomaker -d --force")
    print("")

if __name__ == '__main__':
    print("")
    print("(C) 2020, Siemens AG")
    print("          tiago.gasiba@gmail.com")
    print("")

    # check the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:t:ifreo:d",
                                   ["help","challenge","test", "db=", "config=", 'init' ,'force', 'run', 'export', 'output=', 'fail', 'delete']
                                  )
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if (o == "-h") or (o=="--help"):
            print_help()
            print_usage()
            sys.exit()
        if (o == "-c") or (o=="--challenge"):
            gChal = a
        if (o == "-t") or (o=="--test"):
            gTest = a
        if (o == "--db"):
            gDb = a
        if (o == "--config"):
            gConfigFileName = a
        if (o == "-i") or (o=="--init"):
            gInit = True
        if (o == "-f") or (o=="--force"):
            gForce = True # nvidia pls dont sue
        if (o == "-r") or (o=="--run"):
            gRun = True
        if (o == "-e") or (o=="--export"):
            gExport = True
        if (o == "-o") or (o=="--output="):
            gCustomOut = True
            gOutFiles  = core.splitCSVStringToList(a)
        if (o=="--fail"):
            gFail = True
        if (o == "-d") or (o=="--delete"):
            gDel = True

    # make sure what's mandatory stays mandatory
    if gInit or gRun or gExport: 
        if not gChal:
            print ('[%sERROR%s]: Missing challenge name.' % (fg('red'),attr('reset'))) 
            print_help()
        if not gTest:
            print ('[%sERROR%s]: Missing test name.' % (fg('red'),attr('reset'))) 
            print_help()
# ------ Delete option ----------
    elif gDel:
        # delete specific test
        if gChal and gTest:
            print ('[ %sINFO%s]: Deleting: %s/%s/%s' % (fg('cyan'),attr('reset'), gWorkRootDir, gChal, gTest))
            shutil.rmtree(os.path.join(gWorkRootDir, gChal, gTest))
            sys.exit()
        # delete all wip tests for challenge
        elif gChal:
            print ('[ %sINFO%s]: Deleting: %s/%s/*' % (fg('cyan'),attr('reset'), gWorkRootDir, gChal))
            shutil.rmtree(os.path.join(gWorkRootDir, gChal))
            sys.exit()
        # nuke everything under IO/*
        elif gForce:
            print ('[ %sINFO%s]: Deleting: %s/*' % (fg('cyan'),attr('reset'), gWorkRootDir))
            for subdir in glob.glob(os.path.join(gWorkRootDir, '*')):
                shutil.rmtree(subdir)
            sys.exit()
        # catch error if invalid param combination used
        else:
            print ('[%sERROR%s]: Deletion only valid for the following parameter combinations:'% (fg('red'),attr('reset'))) 
            print ('         -d -c [-t] | -d --force ')
            print ('         Use --help for more info.')
            sys.exit()
# ------ Delete option END -------

    # provide warnings and info for other optional params
    if not gDb and not (gInit or gRun or gDel):
        print ('[ %sWARN%s]: No database specified as input.' % (fg('yellow'),attr('reset')))
    if gConfigFileName != 'challenges.yaml':
        print ('[ %sINFO%s]: Using custom config: %s' % (fg('cyan'),attr('reset'), gConfigFileName))


# ------ Get challenge config file -------
    # Step 1: load configuration
    gConfig = utils.loadYamlFile(gConfigFileName)
    if not gConfig:
        utils.fatalError("Could not properly load the file "+str(gConfigFileName))
    gConfig = ch.loadChallengesConfig(gConfigFileName)
    
    # Step 2: keep only the needed challenge's configuration
    try:
        gConfig = gConfig[gChal]
    except KeyError:
        print('[%sERROR%s]: No challenge named: %s' % (fg('red'), attr('reset'), gChal))
        sys.exit(0)
    if gConfig['disable'] != False:
        print('[ %sWARN%s]: Writing tests for a currently disabled challenge %s' % (fg('yellow'), attr('reset'), gChal))    

    # Step 3: Check what's happening inside the IO folder
    l_OrigChalDir    = os.path.join(gChalBaseFolder, gConfig["directory"])
    l_ChalID         = gConfig["chal_id"]
    l_ChalFiles      = gConfig["files"].split(',')
    l_WorkDir        = os.path.join (gWorkRootDir,gChal,gTest)
    inCurrent        = []
 
# ------ Initialize directory -------
    if gInit:
        copyFrom = l_OrigChalDir
        inCurrent = [os.path.split(x)[-1] for x in glob.glob(os.path.join(l_WorkDir, '*'))]

        #force overwrite?
        if gForce:
            print ("[ %sINFO%s]: Deleting previous directory structure: %s" % (fg('cyan'),attr('reset'), l_WorkDir))            
            try:
                shutil.rmtree(l_WorkDir)
                inCurrent = []
            except FileNotFoundError as e:
                print('[ %sINFO%s]: Nothing to delete. Moving on...' % (fg('cyan'), attr('reset')))    
                #print("\t Original error message: ", e)
                pass
        # no force but length zero --> all is ok, copy
        if len(inCurrent) == 0:
            print ('[ %sINFO%s]: Copying from %s to %s' % (fg('cyan'),attr('reset'), copyFrom, l_WorkDir))
            print ("[ %sINFO%s]: Initialising 'input' and 'output' subfolders. Pruning unneedded files." % (fg('cyan'),attr('reset')))
            try:
                os.makedirs(l_WorkDir)
                utils.copyTree(copyFrom, l_WorkDir)    
                os.mkdir(os.path.join(l_WorkDir, 'input'))
                os.mkdir(os.path.join(l_WorkDir, 'output'))
            except Exception as e: # shouldn't ever get here
                print(e)
                sys.exit(2)
            try:
                shutil.rmtree(os.path.join(l_WorkDir, 'regression'))
            except FileNotFoundError as e:
                print('[ %sWARN%s]: No regression subfolder to delete.' % (fg('yellow'), attr('reset')))    
                print("\t Original error message: ", e)
                print("\t Moving on...")
                pass
            
            # now that we're certain files are where they should be
            # we can also populate the 'input/' folder 
            # with the challenge files
            for file in l_ChalFiles:
                copyFrom = os.path.join(l_WorkDir, file)
                copyTo   = os.path.join(l_WorkDir, 'input', file)
                shutil.move(copyFrom, copyTo)

        # if !gForce and non-empty destination folder --> problem
        else: 
            print('[%sERROR%s]: Can\'t initialise to non-empty IO/input folder.\n    Run again with --force.' % (fg('yellow'), attr('reset')))    
            print ("         Run again with '--force'.")
            sys.exit()
        
    #if !gInit: check if we have the workdir created
    elif not os.path.exists(l_WorkDir):
        print('[%sERROR%s]: Missing directory: %s.' % (fg('red'), attr('reset'), l_WorkDir))    
        print ("         Run with '--init' option first.")
        sys.exit()
 
# ------ Run/Export -------
    # No idea how/if the config file gets written/modified.
    # Keeping this here for good measure.
    l_ChalFiles.sort()
    # os.listdir and glob.glob both have results returned
    # in arbitrary order --> SORT for good measure
    inCurrent = os.listdir(os.path.join(l_WorkDir, 'input'))
    inCurrent.sort()
    

    # Step3: Check if all needed inputs are present
    # This applies for both running and exporting.
    if inCurrent != l_ChalFiles:
        print('[%sERROR%s]: Input file(s) mismatch:\nExpected: %s\n  Gotten: %s' % (fg('red'), attr('reset'), l_ChalFiles, inCurrent))    
        sys.exit()
    
    # ------ Run -------
    if gRun:
        # challenge files already copied
        # we just need to overwrite inputs @TODO
        if gDb:
            ch.db.dbFileName = gDb
        print ('[ %sINFO%s]: Running %s ...' % (fg('cyan'),attr('reset'), l_WorkDir))
        #print ('[>>%sdbg%sINFO%s]: pathRoot=%s, chalBaseFolder=%s, origDir=%s' % (fg('green'), fg('cyan'),attr('reset'), l_WorkDir, '..', l_WorkDir+"/input"))  
        r = ch.evalChalFromDirStruct( "darthVader",  # come with me and together we shall rule the universe!
                                      "127.0.0.1",   # look mom, i'm at home!
                                      l_ChalID,
                                      None,
                                      pathRoot       = l_WorkDir,
                                      testing        = True,
                                      chalBaseFolder = "..",
                                      origDir        = l_WorkDir+"/input",
                                      testwip        = True
                                    )
        # save outputs to /output
        for file in gOutFiles:
            copyFrom = os.path.join(l_WorkDir, "sifu_results", file)
            copyTo   = os.path.join(l_WorkDir, 'output', file)
            try:
                shutil.move(copyFrom, copyTo)
            except FileNotFoundError as e:
                print('[%sERROR%s]: %s' % (fg('red'), attr('reset'), e))
                print('[%si-%sERR%s]: Wanted:    %s' % (fg('cyan'), fg('red'), attr('reset'), gOutFiles))    
                print('[%si-%sERR%s]: Available: %s' % (fg('cyan'), fg('red'), attr('reset'), os.listdir(os.path.join(l_WorkDir, 'output'))))    
                sys.exit()
        
        # cleanup (just in case - maybe next run fails but results stay behind)
        print ('[ %sINFO%s]: Cleaning up ...' % (fg('cyan'),attr('reset')))
        shutil.rmtree(os.path.join(l_WorkDir, "sifu_results"))

        print ('[ %sDONE%s]: Run success. Output captured  under %s/output' % (fg('green'),attr('reset'), l_WorkDir))
        
        for outfile in glob.glob(l_WorkDir+"/output/*"):
            print ('\n[%si%sDONE%s]: CONTENTS OF %s[%s]%s:' % (fg('cyan'), fg('green'), attr('reset'), attr(1), outfile, attr('reset')))
            with open(outfile, 'r') as f:
                fContents = f.read()
                print (fContents)
                print ('')
        sys.exit()
    
    # ------ Export -------
    if gExport:
         
        # First make sure there's a defined output
        if len([os.path.split(x)[-1] for x in glob.glob(os.path.join(l_WorkDir, 'output', '*'))]) == 0 and len(gOutFiles)!=0:
            print('[%sERROR%s]: No output files currently exist, despite expected!' % (fg('red'), attr('reset')))
            print("        Use '--run' to generate expected outputs before exporting the testcase!" )
            sys.exit()
        
        # First check if somehow the challenge magically vanished
        # i.e. Maybe there's funny chalName edits between commits
        if not os.path.exists(l_OrigChalDir):
            print('[%sERROR%s]: No destination folder for challenge:' % (fg('red'), attr('reset')))
            print('[%si-%sERR%s]: Not found: %s' % (fg('cyan'), fg('red'), attr('reset'), l_OrigChalDir))    
            sys.exit()
        
        # Testcase destination folder: ../Challenges/[gChal]/[gTest]
        # First check if it's not already existing...
        l_dstTestPath = os.path.join(l_OrigChalDir,"regression", gTest)
        if os.path.exists(l_dstTestPath):
            print('[%sERROR%s]: Testcase folder already exists! %s' % (fg('red'), attr('reset'), l_dstTestPath))
            sys.exit()

        # Attempt creating the testcase folder structure
        try:
            os.makedirs(os.path.join(l_dstTestPath))
            os.mkdir(os.path.join(l_dstTestPath, 'input'))
            os.mkdir(os.path.join(l_dstTestPath, 'output'))
        except Exception as e:
            print('[%sERROR%s]: %s' % (fg('red'), attr('reset'), e))
            sys.exit()

        # Do the deed
        for subdir in ['input', 'output']:

            copyFrom = os.path.join(l_WorkDir, subdir)
            copyTo   = os.path.join(l_dstTestPath, subdir)
            try:
                utils.copyTree(copyFrom, copyTo)
            except Exception as e:
                print('[%sERROR%s]: %s' % (fg('red'), attr('reset'), e))
                sys.exit()

        # create [l_dstTestPath]/output/.fail file
        # if test marked as expected to fail
        if gFail:
            with open(os.path.join(l_dstTestPath, 'output', '.fail'), 'w+') as f:
                f.close()
        
        print ('[ %sDONE%s]: Exported successfully from %s to %s' % (fg('green'),attr('reset'), l_WorkDir, l_dstTestPath))
        sys.exit()
