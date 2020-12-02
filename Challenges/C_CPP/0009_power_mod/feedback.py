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
        msg = finding['msg'].lower()
        if 'division-by-zero' in msg:
            finding['tag'] = 'POWER_MOD_DIVISION_BY_ZERO'
        elif 'signed integer overflow' in msg:
            finding['tag'] = 'INCREMENTAL_2_POWER_MOD_SIGNED_OVERFLOW_'


    # write json back
    # ===============
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
