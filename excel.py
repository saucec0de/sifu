#!/usr/bin/python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
import xlsxwriter
import challenges
import pprint
import yaml
import sys
import os
import io

sifuServer = "http://localhost:5000"
chalRows = [
     ['ChallengeID', 'Category', 'Name', 'Description', 'Key', 'Points', 'Max Tries', 'Penalty', 'Dependencies', 'File', 'Sensitivity', 'Format' ]
]

# Helpful information from here:
#   https://stackoverflow.com/questions/16393242/xlsxwriter-object-save-as-http-response-to-create-download-in-django
#   https://stackoverflow.com/questions/35710361/python-flask-send-file-stringio-blank-files
#   https://filext.com/faq/office_mime_types.html
def getExcelChallenges():
    ChallengeID = 0
    for c in challenges.allChallenges:
        ch           = challenges.allChallenges[c]
        ChallengeID  = ChallengeID + 1
        Category     = ch['category']
        Name         = ch['description']
        Description  = "Access the challenge through the following <a href='"+sifuServer+"/challenge/"+ch["chal_id"]+"'>link.</a>"
        Key          = ch['flag']
        Points       = ch['points']
        Max_Tries    = ''
        Penalty      = ''
        Dependencies = ''
        File         = ''
        Sensitivity  = 'case_insensitive'
        Format       = 'static'
        row = [ ChallengeID, Category, Name, Description, Key, Points, Max_Tries, Penalty, Dependencies, File, Sensitivity, Format ]
        chalRows.append(row)
    
    output    = io.BytesIO()
    workbook  = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Sifu")
    
    rowNr  = 0
    for row in chalRows:
        colNr = 0
        for cell in row:
            worksheet.write(rowNr, colNr, cell)
            colNr = colNr + 1
        rowNr = rowNr + 1
    
    workbook.close()
    output.seek(0)
    return output
