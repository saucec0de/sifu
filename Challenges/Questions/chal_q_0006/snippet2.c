int is_equal(const char* a, const char* b, size_t len) {
    unsigned char result = 0;
    
    for (size_t i = 0; i < len ; i++) {
        result |= a[i] ^ b[i];
    }
    
    if (result)
        return 1;
    else
        return 0;
}
