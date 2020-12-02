#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# Database Schema
#
#   Table: users - list of users that can login to the system / root is special user (userID=0)
#       userName     : (string)  name of team used to login to the website
#       userPassword : (string)  hashed version of the password
#       userID       : (integer) ID of user
#       isAdmin      : (bool)    False: not admin, True: admin
#       sessionID    : (string)  session ID for the user
#
#   Table: chal_nr_times - used to limit the number of answers to challenges
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: unlock - when the user visits a new challenge, it will be unlocked with an entry in this table
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: unlock_file - when solving challenges, this will unlock the next file
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       fileName     : (string) name of unlocked file
#       unlockCode   : (string) code used to unlock the file
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: reports - user reports something wrong with a challenge
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       message      : (string) description of the problem
#       userContent  : (string) specific user content (main file)
#       inputContent : (string) specific user content (input file)
#       ts           : (string) timestamp
#       folder       : (string) where results are stored
#       ip           : (string) IP address of client
#
#   Table: timeline - records user interaction with the Sifu platform
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       ts           : (string) timestamp
#       type         : (string) type of interaction
#       message      : (string) message specific of interaction
#       folder       : (string) where results are stored
#       ip           : (string) IP address of client
#
#   Table: heartbeat - records which challenge the user is currently looking at
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: hints - records user hints (as tags) received by users
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       hint         : (string) hint tag
#       html         : (string) html presented to the user
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: chal_feedback - records user feedback after solving a challenge
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       rate1        : (string) (Likert 1...5) : Rate this challenge"
#       rate2        : (string) (Likert 1...5) : How well could you recognize this vulnerabilitie(s) in production code?
#       rate3        : (string) (Likert 1...5) : How well did you know how to fix this problem(s) in production code?
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
#
#   Table: chal_cache - cache files from the user interface
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       cacheDir     : (string) directory where files are cached
#
from   flask_login       import UserMixin
from   tinydb            import TinyDB
from   tinydb            import Query
from   tinydb.operations import delete
from   tinydb            import where
from   passlib.hash      import bcrypt_sha256
from   pprint            import pprint as p
import threading
import binascii
import hashlib
import uuid
import utils
import sys
import os

lock = threading.Lock()

if os.path.isdir("/share"):
    dbFileName = "/share/database.json"
else:
    dbFileName = "database.json"
#print("DATABASE FILE: ",dbFileName)

class User(UserMixin):
    def __init__(self,
                 userID,
                 userName="unknown",
                 userPassword="",
                 hashPass=True,
                 isAdmin=False,
                 sessionID=None):
        self.name     = userName
        self.isAdmin  = isAdmin
        self.userID   = userID
        if sessionID:
            self.sessionID = sessionID
        else:
            self.sessionID = str(uuid.uuid4())[-12:]
        self.id = self.sessionID
        if hashPass:
          self.password = "" if (userPassword=="") else bcrypt_sha256.hash(userPassword)
        else:
          self.password = userPassword
        
    def __repr__(self):
        return "%s/%s/%s/%s" % (str(self.id), self.name, self.password, self.sessionID)

    def dbEntry(self):
        return { "userName":     self.name,
                 "userPassword": self.password,
                 "userID":       self.userID,
                 "isAdmin":      self.isAdmin,
                 "sessionID":    self.sessionID }

def getUsers():
    r = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            r         = userTable.all()
        except Exception as e:
            print("Exception - getUsers: "+str(e)+"\n")
    return r

def _highestUserID():
    userList = getUsers()
    maxUID    = -1
    for u in userList:
        uid = u["userID"]
        if (uid>maxUID): maxUID = uid
    return maxUID

def _insertUser(userName, hashPassword, isAdmin=False):
    exception = None
    newID = 1 + _highestUserID()
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            nUsers    = len(userTable)
            if (nUsers>0):
                q = Query()
                u = userTable.search(q.userName==userName)
                if len(u)>0:
                    raise Exception("user already exists")
            u = User(newID,userName,hashPassword,hashPass=False,isAdmin=isAdmin,sessionID=None).dbEntry()
            userTable.insert(u)
        except Exception as e:
            exception = "Could not open database: "+str(e)
    if (exception!=None):
        raise Exception(exception)

