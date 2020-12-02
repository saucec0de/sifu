#!/bin/bash
#
# Copyright (c) Siemens AG, 2020
#     tiago.gasiba@gmail.com
#
# SPDX-License-Identifier: MIT
#

LD_LIBRARY_PATH=/usr/lib32:/lib:/lib64:/lib32 \
      bwrap                           \
      --unshare-all                   \
      --ro-bind /bin /bin             \
      --ro-bind /usr /usr             \
      --ro-bind /lib /lib             \
      --ro-bind /lib64 /lib64         \
      --ro-bind /lib32 /lib32         \
      --ro-bind /usr/lib32 /usr/lib32 \
      --proc /proc                    \
      --bind `pwd` /chal              \
      --chdir /chal -- "$@"
