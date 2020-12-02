int is_equal(const char* a, const char* b, size_t len) {
    unsigned char result = 0;
    unsigned char temp[MAX_LEN];
    
    for (size_t i = 0; i < len ; i++) {
        temp[i] = a[i] ^ b[i];
    }

    for (size_t i = 0; i < len; i++) {
        if (temp[i])
            return 1;
    }
        
    return 0;
}
