char* get_morning_greeting(bool english) {
    static char english_greeting[] = "Good morning!";
    static char german_greeting[] = "Guten Morgen!";
    
    if (english)
        return english_greeting;
    else
        return german_greeting;
}