def createNewSession(userName):
    exception = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            nUsers    = len(userTable)
            if (nUsers>0):
                q = Query()
                u = userTable.search(q.userName==userName)
                if len(u)==0:
                    raise Exception("user does not exist")
                thisUserID    = u[0]["userID"]
                thisUserPass  = u[0]["userPassword"]
                thisIsAdmin   = u[0]["isAdmin"]
                thisPassword  = u[0]["userPassword"]
                newUser = User( userID       = thisUserID,
                                userName     = userName,
                                userPassword = thisPassword,
                                hashPass     = False,         # password should not be changed!
                                isAdmin      = thisIsAdmin,
                                sessionID    = None           # force creation of a new sessionID
                              )
                userTable.update(newUser.dbEntry(),where("userName")==userName)
                return newUser
            else :
                exception = "Database is empty!"
        except Exception as e:
            exception = "Could not open database: "+str(e)
    if (exception!=None):
        raise Exception(exception)

def insertUser(userName, userPassword, isAdmin=False):
    exception = None
    newID = 1 + _highestUserID()
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            nUsers    = len(userTable)
            if (nUsers>0):
                q = Query()
                u = userTable.search(q.userName==userName)
                if len(u)>0:
                    raise Exception("user already exists")
            u = User(newID,userName,userPassword,isAdmin=isAdmin).dbEntry()
            userTable.insert(u)
        except Exception as e:
            exception = "Could not open database: "+str(e)
    if (exception!=None):
        raise Exception(exception)

def insertReport(userName, chalID, message, userContent, inputContent, folder, ip):
    exception = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            repTable  = dataBase.table('reports')
            report    = { "userName"    : userName,
                          "chalID"      : chalID,
                          "message"     : message,
                          "userContent" : userContent,
                          "inputContent": inputContent,
                          "ts"          : utils.GetCurrentTime(),
                          "folder"      : folder,
                          "ip"          : ip }
            repTable.insert(report)
        except:
            exception = "could not open database"
    if (exception!=None):
        raise Exception(exception)

def getAllReports():
    result = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('reports')
            q        = Query()
            rows     = tbl.all()
            result   = rows
        except Exception as e:
            print("Exception - getAllReports: "+str(e)+"\n")
    return result

def verifyUserPassword(userName, userPassword):
    retVal = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            q = Query()
            r = userTable.search(q.userName==userName)
            if len(r)>0:
                u  = r[0]
                pw = u["userPassword"]
                if bcrypt_sha256.verify(userPassword, pw):
                    retVal = u["sessionID"]
        except:
            pass
    return retVal

def getUserByID(userID):
    retVal = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            q = Query()
            r = userTable.search(q.userID==int(userID))
            if len(r)>0:
                retVal = r[0]
        except Exception as e:
            print("Exception - getUserByID: "+str(e)+"\n")
    return retVal

def getUserByUserName(userName):
    retVal = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            q = Query()
            r = userTable.search(q.userName==userName)
            if len(r)>0:
                retVal = r[0]
        except Exception as e:
            print("Exception - getUserByUserName: "+str(e)+"\n")
    return retVal


def getUserBySessionID(sessionID):
    retVal = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            q = Query()
            r = userTable.search(q.sessionID==sessionID)
            if len(r)>0:
                retVal = r[0]
        except Exception as e:
            print("Exception - getUserBySessionID: "+str(e)+"\n")
    return retVal

def isUserAdmin(userName):
    retVal = False
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            q = Query()
            r = userTable.search( (q.userName==userName) & (q.isAdmin==True) )
            if len(r)>0:
                retVal = True
        except Exception as e:
            print("Exception - isUserAdmin: "+str(e)+"\n")
    return retVal

def getUserNameByID(userID):
    userRecord = getUserByID(userID)
    return userRecord["userName"]

def getUserNameBySessionID(sessionID):
    userRecord = getUserBySessionID(sessionID)
    try:
        return (userRecord["userName"], userRecord["sessionID"])
    except:
        return None

def deleteUserID(userID):
    retVal = None
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            userTable.remove(where("userID")==int(userID))
        except Exception as e:
            print("Exception - deleteUserID: "+str(e)+"\n")
    return retVal

