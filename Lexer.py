
from Tokens import patterns 
import re 


def lex(data):
    tokens=[]
    while data:
        if data[0].isspace():
            data=data.lstrip()
            
        else:
            match_found = False
            for token_type , pattern in patterns:
                print(token_type,pattern)
                isMatch = re.match(pattern,data)
                print(isMatch)
                if isMatch:
                    token_value = isMatch.group(0)
                    tokens.append((token_type,token_value))
                    match_found = True 
                    data = data[len(token_value):]
            if not match_found:
                raise ValueError('Unexpected inputs')
    return tokens 



