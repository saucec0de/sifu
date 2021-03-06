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
    for finding in data:
        if 'underflow' in finding['msg'].lower():
            finding['tag'] = 'INCREMENTAL_2_GET_INDEX_OF_RIGHTMOST_CHAR_'


    # write json back
    # ===============
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
