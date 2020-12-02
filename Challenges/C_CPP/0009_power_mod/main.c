/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "utilities.h"
#include "func.h"


int main(int argc, char* argv[]) {
    if (argc != 4)
        return EXIT_FAILURE;
    
    int n; // number of test cases
    if (str2int(&n, argv[1], 10) != STR2INT_SUCCESS)
        return EXIT_FAILURE;
    FILE* infile = fopen(argv[2], "r"); // where to read test cases from
    FILE* outfile = fopen(argv[3], "w"); // where to output results
    if (!infile || !outfile)
        return EXIT_FAILURE;

    // run test cases
    for (int i = 0; i < n; i++) {
        // get inputs
        // ==========
        char temp[1024];
        
        // get a
        int a;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%d", &a);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        
        // get p
        int p;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%d", &p);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        
        // get n
        int n;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%d", &n);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        
        // call test function
        // ==================
        int result = get_power_mod(a, p, n);

        // print result
        // ============
        fprintf(outfile, "RESULT: %d\n", result);
    }
    
    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


