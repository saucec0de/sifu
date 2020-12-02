/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include "func.h"
#include "utils.h"
#include "redirect.h"

int timerExpire(void)         { return 2; }
char *timerErrorMessage(void) { return "This code contains undefined behaviour"; }
char *timerTag(void)          { return "INCREMENTAL_4_FUN6610374294_"; }
std::ostringstream            strCout;
extern int enableLoggingFunction;

void Test_1(void) {
    func();
    testResult(1,"TEST_100001", "make sure the function does not crash", "","","TAG000001");
}

void Test_2(void) {
    int r = 0;
    if (testSourceCodeContent("std::complex<int>[[:space:]]+nextValue;","func.cpp.pp"))
        r = 1;
    testResult(r,"TEST_100002", "nextValue variable was removed from code", "","","NO_TAG");
}

void Test_3(void) {
    int r = 0;
    if (testSourceCodeContent("std::complex<int>[[:space:]]+Values","func.cpp.pp"))
        r = 1;
    testResult(r,"TEST_100003", "Values variable was removed from code", "","","NO_TAG");
}

void Test_4(void) {
    int r = 0;
    if (testSourceCodeContent("std::complex<int>[[:space:]]+Values[[:space:]]*\\[[[:space:]]*4[[:space:]]*\\]","func.cpp.pp"))
        r = 1;
    testResult(r,"TEST_100004", "Values variable is no longer an array of size 4", "","","NO_TAG");
}

void Test_5(void) {
    int r = 0;
    if (testSourceCodeContent("^[[:space:]]*for[[:space:]]*\\(","func.cpp.pp"))
	  //int i = 0; i < 4; i++) {
        r = 1;
    testResult(r,"TEST_100005", "for loop was removed", "","","NO_TAG");
}

void Test_6(void) {
    int r = 0;
    if (testSourceCodeContent("^[[:space:]]+for[[:space:]]*\\(.+;.+<[[:space:]]*4[[:space:]]*;" ,"func.cpp.pp"))
        r = 1;
    testResult(r,"TEST_100006", "number of loop cycles has changed", "","","NO_TAG");
}

void Test_7(void) {
    std::string line;
    std::string strCompare;
    std::stringstream ss(strCout.str().c_str());
    int ii = 0;
    bool allOK = true;
    bool atLeastOneCompare = false;

    while(std::getline(ss,line,'\n')){
        atLeastOneCompare = true;
        strCompare = std::to_string(ii++);
        if (strCompare!=line) {
            allOK = false;
            break;
        }
    }
    allOK &= atLeastOneCompare;
    testResult(allOK?TC_OK:TC_FAIL,"TEST_100007", "stdout does not match expected result", "","","NO_TAG");
}

void Test_8(void) {
    int r = 0;
    if (testSourceCodeContent("(;|,|[[:space:]]|^)nextValue[[:space:]]+=[[:space:]]+Values\\[" ,"func.cpp.pp"))
        r = 1;
    testResult(r,"TEST_100008", "nextValue not being assigned a Values", "","","NO_TAG");
}

void Test_9(void) {
    int   r = 0;
    char *loopVar;
    char  searchLine[400] = {0};

    loopVar = getSourceCodeContent("^[[:space:]]*for[[:space:]]*\\([[:space:]]*.+[[:space:]](.+)[[:space:]]*=.+;.+<[[:space:]]*4[[:space:]]*;" ,"func.cpp.pp");
    if (loopVar) {
        // eliminate trailing space
        for (int ii=strlen(loopVar)-1; ii>0; ii--){
            if ( (loopVar[ii]==' ') || (loopVar[ii]=='\t') ) loopVar[ii]=0;
        }
        strcpy(searchLine, "(;|,|[[:space:]]|^)nextValue[[:space:]]*=[[:space:]]*Values[[[:space:]]*");
        strcat(searchLine, loopVar);
        strcat(searchLine, "[[:space:]]*]");
        if (testSourceCodeContent(searchLine ,"func.cpp.pp"))
            r = 1;
    } else {
        goto _end;
    }
    free(loopVar);
_end:
    testResult(r,"TEST_100009", "nextValue not assigned the correct Value", "","","NO_TAG");
}

void Log_Test(void) {
   enableLoggingFunction = 1;
   func();
   enableLoggingFunction = 0;
}

int main( void ) {
    Test_2();
    Test_3();
    Test_4();
    Test_5();
    Test_6();
    Test_8();
    Test_9();
    Log_Test();

    // cout redirection: inspired in https://stackoverflow.com/questions/4810516/c-redirecting-stdout
    std::streambuf* oldCoutStreamBuf = std::cout.rdbuf();
    std::cout.rdbuf( strCout.rdbuf() );
    Test_1(); // Note: due to undefined behaviour, this function might not return
              //       because it will be stuck in an infinite loop and will the
              //       program will exit with a timer error
    // Restore old cout.
    std::cout.rdbuf( oldCoutStreamBuf );

    Test_7();
    Log_Test();
}
