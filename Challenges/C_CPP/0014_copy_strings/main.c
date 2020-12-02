/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
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

        // get n
        size_t n;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%zu", &n);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        // get src
        char* src;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // src is malloc'd with exact size of the input so ASan can detect overflows too
                src = malloc(len_temp + 1);
                strncpy(src, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        // allocate memory for dest
        size_t dest_size;
        if (n == 0)
            dest_size = 1;
        else
            dest_size = n;
        char* dest = malloc(dest_size);
        dest[0] = '\0';

        //  result
        // ============
        // call test function
        copy_strings(n, dest, src);
        fprintf(outfile, "RESULT: %s\n", dest);
        
        // clean up
        // ========
        free(src);
        free(dest);
    }

    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


