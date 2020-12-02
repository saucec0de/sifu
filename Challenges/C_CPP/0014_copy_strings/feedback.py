#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#
# This will add tags to the findings in unit_test.json that were added by analyse.py
import json

FILE = './sifu_results/unit_test.json'

with open(FILE, 'r+') as f:
    # read json
    # =========
    data = json.load(f)


    # modify json
    # ===========
    # add tag to analyze.py's heap overflow finding only if checker.py labelled that finding
    # with the n=0 identifier
    for finding in data:
        if 'identifier' in finding \
           and finding['identifier'] == "all failed test suites contain n=0 test case":
            msg = finding['msg'].lower()
            if 'error' in msg and 'heap' in msg and 'buffer' in msg and 'flow' in msg:
                finding['tag'] = 'INCREMENTAL_4_COPY_STRINGS__N_EQUAL_TO_ZERO_EDGE_CASE_'
    

    # write json back
    # ===============
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
