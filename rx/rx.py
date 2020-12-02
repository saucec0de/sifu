#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import pathlib
import getopt
import yaml
import json
import sys
import re
import os

def loadYamlFile(inFile):
    _inDict = {}
    try:
        with open(inFile) as f:
            _inDict = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        print("WARNING: "+str(e))
        pass
    return _inDict

def arrayToIndexes(arr):
    idx = 1
    d   = {}
    for a in arr:
        d[a]  = idx
        idx  += 1
    return d

def simpleMatch(inString,inList):
    for inRe in inList:
        m = re.search(inRe,inString)
        if m: return True
    return False

def subSearch(fileLines,regEx,info,outIndexes,lineOffset=0,stopFirst=False):
    allMatches = []
    for lineNumber in range(len(fileLines)):
        line = fileLines[lineNumber].rstrip("\n\r\t")
        m    = re.search(regEx,line)
        if m:
            newMatch = { "_fileName"  : info["fileName"],
                         "_lineNumber": lineNumber+lineOffset,
                         "_rx"        : info["pattern"],
                         "_set"       : info["rxSet"],
                         "_match"     : line
                       }
            for o in outIndexes:
                idx = outIndexes[o]
                try:
                    val = m.group(idx)
                except:
                    val = None
                newMatch[o] = val
            allMatches.append(newMatch)
            if stopFirst: return (allMatches, lineNumber)
    return (allMatches,len(fileLines))

if __name__ == '__main__':
    patternFile     = None
    fileToScan      = None
    recursiveSearch = False
    outputFile      = None
    searchSet       = "all"

    # check the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:f:Ro:s:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if (o == "-h") or (o=="--help"):
            print("")
            print("(C) 2020, Siemens AG")
            print("          tiago.gasiba@gmail.com")
            print("")
            print("Tiago's swiss army knife for Regular eXpressions")
            print("")
            print("Command line arguments:")
            print("")
            print("  Argument       Parameter  Default    Description")
            print("  [-h|--help]                          get this help")
            print("  [-p]           STRING                pattern file (YAML)")
            print("  [-f]           GLOB                  files to scan")
            print("  [-R]                      No         make a recursive search")
            print("  [-o]           STRING                output file (JSON)")
            print("  [-s]           RE,CSV     all        sub-set of patterns to run")
        if (o == "-R"): recursiveSearch = True
        if (o == "-p"): patternFile     = a
        if (o == "-f"): fileToScan      = a
        if (o == "-o"): outputFile      = a
        if (o == "-s"): searchSet       = a

    if not patternFile:
        print("Please specify a pattern file")
        sys.exit(0)
    if not fileToScan:
        print("Please specify a file to scan")
        sys.exit(0)

    allFiles = []
    if recursiveSearch:
        for path in pathlib.Path(".").rglob(fileToScan):
            fileName = os.path.join(path.parents[0],path.name)
            allFiles.append(fileName)
    else:
        for path in pathlib.Path(".").glob(fileToScan):
            fileName = os.path.join(path.parents[0],path.name)
            allFiles.append(fileName)

    # TODO: Bug1:
    #           what if the RE includes a ',' in this case, we have a bug...
    #           altough this will probably not happen often
    #       Bug2:
    #           if the set contains a "forbidden symbol", e.g. "+", then
    #           the command line parameter looks very ugly... oh well...
    activeSets   = []
    _activeSets  = searchSet.split(",")
    if searchSet == "all": _activeSets = [".*"]
    for aS in _activeSets:
        aS = "^" + aS.lstrip("^")
        aS = aS.rstrip("$") + "$"
        activeSets.append(aS)

    allPatterns = loadYamlFile(patternFile)
    allMatches  = []

    for fileName in allFiles:
        # Read all the lines
        # TODO: limitation of this approach is that, if the file
        #       is very large, a lot of memory will be used here
        with open(fileName,"r") as fileIn:
            fileLines = fileIn.readlines()

        # Main Engine
        for pattern in allPatterns:
            rxSet = allPatterns[pattern].get("set","")
            if not simpleMatch(rxSet,activeSets): continue
            flag       = True
            lineOffset = 0
            currPattn  = allPatterns[pattern]
            rxSet      = currPattn.get("set","")
            _patMatch  = {}
            nProtect   = 0
            while flag:
                nProtect += 1
                if nProtect>1000000:
                    printf("WARNING: probably there is something wrong with the code... let's bail out...")
                    sys.exit(0)
                regEx      = currPattn.get("rx",None)
                out        = currPattn.get("out",[])
                outIndexes = arrayToIndexes(out)
                if regEx is None:
                    print("ERROR: rx not defined for '%s'" %(pattern,))
                    sys.exit(0)
                searchLines = fileLines[lineOffset:]
                if not searchLines: break
                (_allMatches, nLines) = subSearch( searchLines,
                                                   regEx,
                                                   { "fileName": fileName,
                                                     "pattern" : pattern,
                                                     "rxSet"   : rxSet
                                                   },
                                                   outIndexes,
                                                   lineOffset,
                                                   stopFirst = True
                                                 )
                lineOffset += nLines + 1
                if not _allMatches: break
                if len(_allMatches)!=1:
                    print("Huston, we have a problem", _allMatches)
                    sys.exit(0)
                for k in _allMatches[0]:
                    if k in ['_lineNumber', "_match"]:
                        # this ones, save as arrays
                        if k not in _patMatch:
                            _patMatch[k] = [ _allMatches[0][k] ]
                        else :
                            _patMatch[k].append( _allMatches[0][k] )
                    else:
                        _patMatch[k] = _allMatches[0][k]

                try:
                    currPattn = currPattn["next"]
                except:
                    # continue the search, based on top-level pattern
                    allMatches.append(_patMatch)
                    _patMatch  = {}
                    currPattn  = allPatterns[pattern]
            pass
    if outputFile:
        with open(outputFile,"w") as fOut:
            fOut.write(json.dumps(allMatches))
    else:
        print(json.dumps(allMatches))
