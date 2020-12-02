import yaml
import os

### Sample Contents of config.yaml:
# 0002_info_leakage:
#   category:      Sifu C/C++
#   points:        100
#   description:   Leave no trace
#   vulnerability: CWE-14 * Information Leakage
#   directory:     Challenges/C_CPP/0002_info_leakage
#   send_dir:      true
#   file:          func_0009.c
#   fname:         func.c
#   chal_id:       c94062933919
#   root:          template
#   root_file:     chal_files.html
#   run:           ./run.py
#   flag:          f296-5420-65a9-7fc8
#   type:          c_makefile
#   disable:       false
#   feedback:      collect
#   addHeader: |
#       #define __OVERWRITE
#       #include "utils.h"
#       #include "deprecated.h"
#       #include "redirect.h"
#       #include "log.h"


localPath = os.path.join(os.path.dirname(__file__))




def FilesToJson(files, path=localPath):
    """
    returns a {filename: contents} dict for
    the given files on the given path
    """

    contents = {}

    # for multiple files, iterate over each
    if type(files)==list:
        for file in files:
            with open(os.path.join(path, file)) as f:
                contents[file]=f.read()
    
    # for just one, do the deed
    elif type(files)==str:
        with open(os.path.join(path, files)) as f:
                contents[files]=f.read()
    
    # if we're here, we screwed up
    else:
        raise TypeError('[utils_testing] excuse me')

    return contents

def fileContentsToStr(file):
    with open(file, 'r') as f:
        return f.read()

def makeIOforTest(path, inFileNames, outFileNames):
    """
    Use to generate the test parametrization lists
    ----
    Inputs: root path, expected input file names, expected output file names
    Output: lists of one dict per param set (to be used with zip when parametrizing)
        {
            in_params:
                [{inSet1_file1: inSet1_file1_contents, ..},
                 {inSet2_file2: inSet2__file2_contents}]
            out_params:
                [{outSet1_file1: outSet1_file1_contents, ..},
                 {outSet2_file2: outSet2__file2_contents}]
        }
    """
    
    test_in = []
    test_out = []

    for (dirpath, _, filenames) in os.walk(path):
        if 'tc-' in dirpath:
            files_in = {}
            files_out = {}

            for file in inFileNames:
                files_in[file] = fileContentsToStr(os.path.join(dirpath,file))
            for file in outFileNames:
                files_out[file] = fileContentsToStr(os.path.join(dirpath,file))                          

            test_in.append(files_in)
            test_out.append(files_out)
    
    return {'in_params':  test_in,
            'out_params': test_out}


if __name__=='__main__':

    # local 'testing'

    print("chalID for '0002_info_leakage' is:", chalNameToChalID('0002_info_leakage') )
    print("files and filenames:\n", getFilesForChalID(chalNameToChalID('0002_info_leakage')))
    print(FilesToJson(getFilesForChalID(chalNameToChalID('0002_info_leakage'))['fileNames'], path='../Challenges/C_CPP/0001_buffer_overflow'))
    
    print("\n\n")
    EgPathAsSeenByTests = '0002_info_leakage'
    inFiles  = ['database.json', 'func_0009.c']
    outFiles = ['ai.json', 'log.txt']

    outFiles_noLog = ['ai.json']

    print(makeIOforTest('IO/0002_info_leakage', inFiles, outFiles))
