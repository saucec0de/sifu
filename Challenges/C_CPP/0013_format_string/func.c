#include <stdio.h>

/**
   If user_answer is the exact same as expected_answer, show congratulations_message.
   Otherwise show try_again_message.
   
   Example call:
   check("Stockholm",
         "Oslo",
         "Well done! That is the right answer.",
         "No, that is not the capital of Norway. Try again!")
         
   Parameters:
   user_answer: null-terminated string
   expected_answer: null-terminated string
   congratulations_message: null-terminated string
   try_again_message: null-terminated string
 **/
void check_and_give_feedback(char* user_answer,
                             char* expected_answer,
                             char* congratulations_message,
                             char* try_again_message) {
    if (user_answer == expected_answer)
        printf(congratulations_message);
    else
        printf(try_again_message);
}
