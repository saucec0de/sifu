/*

  Copyright (c) Siemens AG, 2020
      tiago.gasiba@gmail.com

  SPDX-License-Identifier: MIT


  TODO:
    create function that allows to call the program itself such that a new test can be run from "scratch"
*/

#ifndef __GUARD_UTILS_H__
#define __GUARD_UTILS_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdbool.h>
#include <linux/limits.h>

#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>
#include <time.h>

#define TC_FAIL 0
#define TC_OK   1

extern char   *RESULTS_PATH;
extern size_t  BUFFER_SIZE;

extern int     fTIME;
extern int     timerExpire(void);
extern char *  timerErrorMessage(void);
extern char *  timerTag(void);
extern char *  timerTCName;

#define INTERNAL_ERROR(str) testResult(0,str,"internal error, call for help!","","","");

// general helper functions
int          regEx(const char *re, const char *str, char **p, int n);
char        *getReMatch(const char *re, const char *str);  // malloc
char        *b64_encode (unsigned char *src, size_t len);
int          reRunTestCase(char *param);
int          testSourceCodeContent(char *re, char *fName);
char        *getSourceCodeContent(char *re, char *fName);
void         testResult(int r, char *tc, char *desc, char *expected, char *seen, char *x);

// Functions required to handle communication with backend
void         createDirectory( const char *dirName, mode_t mode );
bool         fileExists( const char *fileName );
bool         isRegularFile(const char *filePath);
int          isDirectory(const char *dirPath);
char        *joinPath(char *pathL, char *pathR, bool separator, bool freeL, bool freeR);
bool         makeSureResultsExist(char *fileName, char *path);
bool         removeDirOrFile( const char *pathName );
bool         renamePath( const char *oldPathName, const char *newPathName );
bool         addJSONResult(char *fileName, char *jsonResult, char *path);
char        *newString(const char *s, size_t maxLen);
char        *stringCat(char *leftS, char *rightS, size_t maxLen, bool freeL, bool freeR);
char        *randomString(int len);
long         fileSize(char *fname);
int          filesAreEqual(char *file1, char *file2);

#endif