def updateUserIDPassword(userID,newPassword):
    exception  = None
    userRecord = getUserByID(userID)
    isAdmin    = isUserAdmin(userRecord["userName"])
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('users')
            userName  = userRecord["userName"]
            u         = User(userID,userName,newPassword,isAdmin=isAdmin).dbEntry()
            userTable.update(u,where("userID")==int(userID))
        except:
            exception = "could not open database"
    if (exception!=None):
        raise Exception(exception)

def getChalNrTimes(userName,chalID):
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            tbl       = dataBase.table('chal_nr_times')
            q         = Query()
            r         = tbl.search( (q.userName==userName) & (q.chalID==chalID) )
            return len(r)
        except Exception as e:
            print("Exception - getChalNrTimes: "+str(e)+"\n")
        return 0

def incChalNrTimes(userName,chalID, ip):
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            userTable = dataBase.table('chal_nr_times')
            row = {"userName":userName, "chalID":chalID, "ts":utils.GetCurrentTime() }
            userTable.insert(row)
        except Exception as e:
            print("Exception - incChalNrTimes: "+str(e)+"\n")

def unlockChallenge(userName,chalID,ip):
    with lock:
        try:
            dataBase    = TinyDB(dbFileName)
            unlockTable = dataBase.table('unlock')
            q           = Query()
            r           = unlockTable.search((q.chalID==chalID) & (q.userName==userName))
            if len(r)==0:
                row = { "userName" : userName,
                        "chalID"   : chalID,
                        "ts"       : utils.GetCurrentTime(),
                        "ip"       : ip }
                unlockTable.insert(row)
        except Exception as e:
            print("Exception - unlockChallenge: "+str(e)+"\n")

def getChallengeUnlocks(userName):
    unlockIDs = []
    with lock:
        try:
            dataBase    = TinyDB(dbFileName)
            unlockTable = dataBase.table('unlock')
            q           = Query()
            rows        = unlockTable.search( q.userName==userName )
            for unlock in rows:
                unlockIDs.append(unlock["chalID"])
        except Exception as e:
            print("Exception - getChallengeUnlocks: "+str(e)+"\n")
    return unlockIDs

def unlockFile(userName,chalID,fileName,unlockCode,ip):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('unlock_file')
            q        = Query()
            r        = tbl.search((q.chalID==chalID) & (q.userName==userName) & (q.unlockCode==unlockCode))
            if len(r)==0:
                row = { "userName"   : userName,
                        "chalID"     : chalID,
                        "fileName"   : fileName,
                        "unlockCode" : unlockCode,
                        "ts"         : utils.GetCurrentTime(),
                        "ip"         : ip
                      }
                tbl.insert(row)
        except Exception as e:
            print("Exception - unlockFile: "+str(e)+"\n")

def getChallengeUnlockFiles(userName):
    rList = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('unlock_file')
            q        = Query()
            rows     = tbl.search( q.userName==userName )
            rList    = rows
        except Exception as e:
            print("Exception - getChallengeUnlockFiles: "+str(e)+"\n")
    return rList

def addInteraction(userName,chalID,iType,message,folder,ip):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tLTable  = dataBase.table('timeline')
            row = { "userName"  : userName,
                    "chalID"    : chalID,
                    "ts"        : utils.GetCurrentTime(),
                    "type"      : iType,
                    "message"   : message,
                    "folder"    : folder,
                    "ip"        : ip       }
            tLTable.insert(row)
        except Exception as e:
            print("Exception - addInteraction: "+str(e)+"\n")

def addHeartBeat(userName,chalID,ip):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tLTable  = dataBase.table('heartbeat')
            row = { "userName"  : userName,
                    "chalID"    : chalID,
                    "ts"        : utils.GetCurrentTime(),
                    "ip"        : ip       }
            tLTable.insert(row)
        except Exception as e:
            print("Exception - addHeartBeat: "+str(e)+"\n")

def addHintTag(userName,chalID,hintTag,html,ip):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('hints')
            row = { "userName"  : userName,
                    "chalID"    : chalID,
                    "ts"        : utils.GetCurrentTime(),
                    "hint"      : hintTag,
                    "html"      : html,
                    "ip"        : ip       }
            tbl.insert(row)
        except Exception as e:
            print("Exception - addHintTag: "+str(e)+"\n")

