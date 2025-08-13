#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <regex.h>
#include <stdbool.h>
#include "lexer.c"



int main() {
    size_t count;
    Token *toks = lex("int main() { a=1+1;} ;", &count);

    if (toks) {
        for (size_t i = 0; i < count; i++) {
            printf("(%s, '%s')\n", toks[i].type, toks[i].value);
            free(toks[i].value);
        }
        free(toks);
    }
}
