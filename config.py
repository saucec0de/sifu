#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import utils
import yaml
import os

if os.path.isdir("/share"):
    configFileName = "/share/sifu.yaml"
else:
    configFileName = "sifu.yaml"

#################################################################
#                        Default Values                         #
#################################################################
serverPort     = 5000
serverAddr     = "127.0.0.1"
useReloader    = False
threaded       = True
debug          = True
startTools     = False
sensitiveFiles = ["./challenges.yaml", "./tags.yaml"]

# Overwrite default values with values from the configFileName
try:
    sifuCfg = utils.loadYamlFile(configFileName)
    cfg     = sifuCfg.get("Configuration",None)
    if cfg:
        serverAddr     = cfg.get("serverAddr",serverAddr)
        serverPort     = cfg.get("serverPort",serverPort)
        useReloader    = cfg.get("useReloader",useReloader)
        threaded       = cfg.get("threaded",threaded)
        debug          = cfg.get("debug",debug)
        sensitiveFiles = cfg.get("sensitiveFiles",sensitiveFiles)
        startTools     = cfg.get("startTools",startTools)
except:
    print("WARNING: could not open file "+str(configFileName))
    print("         using default values...")

