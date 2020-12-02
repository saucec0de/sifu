/*
 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT
*/
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
bool GetPasswordFromUser(char *pwd, size_t pwd_size) {
  strncpy(pwd, "_Secret!%66.Password@", pwd_size);
  return true;
}
