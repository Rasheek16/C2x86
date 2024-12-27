import re
from tokens import patterns

def lex(data):
    """
    Convert a source string 'data' into a list of (token_type, token_value) pairs.

    The 'patterns' list (imported from 'tokens') is expected to be a list of tuples:
    [
        ("TOKEN_TYPE", r"REGEX_PATTERN"),
        ("TOKEN_TYPE2", r"REGEX_PATTERN2"),
        ...
    ]

    1. We remove leading whitespace.
    2. For each pattern, we check if it matches the *beginning* of 'data'.
    3. If matched, we save (token_type, token_value), consume the matched substring,
       and then move on to match the next token.
    4. If no pattern matches at the current position, we raise a ValueError.
    """

    tokens = []

    while data:
        # 1) Skip leading whitespace
        data = data.lstrip()
        if not data:
            break  # If it's all whitespace, we're done.

        match_found = False

        # 2) Try each pattern to see if it matches at the start of 'data'
        for token_type, pattern in patterns:
            match_obj = re.match(pattern, data)
            if match_obj:
                # 3) Extract the matched substring
                token_value = match_obj.group(0)

                # Optional: Check for invalid identifier (digit start)
                if token_type == "Identifier" and token_value and token_value[0].isdigit():
                    raise ValueError(f"Invalid identifier: '{token_value}' cannot start with a digit.")

                # Save the token
                tokens.append((token_type, token_value))

                # "Consume" the matched substring by slicing
                data = data[len(token_value):]
                print(data)
                match_found = True
                break  # Stop checking other patterns

        if not match_found:
            # 4) No pattern matched at the current position → error
            raise ValueError(f"Unexpected input: {data}")

    return tokens