#   Table: chal_feedback - records user feedback after solving a challenge
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       rate1        : (string) (Likert 1...5) : Rate this challenge"
#       rate2        : (string) (Likert 1...5) : How well could you recognize this vulnerabilitie(s) in production code?
#       rate3        : (string) (Likert 1...5) : How well did you know how to fix this problem(s) in production code?
#       ts           : (string) timestamp
#       ip           : (string) IP address of client
def addChalFeedback(userName,chalID,rate1,rate2,rate3,ip):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('chal_feedback')
            row = { "userName"  : userName,
                    "chalID"    : chalID,
                    "ts"        : utils.GetCurrentTime(),
                    "rate1"     : str(rate1),
                    "rate2"     : str(rate2),
                    "rate3"     : str(rate3),
                    "ip"        : ip       }
            tbl.insert(row)
        except Exception as e:
            print("Exception - addChalFeedback: "+str(e)+"\n")

def resetUserHints(userName):
    retVal = None
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('hints')
            tbl.remove(where("userName")==userName)
        except Exception as e:
            print("Exception - resetUserHints: "+str(e)+"\n")
    return retVal

def getUserInteractions(userName):
    userTL = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('timeline')
            q        = Query()
            rows     = tbl.search( q.userName==userName )
            userTL   = rows
        except Exception as e:
            print("Exception - getUserInteractions: "+str(e)+"\n")
    return userTL

def getUserHeartBeat(userName):
    userHB = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('timeline')
            q        = Query()
            rows     = tbl.search( q.userName==userName )
            userHB   = rows
        except Exception as e:
            print("Exception - getUserInteractions: "+str(e)+"\n")
    return userHB

def getAllUserHints(userName):
    result = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('hints')
            q        = Query()
            rows     = tbl.search( q.userName==userName )
            result   = rows
        except Exception as e:
            print("Exception - getAllUserHints: "+str(e)+"\n")
    return result

def getUserHints(userName,chalID):
    result = []
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('hints')
            q        = Query()
            rows     = tbl.search( (q.userName==userName) & (q.chalID   == chalID) )
            result   = rows
        except Exception as e:
            print("Exception - getUserHints: "+str(e)+"\n")
    return result

def getAllInteractions():
    allTL = []
    with lock:
        try:
            dataBase    = TinyDB(dbFileName)
            unlockTable = dataBase.table('timeline')
            q           = Query()
            rows        = unlockTable.all()
            allTL       = rows
        except Exception as e:
            print("Exception - getAllInteractions: "+str(e)+"\n")
    return allTL

def wasChallengeSolved(userName,chalID):
    answer = False
    with lock:
        try:
            dataBase    = TinyDB(dbFileName)
            unlockTable = dataBase.table('timeline')
            q           = Query()
            rows        = unlockTable.search( (q.userName == userName) &
                                              (q.chalID   == chalID)  &
                                              (q.type     == "SOLVE" ) )
            answer = (len(rows)>0)
        except Exception as e:
            print("Exception - wasChallengeSolved: "+str(e)+"\n")
    return answer

#   Table: chal_cache - cache files from the user interface
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       cacheDir     : (string) directory where files are cached
def addChalCache(userName,chalID,cacheDir):
    with lock:
        try:
            dataBase = TinyDB(dbFileName)
            tbl      = dataBase.table('chal_cache')
            row = { "userName"  : userName,
                    "chalID"    : chalID,
                    "cacheDir"  : cacheDir
                  }
            tbl.insert(row)
        except Exception as e:
            print("Exception - addChalCache: "+str(e)+"\n")

#   Table: chal_cache - cache files from the user interface
#       userName     : (string) userName
#       chalID       : (string) ID of the challenge
#       cacheDir     : (string) directory where files are cached
def getCacheDir(userName):
    cache = {}
    with lock:
        try:
            dataBase  = TinyDB(dbFileName)
            tbl       = dataBase.table('chal_cache')
            q         = Query()
            rows      = tbl.search(q.userName==userName)
            for r in rows:
                cache[r["chalID"]] = r["cacheDir"]
        except Exception as e:
            print("Exception - getAllInteractions: "+str(e)+"\n")
    return cache

################################################################################
################################################################################
################################################################################
################################################################################
def initBaseUsersInDatabase():
    insertUser("root",  "p@ssw0rd",  True )
    insertUser("demo",  "demo",      False)
    insertUser("demoa", "csc.1234!", True )

