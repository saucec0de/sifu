char* morning_greeting;
void get_morning_greeting(bool english) {
    char english_greeting[] = "Good morning!";
    char german_greeting[] = "Guten Morgen!";
    
    if (english)
        morning_greeting = english_greeting;
    else
        morning_greeting = german_greeting;
}
