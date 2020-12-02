#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import schema as db
import sqlite3
import pprint
import getopt
import sys
import os

def removeDatabase():
    print("Remove any previously created DB")
    try:
        os.remove(db.dbFileName)
    except Exception as e:
        pass

def createRootUser():
    print("Create root user with default password")
    try:
        db.initBaseUsersInDatabase()
    except:
        print("User already exists!")

def importTeamsFromCTFD(fileName):
    try:
        conn = sqlite3.connect(fileName)
        c    = conn.cursor()
        c.execute('SELECT name, password FROM teams')
        teams = c.fetchall()
        for team in teams:
            teamName     = team[0]
            teamPassHash = team[1]
            print("Importing team: "+teamName)
            db._insertUser(teamName,teamPassHash)
    except Exception as e:
        print("ERROR importing teams: "+str(e))

if __name__=="__main__":
    print("")
    print("(C) 2020, Siemens AG")
    print("          tiago.gasiba@gmail.com")
    print("")

    flag = False

    # check the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hxri:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if (o == "-h") or (o=="--help"):
            print("Command line arguments:")
            print("")
            print("  Argument      Parameter  Default    Description")
            print("  [-x]                                remove previously created database")
            print("  [-r]                                create root user with default password")
            print("  [-i]          STRING                import teams from CTFd sqlite3 db file")
            print("")
            sys.exit()
        elif (o == "-x"):
            removeDatabase()
            flag = True
        elif (o == "-r"):
            createRootUser()
            flag = True
        elif (o == "-i"):
            importTeamsFromCTFD(a)
            flag = True
        else:
            assert False, "unhandled option"
    if not(flag):
        print("Please select some option!")
        print("")
        sys.exit(0)
    print("Done.")

