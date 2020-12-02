#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#

import uuid
f0 = str(uuid.uuid4())[-5:-1]
f1 = str(uuid.uuid4())[-5:-1]
f2 = str(uuid.uuid4())[-5:-1]
f3 = str(uuid.uuid4())[-5:-1]
randomNumber = (''.join(filter(str.isdigit, str(uuid.uuid4())))) + (''.join(filter(str.isdigit, str(uuid.uuid4()))))
randomNumber = randomNumber[:10]
print( "Challenge ID:", (str(uuid.uuid4())[24:]))
print( "Unlock Code :", (str(uuid.uuid4())[28:]))
print( "Flag        : %s-%s-%s-%s" %(f0,f1,f2,f3) )
print( "Random file : func_%s" % (randomNumber) )
