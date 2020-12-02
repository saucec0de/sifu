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

    // input
    FILE* infile = fopen(argv[2], "r"); // where to read test cases from
    if (!infile)
        return EXIT_FAILURE;

    // output
    // for this particular challenge, we associate stdout with the output file
    if (!freopen(argv[3], "w", stdout)) // output results sent to this file
        return EXIT_FAILURE;


    // run test cases
    for (int i = 0; i < n; i++) {
        // get inputs
        // ==========
        char temp[1024];
        
        // get user_answer
        char* user_answer;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // user_answer is malloc'd with exact size of the input so ASan can detect overflows too
                user_answer = malloc(len_temp + 1);
                strncpy(user_answer, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        // get expected_answer
        char* expected_answer;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // expected_answer is malloc'd with exact size of the input so ASan can detect overflows too
                expected_answer = malloc(len_temp + 1);
                strncpy(expected_answer, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        // get congratulations_message
        char* congratulations_message;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // congratulations_message is malloc'd with exact size of the input so ASan can detect overflows too
                congratulations_message = malloc(len_temp + 1);
                strncpy(congratulations_message, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        // get try_again_message
        char* try_again_message;
        {
            int len_temp;
            if (fgets(temp, sizeof temp, infile)) {
                len_temp = strcspn(temp, "\n");
                if (len_temp == (sizeof temp - 1)) // newline not found
                    return EXIT_FAILURE;

                temp[len_temp] = '\0'; // replace newline with \0

                // try_again_message is malloc'd with exact size of the input so ASan can detect overflows too
                try_again_message = malloc(len_temp + 1);
                strncpy(try_again_message, temp, len_temp+1);
            } else {
                return EXIT_FAILURE;
            }
        }

        //  result
        // ============
        printf("RESULT: ");
        // call test function
        check_and_give_feedback(user_answer,
                                expected_answer,
                                congratulations_message,
                                try_again_message);
        printf("\n");
        
        // clean up
        // ========
        free(user_answer);
        free(expected_answer);
        free(congratulations_message);
        free(try_again_message);
    }
    
    if (fclose(infile) == EOF)
        return EXIT_FAILURE;
    if (fclose(stdout) == EOF)
        return EXIT_FAILURE;
    
    return EXIT_SUCCESS;
}


