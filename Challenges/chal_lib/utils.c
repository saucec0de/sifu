/*
 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT
*/
#include <regex.h>
#include "utils.h"

#define MAX_MATCH_GROUPS 20
int       fTIME; // force time() value
char     *RESULTS_PATH  = "sifu_results";
char     *RESULTS_FNAME = "unit_test.json";
char     *timerTCName   = "TIMER_1";
size_t    BUFFER_SIZE   = 4096;
size_t    MAX_JSON_LEN  = 4096;


void timer_handler(int signum) {
    testResult(0, timerTCName, timerErrorMessage(), "","",timerTag());
    _exit(0);
    (void) signum; // avoid compiler warning
}

void __attribute__ ((constructor)) at_startup(void) {
    if (timerExpire()>0) {
        struct sigaction sa;
        sa.sa_handler = timer_handler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;
        sigaction(SIGALRM, &sa, NULL);

        struct itimerval timer;
        timer.it_value.tv_sec     = timerExpire();
        timer.it_value.tv_usec    = 0;
        timer.it_interval.tv_sec  = timerExpire();
        timer.it_interval.tv_usec = 0;
        setitimer(ITIMER_REAL, &timer, NULL);
    }
}

/*
 * This function searchs and matches a string with a POSIX Regular Expression
 *
 * ----------------+-------+--------------------------------------
 *   Type          + Param + Description
 * ----------------+-------+--------------------------------------
 *   const char *  | re    | POSIX regular expression
 *   const char *  | str   | string to match against
 *   char **       | p     | extracted groups
 *   int           | n     | maximum number of extracted groups
 * ----------------+-------+--------------------------------------
 *
 * if (!p)
 *    return value = 1 if found a match
 *                 = 0 if NOT found a match
 * if (p)
 *    return value = number of matched groups
 *    p[i] contains pointer to string of matched group i
 *    NOTE: string p[i] must be later freed by caller
 */
int regEx(const char *re, const char *str, char **p, int n) {
  regex_t    regex;
  regmatch_t pmatch[MAX_MATCH_GROUPS]; // NOTE: 20 should be more than enough!
  regoff_t   off;
  regoff_t   len;
  int        ii;
  int        nMatch = (n<MAX_MATCH_GROUPS) ? MAX_MATCH_GROUPS : n;
  int        retVal = 0;
  int        regExecRet;

  regcomp(&regex, re, REG_EXTENDED);
  regExecRet = regexec(&regex, str, MAX_MATCH_GROUPS, pmatch, 0);

  if (regExecRet) {
    // no matches found
    retVal = 0;
  } else {
    // some matches were found...
 
    if (p) {
      memset(p,0,sizeof(char*)*n);
      for (ii = 0; ii < regex.re_nsub; ii++) {
        int jj = ii + 1;
        const char *pnt = str + pmatch[jj].rm_so;              // start of match
        int l = pmatch[jj].rm_eo - pmatch[jj].rm_so; // match length
        char *tmpStr = (char *)malloc(sizeof(char)*(1+l));
        memset(tmpStr,0,1+l);
        memcpy(tmpStr,pnt,l);
        p[ii] = tmpStr;
      }
      retVal = regex.re_nsub;
    } else {
      retVal = 1;
    }
  }

  regfree(&regex);
  return retVal;
}


char *randomString(int len) {
    static int mySeed = 4444;
    char *strChars    = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-#'?!";
    char *myRandomStr = NULL;

    srand(time(NULL) * len + ++mySeed);

    if (len<1)  len=1;
    myRandomStr = (char*)malloc(sizeof(char) * (len+1));
    if (myRandomStr) {
        int jj= 0;

        for (int ii=0;ii<len;ii++) {
            jj = rand() % strlen(strChars);
            myRandomStr[ii] = strChars[jj];
        }
        myRandomStr[len] = '\0';
        return myRandomStr;
    }
    return NULL;
}

char *getReMatch(const char *re, const char *str) {
  char *p[1] = {NULL};
  int   haveMatch = 0;

  haveMatch = regEx(re,str,NULL,0);
  if (haveMatch) {
    regEx(re,str,p,1);
    return p[0];
  }
  return NULL;
}

static const char table[] = {
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
  'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
  'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
  'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
  'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
  'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
  'w', 'x', 'y', 'z', '0', '1', '2', '3',
  '4', '5', '6', '7', '8', '9', '+', '/'
};

