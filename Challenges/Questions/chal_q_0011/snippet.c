#include <stdio.h>

int main(void) {
    int a[5];
    int sum = 0;
    
    int i = 0;
    while (i < 4) {
        a[i] = i++;
        sum += a[i];
    }

    printf("%d\n", sum);
        
    return 0;
}
