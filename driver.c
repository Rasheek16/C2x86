#include "lexer.h"  
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char filename[100]; 

    printf("Enter file name: ");
    scanf("%99s", filename);
    FILE *fptr = fopen(filename, "r");
    if (fptr == NULL) {
        perror("Error opening file");
        return EXIT_FAILURE;
    }

    // Example: pass file to your lexer function
    lexer(fptr);

    fclose(fptr);
    return EXIT_SUCCESS;
}