char *b64_encode (unsigned char *src, size_t len) {
  int i = 0;
  int j = 0;
  char *enc = NULL;
  size_t size = 0;
  unsigned char buf[4];
  unsigned char tmp[3];

  enc = (char *) calloc(1,1);
  if (NULL == enc) { return NULL; }

  while (len--) {
    tmp[i++] = *(src++);
    if (3 == i) {
      buf[0] = (tmp[0] & 0xfc) >> 2;
      buf[1] = ((tmp[0] & 0x03) << 4) + ((tmp[1] & 0xf0) >> 4);
      buf[2] = ((tmp[1] & 0x0f) << 2) + ((tmp[2] & 0xc0) >> 6);
      buf[3] = tmp[2] & 0x3f;
      enc = (char *) realloc(enc, size + 4);
      for (i = 0; i < 4; ++i) {
        enc[size++] = table[buf[i]];
      }
      i = 0;
    }
  }
  if (i > 0) {
    for (j = i; j < 3; ++j) {
      tmp[j] = '\0';
    }
    buf[0] = (tmp[0] & 0xfc) >> 2;
    buf[1] = ((tmp[0] & 0x03) << 4) + ((tmp[1] & 0xf0) >> 4);
    buf[2] = ((tmp[1] & 0x0f) << 2) + ((tmp[2] & 0xc0) >> 6);
    buf[3] = tmp[2] & 0x3f;
    for (j = 0; (j < i + 1); ++j) {
      enc = (char *) realloc(enc, size + 1);
      enc[size++] = table[buf[j]];
    }
    while ((i++ < 3)) {
      enc = (char *) realloc(enc, size + 1);
      enc[size++] = '=';
    }
  }
  enc = (char *) realloc(enc, size + 1);
  enc[size] = '\0';
  return enc;
}

void testResult(int r, char *tc, char *desc, char *expected, char *seen, char *x){
    char *jsonString = NULL;
    char *_x = (char *)b64_encode((unsigned char *)expected,strlen(expected));
    char *_s = (char *)b64_encode((unsigned char *)seen,strlen(seen));

    makeSureResultsExist(RESULTS_FNAME,RESULTS_PATH);
    jsonString = newString("{ ", MAX_JSON_LEN);
    jsonString = stringCat(jsonString, "\"tc\" : \""     ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,tc                 ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,"\",\n"            ,MAX_JSON_LEN, true, false );

    jsonString = stringCat(jsonString, "\"msg\" : \""    ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,desc               ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,"\",\n"            ,MAX_JSON_LEN, true, false );

    jsonString = stringCat(jsonString, "\"expect\" : \"" ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,_x                 ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,"\",\n"            ,MAX_JSON_LEN, true, false );

    jsonString = stringCat(jsonString, "\"seen\" : \""   ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,_s                 ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,"\",\n"            ,MAX_JSON_LEN, true, false );

    jsonString = stringCat(jsonString, "\"tag\" : \""    ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,x                  ,MAX_JSON_LEN, true, false );
    jsonString = stringCat(jsonString,"\",\n"            ,MAX_JSON_LEN, true, false );

    jsonString = stringCat(jsonString, "\"result\" : "   ,MAX_JSON_LEN, true, false );
    if (r==0) {
    jsonString = stringCat(jsonString, "\"FAIL\"\n"      ,MAX_JSON_LEN, true, false );
    } else {
    jsonString = stringCat(jsonString, "\"OK\"\n"        ,MAX_JSON_LEN, true, false );
    }

    jsonString = stringCat(jsonString,"}\n"              ,MAX_JSON_LEN, true, false);

    addJSONResult(RESULTS_FNAME, jsonString, RESULTS_PATH);

    free(jsonString);

    if (r==0) {
        printf("%.20s: FAIL, %.100s [e='%s',s='%s',x='%s']\n",tc,desc,_x,_s,x);
    } else {
        printf("%.20s: OK, %.100s [e='%s',s='%s',x='%s']\n",tc,desc,_x,_s,x);
    }
    if(_x) free(_x);
    if(_s) free(_s);
    fflush(stdout);
}

