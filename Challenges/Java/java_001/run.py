#!/usr/bin/python3
import subprocess
import logging
import shutil
import sys
import re
import os

file_handler   = logging.FileHandler(filename='run_log.txt')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers       = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s: %(message)s',
    handlers=handlers
)

log   = logging.getLogger('RUN_PY')
print = log.info
try:
    shutil.rmtree("run_log.txt")
except:
    pass

def runInJail( cmd ):
    ret = subprocess.run(["./run_jail.sh " + cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ret

print("Start Test")

# Make sure that there is no "target" directory, i.e. java compiled code
try:
    shutil.rmtree("target")
except:
    pass
# make clean
ret = subprocess.run(["mvn package"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = ret.stdout.decode("utf-8")
print(output)

ret =runInJail("/usr/lib/jvm/java-11-openjdk-amd64/bin/java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.App")
print(ret.stdout.decode("utf-8"))
