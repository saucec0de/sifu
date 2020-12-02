char* get_morning_greeting(bool english) {
    char english_greeting[] = "Good morning!";
    char german_greeting[] = "Guten Morgen!";
    
    if (english)
        return english_greeting;
    else
        return german_greeting;
}
