from tokens import patterns
import re

def lex(data):
    try:
       
        tokens = []   

        while data:
            # Skip whitespaces
            if data[0].isspace():
                data = data.lstrip()
            else:
                match_found = False
                # Iterate through each pattern
                for token_type, pattern in patterns:
                    isMatch = re.match(pattern, data)
                    if isMatch:
                        token_value = isMatch.group(0)
                        # Check for invalid identifier case (starting with digits)
                        if token_type == "Identifier" and token_value[0].isdigit():
                            raise ValueError(f"Invalid identifier: '{token_value}' cannot start with a digit.")
                        tokens.append((token_type, token_value))
                        data = data[len(token_value):]
                        match_found = True
                        break  # Break once a match is found
                    
                if not match_found:
                    # Raise an error with the relevant information
                    raise ValueError(f'Unexpected input: {data}')
        return tokens

    except Exception as e:
        raise e
