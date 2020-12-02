#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include "user.h"

int ConnectToServer(void) {
  char pwd[64]; // do not change this line
  if (GetPasswordFromUser(pwd, sizeof(pwd))) {
      printf("Get User Password: %s\n", pwd);
  } else {
      return 0;
  }
  memset(pwd, 0, sizeof(pwd));
  return 42;
}

int _main(void) {
  int  connHandle;

    if (connHandle=ConnectToServer()) {
        // handle connection to the server
    } else {
        // handle error
    }
  return 0; // _main: do not change this line
}
