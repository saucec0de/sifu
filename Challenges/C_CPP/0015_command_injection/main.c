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

char *switch_colour_exe_path;

/***
    Set global variable switch_colour_exe_path based
    on passed arguments.
 **/
void set_exe_path(char* colour, int expected_output);


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
        
        // get colour
        char* colour;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // colour is malloc'd with exact size of the input so ASan can detect overflows too
                colour = malloc(len_temp + 1);
                strncpy(colour, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }
        
        // get expected_output
        // in this case, checker.py also sends us the expected_output
        // so that we can set the global variable containing the binary accordingly
        int expected_output;
        if (fgets(temp, sizeof temp, infile)) {
            int ret = sscanf(temp, "%d", &expected_output);
            if (ret == EOF || ret < 1)
                return EXIT_FAILURE;
        } else {
            return EXIT_FAILURE;
        }
        

        // call test function
        // ==================
        set_exe_path(colour, expected_output);
        int result = switch_colour(colour);

        // print result
        // ============
        fprintf(outfile, "RESULT: %u\n", result);

        // clean up
        // ========
        free(colour);
    }
    
    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(outfile) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


void set_exe_path(char* colour, int expected_output) {
// if colour is not one of "red", "green" and "blue",
// then the only thing needed is that the exe chosen
// is one of the ./return1_...'s. This will
// be the case since then expected_output will be 1
    if (expected_output) {
        switch (colour[0]) {
        case 'r':
            switch_colour_exe_path = "./return1_for_red";
            break;
        case 'b':
            switch_colour_exe_path = "./return1_for_blue";
            break;
        case 'g':
            switch_colour_exe_path = "./return1_for_green";
            break;
        default:
            switch_colour_exe_path = "./return1_for_red";
        }
    } else {
        switch (colour[0]) {
        case 'r':
            switch_colour_exe_path = "./return0_for_red";
            break;
        case 'b':
            switch_colour_exe_path = "./return0_for_blue";
            break;
        case 'g':
            switch_colour_exe_path = "./return0_for_green";
            break;
        default:
            // this condition should never be reached if
            // checker.py and config.py are working correctly
            // and are passing the right inputs
            switch_colour_exe_path = "./return1_for_red";
        }
    }
}
