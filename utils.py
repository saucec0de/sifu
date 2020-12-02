#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
from   datetime import datetime
import subprocess
import challenges
import hashlib
import shutil
import json
import uuid
import yaml
import sys
import os
import re

debugMode  = True
resultsDir = "sifu_results"

#
# Auxiliary class representing a JSTree node
#
class Node:
    def __init__(self, id, text, parent, icon=None):
        self.id     = id
        self.text   = text
        self.parent = parent
        self.icon   = icon

    def is_equal(self, node):
        return self.id == node.id

    def as_json(self):
        if (self.icon==None):
          return dict( id     = self.id,
                       parent = self.parent,
                       text   = self.text )
        else:
          return dict( id     = self.id,
                       parent = self.parent,
                       text   = self.text,
                       icon   = self.icon )

#
# executeOS(path,cmd)
#
#  path :   path where the command is located
#  cmd  :   command to execute
#
#  returns
#    the standard output + standard error of the
#    executed command as a single string
#
def executeOS(path, cmd):
    runCmd = 'cd '+path+'; '+cmd + " 2>&1"
    #x = subprocess.run([runCmd], shell=True, capture_output=True)  # only works after python 3.7!
    x = subprocess.run([runCmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return x.stdout.decode("utf-8") 
#
# GetCurrentTime()
#
#   returns
#      returns the current time as a string
#
def GetCurrentTime():
    now = datetime.now()
    return str(now)

#
# fileContents(fullPath)
#
#   fullPath : full path of the text file to be read
#
#   returns
#     the contents of the text file
#     on error, an empty string is returned
#
def fileContents(fullPath):
    contents = ""
    try:
        with open(fullPath,"r") as f:
            return f.read()
    except:
        return contents


#
# internal auxiliary function
#
def _get_nodes_from_path(path):
    nodes = []
    path_nodes = path.split("/")
    for idx, node_name in enumerate(path_nodes):
        parent = None
        node_id = "/".join(path_nodes[0:idx+1])
        if idx != 0:
            parent = "/".join(path_nodes[0:idx])
        else:
            node_id = "."
            parent = "#"
        
        if ((1+idx)==len(path_nodes)):
            #print("APPEND:",node_name, (1+idx)==len(path_nodes) )
            nodes.append(Node(node_id, node_name, parent, "jstree-file"))
        else:
            nodes.append(Node(node_id, node_name, parent))
    return nodes

#
# jstreeJSON(files)
#
def jstreeJSON(allFiles):
    unique_nodes = []
    for fName in allFiles:
        nodes = _get_nodes_from_path(fName)
        for node in nodes:
            if not any(node.is_equal(unode) for unode in unique_nodes):
                unique_nodes.append(node)
    retVal = [node.as_json() for node in unique_nodes]
    return retVal

def recursiveListDir(path):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn]

def processPost( p ):
    if (type(p) is dict):
        _d = {}
        for k in p.keys():
            _d[k] = processPost( p[k] )
        return _d
    elif (type(p) is list):
        _l = []
        for i in p:
            _l.append( processPost(i) )
        return _l
    elif (type(p) is int):
        return p
    elif (type(p) is str):
        _s = p
        try:
            if (p[0]=="[") or (p[0]=="{"):
                _s = json.loads(p)
        except:
            pass
        return _s
    else:
        raise Exception("ERROR while post-processing POST request")

def requestToDict(r):
    d = {}
    try:
        for k in r.args:
            v = r.args.get(k)
            d[k] = v
    except Exception as e:
        print("WARNING: (requestToDict)" + str(e))
        pass
    return d

    
def copyWithFullPath(srcFile,dstFile):
    dstPath = os.path.dirname(dstFile)
    os.makedirs(dstPath,exist_ok=True)
    shutil.copy(srcFile,dstFile)

def loadYamlFile(inFile):
    _inDict = {}
    try:
        with open(inFile) as f:
            _inDict = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        #print("WARNING: "+str(e))
        pass
    return _inDict

def fatalError(msg,errorCode=0):
    print("[FATAL] ERROR: "+str(msg))
    sys.exit(errorCode)

# This version of copyTree can copy from one folder to another
# without the neeed to create a directory at the destination
def copyTree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def fileHash(fileName):
    hashVal = None
    try:
        fileContents = open(fileName,"rb").read()
        md5Hash      = hashlib.md5(fileContents)
        md5Hashed    = md5Hash.hexdigest()
        hashVal      = str(md5Hashed)
    except:
        pass
    return hashVal
