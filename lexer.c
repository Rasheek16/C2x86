
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <regex.h>
#include <stdbool.h>
#include "tokens.h"

typedef struct {
    const char *type;
    char *value;
} Token;

static void lstrip(char **str) {
    while (**str && isspace((unsigned char)**str)) {
        (*str)++;
    }
}

Token *lex(const char *input, size_t *out_count) {
    const char *constant_token_types[] = {
        "Constant",
        "unsigned_int_constant",
        "long_int_constant",
        "signed_long_constant",
        "floating_point_constant"
    };
    const int constant_count = sizeof(constant_token_types) / sizeof(constant_token_types[0]);

    const char allowed_after_constant[] = {
        ';',' ','\t','\n','(',')','{','}','+','-','*','/','%',
        '=','<','>','!','&','|','~',',',':','?','e','E','.','u',
        'L','l','U',']','['
    };
    const int allowed_count = sizeof(allowed_after_constant) / sizeof(allowed_after_constant[0]);

    char *data = strdup(input);
    if (!data) {
        perror("strdup");
        exit(1);
    }
    char *ptr = data;

    Token *tokens = NULL;
    size_t token_count = 0;

    while (*ptr) {
        lstrip(&ptr);
        if (!*ptr) break;

        bool match_found = false;

        for (int i = 0; i < patterns_count; i++) {
            regex_t regex;
            if (regcomp(&regex, patterns[i].pattern, REG_EXTENDED) != 0) {
                fprintf(stderr, "Failed to compile regex: %s\n", patterns[i].pattern);
                free(data);
                return NULL;
            }

            regmatch_t match[1];
            if (regexec(&regex, ptr, 1, match, 0) == 0 && match[0].rm_so == 0) {
                int len = match[0].rm_eo;
                char *token_value = strndup(ptr, len);
                if (!token_value) {
                    perror("strndup");
                    exit(1);
                }

                if (strcmp(patterns[i].name, "Identifier") == 0 && isdigit((unsigned char)token_value[0])) {
                    fprintf(stderr, "Invalid identifier: '%s'\n", token_value);
                    free(token_value);
                    free(data);
                    return NULL;
                }

                for (int c = 0; c < constant_count; c++) {
                    if (strcmp(patterns[i].name, constant_token_types[c]) == 0) {
                        for (int k = 0; k < len; k++) {
                            char ch = token_value[k];
                            if (!isdigit((unsigned char)ch)) {
                                bool allowed = false;
                                for (int a = 0; a < allowed_count; a++) {
                                    if (ch == allowed_after_constant[a]) {
                                        allowed = true;
                                        break;
                                    }
                                }
                                if (!allowed) {
                                    fprintf(stderr, "Invalid character '%c' after constant '%s'\n",
                                            ch, token_value);
                                    free(token_value);
                                    free(data);
                                    return NULL;
                                } else {
                                    token_value[k] = '\0';
                                    len = k; 
                                }
                                break;
                            }
                        }
                        break;
                    }
                }

                tokens = realloc(tokens, (token_count + 1) * sizeof(Token));
                tokens[token_count].type = patterns[i].name;
                tokens[token_count].value = token_value;
                token_count++;

                ptr += len;
                match_found = true;
                regfree(&regex);
                break;
            }

            regfree(&regex);
        }

        if (!match_found) {
            fprintf(stderr, "Unexpected input: %s\n", ptr);
            free(data);
            for (size_t t = 0; t < token_count; t++) {
                free(tokens[t].value);
            }
            free(tokens);
            return NULL;
        }
    }

    free(data);
    *out_count = token_count;
    return tokens;
}
