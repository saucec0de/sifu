int f(void) {
    printf("f was called\n");
    return 1;
}

int g(void) {
    printf("g was called\n");
    return 2;
}


int h(void) {
    printf("h was called\n");
    return 3;
}


int a = (f() + g()) + h();
