/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include "utilities.h"
#include "func.h"


int main(int argc, char* argv[]) {
    if (argc != 4)
        return EXIT_FAILURE;
    
    int n; // number of test cases
    if (str2int(&n, argv[1], 10) != STR2INT_SUCCESS)
        return EXIT_FAILURE;

    // for this particular challenge, there should always be one test case
    if (n != 1)
        return EXIT_FAILURE;

    // input
    // for this particular challenge, we associate stdin with the input file
    if (!freopen(argv[2], "r", stdin))
        return EXIT_FAILURE;

    FILE* outfile = fopen(argv[3], "w"); // where to output results
    if (!outfile)
        return EXIT_FAILURE;


    // run test cases
    // note n is expected to be 1 here, so this will run one time
    for (int i = 0; i < n; i++) {
        // get inputs
        // ==========
        char temp[1024];
        
        // get count (how many times to call test function)
        int count;
        if (fgets(temp, sizeof temp, stdin)) {
            int ret = sscanf(temp, "%d", &count);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        if (count < 1)
            return EXIT_FAILURE;
        

        for (int j = 0; j < count; j++) {
            // call test function
            // ==================
            int result = is_letter();
            // print result
            // ============
            fprintf(outfile, "RESULT: %d\n", result);
        }

    }
    
    if (fclose(stdin) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


