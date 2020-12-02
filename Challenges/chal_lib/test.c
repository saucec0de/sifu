#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>

#define MAX_MATCH_GROUPS 20

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
 
    printf("N = %ld\n",regex.re_nsub);

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

int main(void)
{
  const char *str = "Hello, World";
  char *p[5] = {NULL};
  int ii;

  ii = regEx("Hello, World",str,p,5);
  printf("RET = %d\n",ii);

  for (int ii=0; ii<5; ii++) {
    if (p[ii]) {
      printf("%d  : %s\n",ii,p[ii]);
      free(p[ii]);
    }
  }

  exit(0);
}

