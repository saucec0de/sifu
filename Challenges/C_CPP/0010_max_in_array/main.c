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
    FILE* infile = fopen(argv[2], "r"); // where to read test cases from
    FILE* outfile = fopen(argv[3], "w"); // where to output results
    if (!infile || !outfile)
        return EXIT_FAILURE;

    // run test cases
    for (int i = 0; i < n; i++) {
        // get inputs
        // ==========
        char temp[1024];
        
        // get len
        size_t len;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%zu", &len);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        
        // get arr
        unsigned* arr;
        arr = malloc(len*sizeof(int));
        for (size_t i = 0; i < len; i++) {
            unsigned n;
            if (fgets(temp, sizeof temp, infile)) {
                int ret = sscanf(temp, "%u", &n);
                if (ret == EOF || ret < 1)
                    return EXIT_FAILURE;
            } else {
                return EXIT_FAILURE;
            }
            arr[i] = n;
        }
        

        // call test function
        // ==================
        unsigned result = get_max_in_array(arr, len);

        // print result
        // ============
        fprintf(outfile, "RESULT: %u\n", result);

        // clean up
        // ========
        free(arr);
    }
    
    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


