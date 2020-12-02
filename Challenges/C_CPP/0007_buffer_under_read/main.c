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
        
        // get string
        char* string;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // string is malloc'd with exact size of the input so ASan can detect overflows too
                string = malloc(len_temp + 1);
                strncpy(string, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        // get len
        int len;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%d", &len);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        
        // get c (char)
        char c;
        if (fgets(temp, sizeof temp, infile)) {
            int len_temp;
            len_temp = strcspn(temp, "\n");
            if (len_temp != 1) // input not of form "<char>\n" or "<char>\0"
                return EXIT_FAILURE;
            
            c = temp[0];
        } else {
            return EXIT_FAILURE;
        }
        
        // call test function
        // ==================
        int result = get_index_of_rightmost_char(string, len, c);

        // print result
        // ============
        fprintf(outfile, "RESULT: %d\n", result);
        
        // clean up
        // ========
        free(string);
    }
    
    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


