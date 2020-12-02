/*
 * Read the readme.txt file for information on how to solve this challenge 
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "log.h"

void func(char *s) {
    char buffer[20];  // do not change this line

    strcpy(buffer,s);
    printf("String is: %s",buffer);
    logger("Log: %s\n",buffer);
}
