#!/bin/bash

echo "Staring JAIL..."
bwrap --unshare-all           \
      --ro-bind /bin /bin     \
      --ro-bind /usr /usr     \
      --ro-bind /lib /lib     \
      --ro-bind /lib64 /lib64 \
      --ro-bind /proc /proc   \
      --bind `pwd` /chal      \
      --chdir /chal -- "$@"
