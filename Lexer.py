def lexer(code):
    tokens = []
    i = 0
    
    while i < len(code):
        char = code[i]
        
        if char == '|':
            tokens.append(('PIPE', '|'))
            i += 1
        elif code[i:i+4] == 'proc' and (i+4 == len(code) or not code[i+4].isalnum()):
            tokens.append(('PROC', 'proc'))
            i += 4
        elif code[i:i+5] in {'goto', 'move', 'turn', 'face', 'put', 'pick', 'jump', 'nop', 'goTo'}:
            tokens.append(('COMMANDCOMPLEX', code[i:i+5]))
            i += len(code[i:i+5])
        elif char in {'M', 'R', 'C', 'B', 'P'}:
            tokens.append(('COMMANDCAPITAL', char))
            i += 1
        elif code[i:i+6] in {'with', 'ofType', 'toThe', 'inDir', 'InDir'}:
            tokens.append(('COMPLEMENT', code[i:i+6]))
            i += len(code[i:i+6])
        elif code[i:i+6] in {'if', 'then', 'else', 'while', 'do', 'for', 'repeat'}:
            tokens.append(('CONTROL', code[i:i+6]))
            i += len(code[i:i+6])
        elif code[i:i+7] in {'facing', 'canPut', 'canPick', 'canMove', 'canJump', 'not'}:
            tokens.append(('CONDITION', code[i:i+7]))
            i += len(code[i:i+7])
        elif char == '#':
            constant = '#'
            i += 1
            while i < len(code) and code[i].isalpha():
                constant += code[i]
                i += 1
            if constant in {'#left', '#right', '#around', '#north', '#south', '#east', '#west', '#balloons', '#chips', '#front', '#back'}:
                tokens.append(('CONSTANT', constant))
            else:
                raise RuntimeError(f"Unexpected constant: {constant}")
        elif char.isdigit():
            num = ''
            while i < len(code) and code[i].isdigit():
                num += code[i]
                i += 1
            tokens.append(('NUMBER', int(num)))
        elif char in {'=', ':', ';', '.', '(', ')', '{', '}', '[', ']'}:
            token_types = {'=': 'ASSIGN', ':': 'COLON', ';': 'SEMICOLON', '.': 'PERIOD',
                           '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
                           '[': 'LBRACKET', ']': 'RBRACKET'}
            tokens.append((token_types[char], char))
            i += 1
        elif code[i:i+11] == 'andBalloons':
            tokens.append(('ANDBALLOONS', 'andBalloons'))
            i += 11
        elif code[i:i+3] == 'and':
            tokens.append(('AND', 'and'))
            i += 3
        elif char.isspace() or char == ',':
            i += 1
        elif char.isalpha() or char == '_':
            identifier = ''
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                identifier += code[i]
                i += 1
            if identifier in {'if', 'then', 'else', 'while', 'do', 'for', 'repeat'}:
                tokens.append(('CONTROL', identifier))
            elif identifier in {'goto', 'move', 'turn', 'face', 'put', 'pick', 'jump', 'nop', 'goTo'}:
                tokens.append(('COMMANDCOMPLEX', identifier))
            elif identifier in {'with', 'ofType', 'toThe', 'inDir', 'InDir'}:
                tokens.append(('COMPLEMENT', identifier))
            else:
                tokens.append(('ID', identifier))
        else:
            raise RuntimeError(f"Unexpected character: {char}")
    
    # Postprocesamiento para unir COMMANDCOMPLEX con ID o COMMANDCAPITAL
    processed_tokens = []
    i = 0
    while i < len(tokens):
        kind, value = tokens[i]
        if kind == 'COMMANDCOMPLEX' and i + 1 < len(tokens) and tokens[i + 1][0] == 'ID':
            combined_value = value + tokens[i + 1][1]
            processed_tokens.append(('ID', combined_value))
            i += 2
        elif kind == 'COMMANDCOMPLEX' and i + 2 < len(tokens) and tokens[i + 1][0] == 'COMMANDCAPITAL' and tokens[i + 2][0] == 'ID':
            combined_value = value + tokens[i + 1][1] + tokens[i + 2][1]
            processed_tokens.append(('ID', combined_value))
            i += 3
        else:
            processed_tokens.append((kind, value))
            i += 1
    
    return processed_tokens