int testSourceCodeContent(char *re, char *fName) {
    char    line[4096];
    int     flagFound = 0;
    FILE   *fp;
    int     lineNumber = 0;

    fp = fopen(fName,"r");
    if (!fp) return 0;

    while (!feof(fp)) {
        if (fgets(line,4095,fp)) {
            //printf("match '%s' ::: '%s'",re,line);  // for debugging purposes
            lineNumber++;
            if ( regEx(re,line,NULL,0) ) {
              //printf("OK at line %d\n",lineNumber);
              break;
            } else {
              //printf("FAIL\n");
            }
        } else return 0;
    }
_end:
    fclose(fp);
    return lineNumber;
}

char *getSourceCodeContent(char *re, char *fName) {
    char line[4096];
    int   flagFound = 0;
    FILE *fp;
    char *match;

    fp = fopen(fName,"r");
    if (!fp) return 0;

    while (!feof(fp)) {
        if (fgets(line,4095,fp)) {
            //printf("%s",line);  // for debugging purposes
            if ( regEx(re,line,NULL,0) ) {
              match = getReMatch(re,line);
              //printf("match %s at line %d\n",re,lineNumber);
              break;
            }
        } else return NULL;
    }
_end:
    fclose(fp);
    return match;
}

int reRunTestCase(char *param) {
    FILE *fp;
    char buf[1035];
    char buf2[20];
    char cmdLine[100];
    int  ret;
  
    strncpy(cmdLine,"./main ",99);
    strcat(cmdLine,param);
    fp = popen(cmdLine,"r");
    if (fp == NULL) {
      printf("Failed to run command\n" );
      return 0;
    }
  
    while (fgets(buf, sizeof(buf), fp) != NULL) {
        printf("%s", buf);
    }
  
    ret = pclose(fp);
    return ret;
}


void createDirectory( const char *dirName, mode_t mode ) {
    struct stat st = {0};

    if (stat(dirName, &st) == -1) {
        mkdir(dirName, mode);
    }
}

bool fileExists( const char *fileName ) {
    if( access( fileName, F_OK ) != -1 ) {
        return true;
    } else {
        return false;
    }
}

bool isRegularFile(const char *filePath) {
    struct stat pathStat;

    if (stat(filePath, &pathStat)!=0) {
        return false;
    }
    if (S_ISREG(pathStat.st_mode))
        return true;
    else
        return false;
}

int isDirectory(const char *dirPath) {
    struct stat pathStat;

    stat(dirPath, &pathStat);
    return S_ISDIR(pathStat.st_mode);
}

char *joinPath(char *pathL, char *pathR, bool separator, bool freeL, bool freeR) {
    char *joinPath;
    size_t totalLen = strnlen(pathL,PATH_MAX-1) + strnlen(pathR,PATH_MAX-1) + (separator?1:0) + 1;

    if (totalLen>=PATH_MAX) {
        if (freeL) free(pathL);
        if (freeR) free(pathR);
        return NULL;
    }

    joinPath  = (char *)calloc(1,sizeof(char)*totalLen);
    strncpy(joinPath,pathL,totalLen-1);
    if (separator) strncat(joinPath,"/",  totalLen - strlen(joinPath) - 1);
    strncat(joinPath,pathR,totalLen - strlen(joinPath) - 1);
    if (freeL) free(pathL);
    if (freeR) free(pathR);
    return joinPath;
}

bool makeSureResultsExist(char *fileName, char *path) {
    char *jPath = NULL;
    FILE *fp = NULL;

    // make sure the directory "path" exists
    if (!isDirectory(path)) {
        if (isRegularFile(path)) {
            printf("ERROR: '%s' is a not a directory but a file!\n",path);
            return false;
        } else {
            createDirectory(path,0700);
        }
    }

    jPath = joinPath(path,fileName,true,false,false);

    if (!fileExists(jPath)) {
        // if the results "fileName" does not exist, create an empty one
        fp = fopen(jPath,"w");
        if (fp) {
            fwrite("[\n]\n",4,1,fp);
            fclose(fp);
        }
        free(jPath);
        return true;
    }
    free(jPath);

    return true;
}

bool removeDirOrFile( const char *pathName ) {
    struct stat sb;

    if (!stat(pathName, &sb)) {
        if (S_ISDIR(sb.st_mode))
            if (0==rmdir(pathName))
                return true;
            else
                return false;
        else
            if (0==unlink(pathName))
                return true;
            else
                return false;
    } else {
        return false;
    }
}

