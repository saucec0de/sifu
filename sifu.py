#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# TODO: Protect the request.values from "missing values"
#
from   flask         import send_from_directory
from   flask         import render_template
from   flask         import send_file
from   flask         import request
from   flask         import url_for
from   flask         import Flask
from   flask         import Response
from   flask         import redirect
from   flask         import escape
from   flask         import abort
from   jinja2        import Template
from   flask_login   import LoginManager
from   flask_login   import UserMixin
from   flask_login   import login_required
from   flask_login   import login_user
from   flask_login   import logout_user
from   flask_login   import current_user
from   flask_web_log import Log
from   faker         import Faker
from   pprint        import pprint as p
import schema        as     db
import challenges
import subprocess
import logging
import startup
import config
import atexit
import base64
import shutil
import getopt
import excel
import utils
import core
import copy
import json
import uuid
import sys
import os
import re
import io

##############################
heartBeat   = 5000
faker       = Faker()
logFileName = "sifu.log"

if os.path.isdir("/share"):
    logFileName = "/share/sifu.log"

# flask-app
app = Flask(__name__, template_folder="./templates")
# config
app.config.update(
    DEBUG        = True,
    SECRET_KEY   = '0.theRaininSpainStaysMainlyinThePlain_Yeah!.0',
    LOG_TYPE     = "CSV",
    LOG_FILENAME = "access.log"
)
Log(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

genericError = "Not permitted"

################################################################################
# Function to execute before exiting the server
def cleanUpExit():
    print("")
    if config.startTools:
        allTools = startup.getListOfTools()
        for tool in allTools:
            startup.stopTool(tool)
    print("")
    print("###############")
    print("#     Bye!    #")
    print("###############")
    print("")


################################################################################
# get remote IP Address (should work if e.g. behind NGINX)
#   https://calvin.me/forward-ip-addresses-when-using-nginx-proxy/
#   https://stackoverflow.com/questions/12770950/flask-request-remote-addr-is-wrong-on-webfaction-and-not-showing-real-user-ip
def getClientIPAddress():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

################################################################################
# landing page
@app.route('/', methods=['GET', 'POST'])
@login_required
def root():
    userName = current_user.name
    chalList = {}
    isAdmin  = db.isUserAdmin(userName)
    if not(isAdmin):
        unlockList = db.getChallengeUnlocks(userName)
        allChals   = copy.deepcopy(challenges.allChallenges) # use copy, don't change global data structure
        for c in allChals:
            if allChals[c]["chal_id"] in unlockList:
                chalList[c] = allChals[c]
                # the flag should only be shown if the challenge was solved already
                chalID = challenges.keyToID[c]
                if not(db.wasChallengeSolved(userName,chalID)):
                    chalList[c]["flag"] = ""
    else:
        chalList = challenges.allChallenges
    return render_template("welcome.html",chals=chalList, user=userName, isAdmin=isAdmin)

################################################################################
# used to serve static files, e.g. javascript, CSS, etc
@app.route('/static/<path:path>')
@login_required
def send_js(path):
    return send_from_directory('static', path)

################################################################################
# main challenge entry point
@app.route("/challenge/<chalID>")
@login_required
def challengeRoot(chalID):
    userName  = current_user.name
    ipAddress = getClientIPAddress()
    #db.addChalCache(userName,chalID,"xxx")
    if chalID in challenges.idToKey:
        cfg      = challenges.getChalConfig(chalID)
        rootFile = cfg["root_file"]
        db.unlockChallenge(userName,chalID,ipAddress)
        db.addInteraction(userName, chalID, "ENTRY", "visit challenge", "", ipAddress)
        if cfg["root"]=="template": # programming challenges
            isAdmin = db.isUserAdmin(userName)
            return render_template(rootFile,cfg=cfg, hbTimer=heartBeat, isAdmin=isAdmin)
        elif cfg["root"]=="challenge": # multiple choice questions
            chalDir = cfg["directory"]
            tplFile = os.path.join(chalDir,rootFile)
            tpl     = open(tplFile,"r").read()
            t       = Template(tpl)
            isAdmin = db.isUserAdmin(userName)
            return t.render({"cfg":cfg,"hbTimer":heartBeat,"chalID":chalID,"isAdmin":isAdmin})
        else:
            return genericError
    else:
        p(chalID)
        p(challenges.idToKey)
        db.addInteraction(userName, chalID, "ENTRY", "unkown challenge", "", ipAddress)
        return genericError

################################################################################
# unlock challenge file
@app.route("/challenge/<chalID>/unlock_file/<code>", methods=['GET'])
@login_required
def unlockChallengeFile(chalID,code):
    userName  = current_user.name
    if chalID in challenges.idToKey:
        cfg = copy.deepcopy(challenges.getChalConfig(chalID))
        allowPostUnlock = ""
        try:
            allowPostUnlock = cfg["unlock_post"].split(",")
        except:
            allowPostUnlock = []
        try:
            unlockCodes = cfg["unlock_codes"].split(",")
        except:
            unlockCodes = []
        if not(len(allowPostUnlock)==len(unlockCodes)):
            return "Inconsistent length of unlock codes"
        postUnlock = dict(zip(unlockCodes,allowPostUnlock))
        if code in postUnlock:
            # unlock code found in configuration file
            fileName = postUnlock[code]
            #print("FOUND POSTUNLOCK:",code,fileName)
            db.unlockFile(userName,chalID,fileName,code,getClientIPAddress())
        else:
            # is someone trying random unlock codes?
            return "ERROR: what are you trying to do?"
    return genericError

################################################################################
# will get/download a file from the challenge
@app.route("/challenge/<chalID>/file/<fileName>", methods=['GET','POST'])
@login_required
def challengeFile(chalID,fileName):
    userName  = current_user.name
    if chalID in challenges.idToKey:
        cfg = copy.deepcopy(challenges.getChalConfig(chalID))
    else:
        return genericError
    if request.method == 'GET':
        #print("Try allow_get...")
        try:
            allowHtml = cfg["allow_get"]
        except:
            allowHtml = ""
        allowHtml = allowHtml.split(",")
        #print("allow: ",allowHtml)
        if fileName in allowHtml:
            chalDir  = cfg["directory"]
            fileName = os.path.join(chalDir,fileName)
            return send_file(fileName)
        else:
            return genericError
    _postValuesAsDict = request.values.to_dict(flat=False)
    postValuesAsDict  = {}
    # ugly hack...
    for k in _postValuesAsDict:
        newK = "".join("_".join(k.split("[")).split("]"))
        postValuesAsDict[newK] = _postValuesAsDict[k]
    postValuesAsDict = utils.processPost(postValuesAsDict)
    limitFile = int(cfg["limitFile"]) if ("limitFile" in cfg) else 0
    db.unlockChallenge(userName,chalID,getClientIPAddress())
    if limitFile>0:
        n = db.getChalNrTimes(userName,chalID)
        if (n>=limitFile):
            return "Limit exceeded"
    db.incChalNrTimes(userName,chalID,getClientIPAddress())
    allowPost = ""
    try:
        allowPost = cfg["allow_post"]
    except:
        allowPost = ""
    allowPost = allowPost.split(",")
    #print("Try allow_post...")
    if fileName in allowPost:
        chalDir = cfg["directory"]
        tplFile = os.path.join(chalDir,fileName)
        tpl     = open(tplFile,"r").read()
        t       = Template(tpl)
        try:
          cfg["unlock_codes"] = cfg["unlock_codes"].split(",")
        except Exception as e:
          cfg["unlock_codes"] = []
        html    = t.render({"post":postValuesAsDict,"cfg":cfg, "chalID":chalID})
        #print("Rendered HTML")
        #print(html)
        #print("")
        # if we can find the flag in the HTML code, then the challenge was solved
        if re.search(cfg["flag"],html):
            db.addInteraction(userName, chalID, "SOLVE", "", "", getClientIPAddress())
        # if we can find this comment in the code, it means that we have failed the challenge
        if re.search("<!-- FAIL -->",html):
            db.addInteraction(userName, chalID, "FAIL", "", "", getClientIPAddress())
        return html
    #print("Try unlock_post...")
    allowPostUnlock = ""
    try:
        allowPostUnlock = cfg["unlock_post"].split(",")
    except:
        allowPostUnlock = []
    try:
        unlockCodes = cfg["unlock_codes"].split(",")
    except:
        unlockCodes = []
    if not(len(allowPostUnlock)==len(unlockCodes)):
        return "Inconsistent length of unlock codes"
    postUnlock = dict(zip(allowPostUnlock,unlockCodes))
    if fileName in allowPostUnlock:
        chalUnlocks = db.getChallengeUnlockFiles(userName)
        flagFound = False
        for u in chalUnlocks:
            if (u["chalID"] == chalID) and (u["unlockCode"]==postUnlock[fileName]):
                #print("FOUND")
                chalDir = cfg["directory"]
                tplFile = os.path.join(chalDir,fileName)
                tpl     = open(tplFile,"r").read()
                t       = Template(tpl)
                try:
                  cfg["unlock_codes"] = cfg["unlock_codes"].split(",")
                except Exception as e:
                  cfg["unlock_codes"] = []
                p(postValuesAsDict)
                html    = t.render({"post":postValuesAsDict,"cfg":cfg, "chalID":chalID})
                #print("Rendered HTML")
                #print(html)
                #print("")
                # if we can find the flag in the HTML code, then the challenge was solved
                if re.search(cfg["flag"],html):
                    db.addInteraction(userName, chalID, "SOLVE", "", "", getClientIPAddress())
                # if we can find this comment in the code, it means that we have failed the challenge
                if re.search("<!-- FAIL -->",html):
                    db.addInteraction(userName, chalID, "FAIL", "", "", getClientIPAddress())
                return html
        return "ERROR: a team of highly trained monkeys was just dispatched to ignore your request"
    else:
        return genericError

###############################################################################
@app.route('/challenge/<chalID>/func', methods=['GET'])
@login_required
def sendFile(chalID):
    userName  = current_user.name
    ipAddress = getClientIPAddress()
    try:
        resetChal = False
        try:
            resetChal = request.values["reset"]=="true"
        except:
            pass
        if not(chalID in challenges.idToKey):
            db.addInteraction(userName, chalID, "OOPS", "challenge not found", "", ipAddress)
            return "Not Found!"
        else:
            chalKey  = challenges.idToKey[chalID]
            chalPath = challenges.allChallenges[chalKey]["directory"]
            allChalDir = db.getCacheDir(userName)
            chalDir    = allChalDir.get(chalID,None)
            cacheFiles = False
            if None!=chalDir:
                # We have already a Cache... use it...
                #print("GET Cache: for user", userName)
                srcDir   = chalDir
            else:
                # We do not have a Cache... we will create it...
                newUUID    = str(uuid.uuid4()) # Generate new random UUID
                cacheDir   = "upload/cache/"+newUUID
                srcDir     = chalPath
                cacheFiles = True
                os.mkdir(cacheDir)
                db.addChalCache(userName,chalID,cacheDir)
                #print("GEN Cache:",cacheDir," for chalID",chalID," for user", userName)
            #print("Send Challenge Directory")
            cfg         = challenges.getChalConfig(chalID)
            files       = cfg.get("files","")
            filesToSend = []
            if not(files==""):
                filesToSend = cfg.get("files","").split(",")
                firstFile   = filesToSend[0]
                if firstFile[:2] != "./": firstFile = "./"+firstFile
            # Make sure that each file starts with "./"
            allFiles = []
            for f in filesToSend:
                if f[:2] != "./":
                    allFiles.append("./"+f)
                else:
                    allFiles.append(f)
            filesToSend = sorted(allFiles)
            fContent    = {}
            #print("filesToSend: ",filesToSend)
            for f in filesToSend:
                if resetChal:
                    # this time we need to create a cache for the files
                    _srcFile = os.path.join(chalPath,f)
                    _dstFile = os.path.join(srcDir,f)
                    #print("FROM: "+_srcFile+" TO: "+_dstFile)
                    utils.copyWithFullPath(_srcFile,_dstFile)
                if cacheFiles:
                    # this time we need to create a cache for the files
                    _srcFile = os.path.join(srcDir,  f)
                    _dstFile = os.path.join(cacheDir,f)
                    #print("FROM: "+_srcFile+" TO: "+_dstFile)
                    utils.copyWithFullPath(_srcFile,_dstFile)
                fContent[f] = utils.fileContents(os.path.join(srcDir,f))
            jstree = utils.jstreeJSON( filesToSend )
            r =  {"fcontent":fContent, "dirstruct":jstree, "workFile":firstFile}
            #print("Send Files (r):")
            #p(r)
            return r
    except Exception as e:
        userName = current_user.name
        db.addInteraction(userName, chalID, "OOPS", "error loading main challenge file", "", ipAddress)
        print("ERROR:", str(e))
        return "Error loading main challenge file"

################################################################################
# downloads the additional file that is used as user input
@app.route('/challenge/<chalID>/input_file', methods=['GET'])
@login_required
def sendInputFile(chalID):
    try:
        if not(chalID in challenges.idToKey):
            db.addInteraction(userName, chalID, "OOPS", "challenge not found", "", getClientIPAddress())
            return "Not Found!"
        else:
            chalKey  = challenges.idToKey[chalID]
            chalPath = challenges.allChallenges[chalKey]["directory"]
            chalFile = challenges.allChallenges[chalKey]["input_file"]
            #print("Send Input File: "+chalFile+" from "+chalPath)
            return send_from_directory(directory=chalPath, filename=chalFile)
    except:
        db.addInteraction(userName, chalID, "OOPS", "error loading challenge input file", "", getClientIPAddress())
        return "Error loading challenge input file"

################################################################################
# retrieves all the hints given to the user
@app.route('/challenge/<chalID>/hints', methods=['GET'])
@login_required
def getChalHints(chalID):
    if not(chalID in challenges.idToKey):
        return {"results":"Challenge not found!"}
    userName   = current_user.name
    chalHints  = db.getUserHints(userName,chalID)
    cfg        = challenges.getChalConfig(chalID)
    _heartBeat = False
    try:
        _heartBeat = False
        try:
            _heartBeat = request.values["heartbeat"]
        except:
            pass
        if _heartBeat:
            # Handle HeartBeat
            #print("HB:", chalID, userName, getClientIPAddress())
            db.addHeartBeat(userName,chalID,getClientIPAddress())
            # Handle File Cache
            hasFiles = False
            try:
                _files = json.loads(request.values["userfiles"])
                hasFiles = True
            except:
                pass
            if hasFiles:
                allChalDir = db.getCacheDir(userName)
                cacheDir   = allChalDir.get(chalID,None)
                if None!=cacheDir:
                    for f in _files:
                        fullPath = os.path.normpath(os.path.join(cacheDir,f))
                        #print("Write Cache File:",fullPath)
                        with open(fullPath,"w+") as o:
                            o.write(_files[f])
                    #p(_files)
                else:
                    print("ERROR: could not get the cache dir!!!")
    except Exception as e:
        print("Exception: "+str(e))
    hintsHtml = "<br>"
    for hint in chalHints:
        html = '<div class="box3 sb14">' + hint["html"] + '</div>'
        hintsHtml = html+hintsHtml
    hintsHtml = "<br>" + hintsHtml
    return {"hints":hintsHtml}

################################################################################
# user sends in changed files in the challenge
# the solution will be checked and a proper answer will be sent back
@app.route('/challenge/<chalID>/send_all', methods=['POST'])
@login_required
def postSendAll(chalID):
    if not(chalID in challenges.idToKey):
        return {"results":"Challenge not found!"}
    userName  = current_user.name
    userIP    = getClientIPAddress()
    db.unlockChallenge(userName,chalID,userIP)
    cfg      = copy.deepcopy(challenges.getChalConfig(chalID))
    userData = json.loads(request.values["userfiles"])
    r        = challenges.evalChalFromDirStruct(userName,userIP,chalID,userData)
    feedback = cfg.get("feedback","collect") # by default collect feedback from player on the challenge
                                             # set feedback to "skip" in challenges.yaml to skip this step
    return {"results":r["result"], "log-results":r["logger"], "solve":r["solve"], "feedback":feedback}

################################################################################
# user sends feedback for challenge
@app.route('/challenge/<chalID>/chal_feedback', methods=['POST'])
@login_required
def postChalFeedback(chalID):
    if not(chalID in challenges.idToKey):
        return {"results":"Challenge not found!"}
    userName = current_user.name
    userIP   = getClientIPAddress()
    rate1    = request.values["rate1"]
    rate2    = request.values["rate2"]
    rate3    = request.values["rate3"]
    db.addChalFeedback(userName,chalID,rate1,rate2,rate3,userIP)
    return "OK"

################################################################################
# user sends in a possible solution
# this solution will be checked and a proper answer will be sent back
@app.route('/challenge/<chalID>/send', methods=['POST'])
@login_required
def postSend(chalID):
    if not(chalID in challenges.idToKey):
        return {"results":"Challenge not found!"}
    userName  = current_user.name
    userIP    = getClientIPAddress()
    db.unlockChallenge(userName,chalID,userIP)
    cfg = copy.deepcopy(challenges.getChalConfig(chalID))
    mainFileContent  = request.values["usercontent"]
    #print("----mainFileContent----------------------")
    #print(mainFileContent)
    #print("-----------------------------------------")
    inputFileContent = ""
    try:
        inputFileContent = request.values["inputfile"]
        #print("~~~~inputFileContent~~~~~~~~~~~~~~~~~~~~~")
        #print(inputFileContent)
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    except:
        pass
    (result,d,tcDir) = challenges.evalChalFromString(userName,chalID,mainFileContent, inputFileContent)
    chalLogLines = challenges.collectChallengeEvalLogs(tcDir)
    chalLog = []
    for s in chalLogLines:
        chalLog.append( escape(s) )
    chalLog = "<br>".join(chalLog)
    failMsg    = None
    failPrio   = None
    tag        = None
    if result==False:
        try:
            for e in d:
                if d[e]["pass"]=="FAIL":
                    newPrio = int(d[e]["nr"])
                    if None==failPrio:
                        failPrio = newPrio
                        failMsg  = d[e]["msg"]
                        tag      = d[e]["x"]
                    else:
                        if newPrio < failPrio:
                            failPrio = newPrio
                            failMsg  = d[e]["msg"]
                            tag      = d[e]["x"]
            if failMsg:
                hintHtml = ""
                if tag in challenges.allTags:
                    myTag    = challenges.allTags[tag]
                    tagDesc  = myTag["description"]
                    hintHtml = tagDesc.format(**myTag)
                    db.addHintTag(userName,chalID,tag,hintHtml,getClientIPAddress())
                if False:  # Toggle this to test a new tag
                    myTag    = challenges.allTags["TEST_TAG"]
                    tagDesc  = myTag["description"]
                    hintHtml = tagDesc.format(**myTag)
                    #print("HINT:",hintHtml)
                    db.addHintTag(userName,chalID,"TEST_TAG",hintHtml,getClientIPAddress())
                db.addInteraction(userName, chalID, "FAIL", failMsg, tcDir, getClientIPAddress())
                return {"results":failMsg, "log-results":chalLog }
            else:
                msg = "Oops! please contact one of the coaches"
                db.addInteraction(userName, chalID, "OOPS", msg, tcDir, getClientIPAddress())
                return {"results":msg, "log-results":chalLog}
        except:
            pass
        #p(d)
        msg = "Oops! - where did the failed result go to?"
        db.addInteraction(userName, chalID, "OOPS", msg, tcDir, getClientIPAddress())
        return {"results":msg, "log-results":chalLog}
    else:
        flag = str(cfg["flag"])
        db.addInteraction(userName, chalID, "SOLVE", flag, tcDir, getClientIPAddress())
        return {"results":"Well done, here is your flag: " + flag, "log-results":chalLog}

################################################################################
# user sends reports something wrong with a challenge
@app.route('/challenge/<chalID>/report', methods=['POST'])
@login_required
def postReportChallenge(chalID):
    if not(chalID in challenges.idToKey):
        return {"results":"Challenge not found!"}
    userName          = current_user.name
    mainFileContent   = str( base64.b64encode(request.values["usercontent"].encode("utf-8")), "utf-8" )
    reportMessage     = request.values["message"]
    inputFilesContent = ""
    try:
        inputFilesContent = str( base64.b64encode(request.values["files"].encode("utf-8")), "utf-8" )
    except:
        pass
    db.unlockChallenge(userName,chalID,getClientIPAddress())
    db.insertReport(userName,chalID,reportMessage,mainFileContent,inputFilesContent,"",getClientIPAddress())
    return {"results":"Thank you! We will have a look into it."}


###############################################################################
# Used to implement "Sifu Apps"
@app.route('/app/<appName>', methods=['GET'])
@login_required
def sifuApp(appName):
    userName    = current_user.name
    templateDir = "app/"+appName+"/"
    baseAppDir  = "templates/"+templateDir
    print("Trying to access app: "+baseAppDir+" / "+str(userName))
    try:
        appSettings = utils.loadYamlFile(baseAppDir+"/settings.yaml")
        print("App Settings:")
        p(appSettings)
        canUseApp = core.isUserInList(userName,appSettings.get("allow",[]),db)
        if not canUseApp: abort(404)
        # Are we trying to get a file?
        fileName = request.args.get("file")
        allVars = utils.requestToDict(request)
        if fileName:
            return send_from_directory(baseAppDir, fileName)
        isAdmin  = db.isUserAdmin(userName)
        return render_template(templateDir+"index.html", user=userName, isAdmin=isAdmin, allVars=allVars)
    except:
        abort(404)
    return "Go somewhere else!"

################################################################################
# placeholder for admin tasks
@app.route("/admin")
@login_required
def adminInterface():
    userName  = current_user.name
    isAdmin   = db.isUserAdmin(userName)
    if isAdmin:
        users = db.getUsers()
        tl    = copy.deepcopy(db.getAllInteractions())
        rep   = copy.deepcopy(db.getAllReports())
        for t in tl:
            t["ts"] = t["ts"].split(".")[0] # remove milliseconds
        for r in rep:
            r["ts"] = r["ts"].split(".")[0] # remove milliseconds
        return render_template("admin.html", users=users, user=userName, timeline=tl, reports=rep, isAdmin=isAdmin)
    else:
        return genericError

################################################################################
# here an administrator can send hints to users
@app.route("/admin/user_action")
@login_required
def adminUserHint():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    if isAdmin:
        users    = db.getUsers()
        return render_template("admin_user_action.html", isAdmin=isAdmin, users=users, chals=challenges.allChallenges)
    else:
        return genericError

################################################################################
# add a hint with text to a challenge of a user
@app.route("/admin_api/user_action/add_hint", methods=['POST'])
@login_required
def adminUserActionAddHint():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    userIP   = getClientIPAddress()
    if isAdmin:
        postValuesAsDict = request.values.to_dict(flat=False)
        targetUserName   = postValuesAsDict["username"][0]
        targetChalID     = postValuesAsDict["chal_id"][0]
        targetHintText   = postValuesAsDict["hint_text"][0]
        db.addHintTag(targetUserName,targetChalID,"COACH_HINT",targetHintText,userIP)
        return "OK"
    else:
        return genericError

################################################################################
# reset all user hints
@app.route("/admin_api/user_action/reset_hints", methods=['POST'])
@login_required
def adminUserActionResetUserHints():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    userIP   = getClientIPAddress()
    if isAdmin:
        postValuesAsDict = request.values.to_dict(flat=False)
        targetUserName   = postValuesAsDict["username"][0]
        #print("RESET HINTS FOR:",targetUserName)
        db.resetUserHints(targetUserName)
        return "OK"
    else:
        return genericError

################################################################################
# Download Excel File with all challenges
@app.route("/admin_api/admin_action/excel", methods=['GET'])
@login_required
def adminAdminActionExcel():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    userIP   = getClientIPAddress()
    if isAdmin:
        xlsxFile = excel.getExcelChallenges()
        return send_file( xlsxFile,
                          as_attachment       = True,
                          attachment_filename = 'challenges.xlsx',
                          mimetype            = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        return genericError

################################################################################
# admin API: create new user
@app.route("/admin_api/create_new_user", methods=['POST'])
@login_required
def adminCreateNewUser():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    if isAdmin:
        postValuesAsDict = request.values.to_dict(flat=False)
        newUserName = postValuesAsDict["username"][0]
        newPassword = postValuesAsDict["password"][0]
        newAdmin    = (postValuesAsDict["isAdmin"][0] == "true")
        users       = db.getUsers()
        userList    = list(map( lambda uR: uR["userName"], users ))
        if not(newUserName in userList):
            try:
                db.insertUser(newUserName,newPassword,isAdmin=newAdmin)
            except:
                return "Error adding user"
            if newAdmin:
                uStr = "(admin)"
            else:
                uStr = "(normal)"
            db.addInteraction(userName, "", "ADD-USER", "Added new "+uStr+" user "+str(newUserName), "", getClientIPAddress())
            return "OK"
        else:
            return "User already exists!"
    else:
        return genericError

################################################################################
# admin API: delete user
@app.route("/admin_api/delete_user", methods=['POST'])
@login_required
def adminDeleteUser():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    if isAdmin:
        postValuesAsDict = request.values.to_dict(flat=False)
        delUserName = postValuesAsDict["username"][0]
        delUserID   = postValuesAsDict["userid"][0]
        try:
            print(delUserName, delUserID)
            db.deleteUserID(delUserID)
        except:
            return "Error while deleting user"
        db.addInteraction(userName, "", "DEL-USER", "Deleted user "+str(delUserName), "", getClientIPAddress())
        return "OK"
    else:
        return genericError

################################################################################
# admin API: change user password
@app.route("/admin_api/change_user_pass", methods=['POST'])
@login_required
def adminChangeUserPassword():
    userName = current_user.name
    isAdmin  = db.isUserAdmin(userName)
    if isAdmin:
        postValuesAsDict = request.values.to_dict(flat=False)
        theUserID   = postValuesAsDict["userid"][0]
        theUserPass = postValuesAsDict["newpassword"][0]
        try:
            db.updateUserIDPassword(theUserID, theUserPass)
        except:
            return genericError
        db.addInteraction(userName, "", "PW-USER", "Changed password of user with id "+str(theUserID), "", getClientIPAddress())
        return "OK"
    else:
        return genericError

################################################################################
# login landing page
# here the team member should login with his team member name and team password
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username  = request.form['username']
        password  = request.form['password']
        sessionID = db.verifyUserPassword(username,password)
        if None!=sessionID:
            user = db.createNewSession(username)
            login_user(user)
            db.addInteraction(username, "", "LOGIN", "", "", getClientIPAddress())
            return redirect(request.args.get("next"))
        else:
            return render_template("login.html",message="Error while logging in")
    else:
        return render_template("login.html",message="")

################################################################################
# logs the team member out
@app.route("/logout")
@login_required
def logout():
    userName  = current_user.name
    logout_user()
    db.addInteraction(userName, "", "LOGOUT", "", "", getClientIPAddress())
    db.createNewSession(userName) # this effectively invalidates the previous session
    return render_template("logout.html")

################################################################################
# Generates a random user
@app.route("/genlogin")
def genLogin():
  while True:
    newUserName = faker.first_name() + "_" + faker.last_name()
    newPassword = newUserName + "!"
    users       = db.getUsers()
    userList    = list(map( lambda uR: uR["userName"], users ))
    if not(newUserName in userList):
      try:
        db.insertUser(newUserName,newPassword,isAdmin=False)
        return render_template("genlogin.html",newUserName=newUserName,newPassword=newPassword)
      except:
        return "Internal error 0xdeadbeef"
    else:
        return "User already exists!"

################################################################################
# 401 error page
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


################################################################################
# callback to reload the user object
################################################################################
@login_manager.user_loader
def load_user(sessionID):
    try:
        (userName, userID) = db.getUserNameBySessionID(sessionID)
        return db.User(userID,userName, sessionID=sessionID)
    except:
        return None

# main function for the server
if __name__ == '__main__':
    print("")
    print("(C) 2020, Siemens AG")
    print("          tiago.gasiba@gmail.com")
    print("")

    # check the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsuU", ["help", "server=", "port=", "log=", "--sense"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opts:
        if (o == "-h") or (o=="--help"):
            print("Command line arguments:")
            print("")
            print("  Argument       Parameter  Default    Description")
            print("  [-h|--help]                          get this help")
            print("  [--port]       INT        5000       run the website on port given by INT")
            print("  [--server]     STRING     127.0.0.1  serve the webserver on the IP address given by STRING")
            print("  [--log]        STRING     sifu.log   file where to write server logs")
            print("  [-s|--sense]                         make Sifu sensitive to file changes")
            print("  [-u|-U]                              start (-U) or do not start (-u) external tools")
            print("")
            sys.exit()
        if (o == "-u"):
            config.startTools = False
        elif (o == "-U"):
            config.startTools = True
        elif (o == "-s") or (o=="--sense"):
            config.useReloader = True
        elif o == "--server":
            config.serverAddr = a
        elif o == "--log":
            logFileName = a
        elif o == "--port":
            try:
                config.serverPort = int(a)
            except:
                print("ERROR: port parameter must be an integer")
                sys.exit(2)
        else:
            assert False, "unhandled option"

    # if the database is not existing, create an empty one
    if (not(os.path.isfile(db.dbFileName))):
        db.initBaseUsersInDatabase()

    # run the main App
    app.config['TEMPLATES_AUTO_RELOAD'] = True # jinja2: do not cache templates
    # configure logging to file
    print("LOG FILE: ",logFileName)
    logging.basicConfig(filename=logFileName,level=logging.DEBUG)
    atexit.register(cleanUpExit)

    if config.startTools:
        allTools = startup.getListOfTools()
        for tool in allTools:
            startup.startTool(tool)

    # run application
    app.run(host=config.serverAddr,
            port=config.serverPort,
            debug=config.debug,                # FIXME: normal debugging would also use the reloader
            use_reloader=config.useReloader,   # FIXME?: if set to True, flask auto-reloads via watchdog reloader
            extra_files=config.sensitiveFiles, # FIXME (cont.): extra_files does nothinf if set_reloader is unset
            threaded=config.threaded)

