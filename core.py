#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# This module implements sore Sifu functionalities
#
import utils
import re
import os

def isUserInList(userName,userList,db):
    uList = []
    if type(userList) is str:
        uList = [userList]
    elif type(userList) is list:
        uList = userList
    else:
        print("WARNING: isUserInList - wrong type in input!")
        return False

    for u in uList:
        if (u=="root") and (db.isUserAdmin(userName)): return True
    return False

def chalNameToChalID(configFile,chalName,defaultValue=None):
    """
    returns chalID for a given chalName
    """
    v = defaultValue
    try:
        v = configFile[chalName]['chal_id']
    except:
        pass
    return v

def getFilesForChalID(configFile,chalID):
    """
    returns dict of files and filenames for a given chalID
    """
    for item in configFile:
        if configFile[item]['chal_id']==chalID:
            files = configFile[item]['file']
            fileNames = configFile[item]['fname']
            break

    return {"files":     files,
            "fileNames": fileNames}

def splitCSVStringToList(csvString):
    r   = []
    tmp = csvString.split(",")
    for v in tmp:
        sl = v.lstrip(" \t")
        sr = sl.rstrip(" \t")
        r.append(sr)
    return r

def filterListOnRe(inList, inRe):
    outList = []
    for el in inList:
        if re.search(inRe,el):
            outList.append(el)
    return outList

# input: directory name
# output: dictionary with keys as subfolders and values as path names of the subfolders
def getAllSubfolders(dirName):
    folders = {}
    try:
        subFolders = [f.name for f in os.scandir(dirName) if f.is_dir()]
        for sf in subFolders:
            folders[sf] = os.path.join(dirName,sf)
    except:
        pass
    return folders