bool renamePath( const char *oldPathName, const char *newPathName ) {
    if (0==rename(oldPathName, newPathName))
        return true;
    else
        return false;
}

bool addJSONResult(char *fileName, char *jsonResult, char *path) {
    FILE *fpOrig;
    FILE *fpDest;
    char *jPathOrig;
    char *jPathDest;
    char  buffer[BUFFER_SIZE];
    int   nLines = 0;

    if (!makeSureResultsExist(fileName,path)) {
        return false;
    }

    jPathOrig = joinPath(path,fileName,true,false,false);
    jPathDest = joinPath(jPathOrig,".new",false,false,false);

    fpOrig = fopen(jPathOrig,"r");
    fpDest = fopen(jPathDest,"w");

    while (!feof(fpOrig)) {
        if ( fgets(buffer,BUFFER_SIZE,fpOrig) ) {
            if (strcmp("]\n",buffer)==0){
                // this will be the last line in the JSON format
                if (nLines>1) {
                    fwrite(",\n",2,1,fpDest);
                }
                fwrite(jsonResult,strlen(jsonResult),1,fpDest); // dump the JSON result
                if (jsonResult[strlen(jsonResult)-1]!='\n') {
                    fwrite("\n",1,1,fpDest); // carriage return if json result does not have it
                }
                fwrite(buffer,strlen(buffer),1,fpDest); // write closing brackets
            } else if (strcmp("[]\n",buffer)==0) {  // this file contains only "[]\n"
                fwrite("[\n",2,1,fpDest);  // write opening brackets
                fwrite(jsonResult,strlen(jsonResult),1,fpDest); // dump the JSON result
                if (jsonResult[strlen(jsonResult)-1]!='\n') {
                    fwrite("\n",1,1,fpDest); // carriage return if json result does not have it
                }
                fwrite("]\n",2,1,fpDest);  // write closing brackets
            } else {
                fwrite(buffer,strlen(buffer),1,fpDest); // just copy this line
            }
            nLines++;
        }
    }
    fflush(fpDest);
    fclose(fpDest);
    fclose(fpOrig);

    if (false==removeDirOrFile(jPathOrig)) {
        free(jPathOrig);
        free(jPathDest);
        return false;
    }
    if (false==renamePath(jPathDest,jPathOrig)) {
        free(jPathOrig);
        free(jPathDest);
        return false;
    }

    free(jPathOrig);
    free(jPathDest);
    return true;
}

char *newString(const char *s, size_t maxLen) {
    char   *nStr;
    size_t len;

    len = strnlen(s,maxLen);
    if (len>=maxLen)
        return NULL;
    nStr = (char*)calloc(len+1,1);
    strncpy(nStr,s,len+1);
    return nStr;
}

char *stringCat(char *leftS, char *rightS, size_t maxLen, bool freeL, bool freeR) {
    char   *nStr;
    size_t len;

    len  = strnlen(leftS,maxLen);
    len += strnlen(rightS,maxLen) + 1;
    if (len>=maxLen)
        return NULL;
    nStr = (char*)calloc(len,1);

    strncpy(nStr,leftS,len-1);
    strncat(nStr,rightS, len-strnlen(nStr,len)-1);
    if (freeL) free(leftS);
    if (freeR) free(rightS);
    return nStr;
}

long fileSize(char *fname) {
    FILE *fp;
    long fsize;

    fp = fopen(fname,"rb");
    if(!fp) return -1;

    fseek(fp, 0L, SEEK_END);
    fsize = ftell(fp);
    fclose(fp);
    return fsize;
}

int filesAreEqual(char *file1, char *file2) {
    FILE *fp1, *fp2;
    long  fs1,  fs2;
    char  cb1,  cb2;
    int   cmp = 0;

    fs1 = fileSize(file1);
    if (fs1<0) return 0;
    fs2 = fileSize(file2);
    if (fs2<0) return 0;
    if (fs1!=fs2) return 0;

    fp1 = fopen(file1,"rb");
    if (!fp1) return 0;
    fp2 = fopen(file2,"rb");
    if (!fp2) { fclose(fp1); return 0; }

    while (!feof(fp1)) {
        fread(&cb1,1,1,fp1);
        fread(&cb2,1,1,fp2);
        if (cb1!=cb2) goto _exit;
    }
    cmp = 1;
_exit:
    fclose(fp1);
    fclose(fp2);
    return cmp;
}
