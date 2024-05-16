#include "utils.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

// #include <limits.h>

/*
#include <stddef.h>
#include <string.h>
*/

int main() {
    printf("Hello, world!\n");

    uint32_t sum = add(3, 5);
    printf("The sum of 3 and 5 is: %u\n", sum);

    return 0;
}
