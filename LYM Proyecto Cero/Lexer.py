import re      # Importacion de la libreria de regular expressions

# Especificacion de Tokens
keywords = [
    ('EXEC', r'\bEXEC\b'),           # Simbolo de EXEC
    ('NEW', r'\bNEW\b'),             # Simbolo de NEW
    ('VAR', r'\bVAR\b'),             # Simbolo de VAR
    ('MACRO', r'\bMACRO\b'),         # Simbolo de MACRO
]

conditions = [
    ('CONDITION', r'(Blocked\?|Facing\?|zero\?|blocked\?|not)'),
]

commands = [
    ('COMMAND2', r'(turnToMy|turnToThe|walk|jump|drop|pick|grab|letGo|pop|moves|nop|safeExe)'), # Comandos compuestos de dos o mas letras
    ('COMMAND', r'[MRBCP]'),            # Comandos compuestos de una sola letra (M,R,B,C,P)
]

control_structures = [
    ('CONTROL', r'(if|then|else|while|do|repeat|od|times|per|fi)'), 
]

constants = [
    ('CONSTANT', r'(myBalloons|balloonsHere|chipsHere|roomForChips|size|myX|myY|myChips)'),
]

literals = [
    ('NUMBER', r'\b\d+\b'),             # Secuencia de uno o mas digitos
    ('ASSIGN', r'='),                   # Simbolo de Igual
    ('SEMICOLON', r';'),                # Simbolo de Punto y Coma
    ('LPAREN', r'\('),                  # Simbolo de Parentesis Derecho
    ('RPAREN', r'\)'),                  # Simbolo de Parentesis Izquierdo
    ('LBRACE', r'\{'),                  # Simbolo de Corchete Derecho
    ('RBRACE', r'\}'),                  # Simbolo de Corchete Izquierdo
    ('COMMA', r','),                    # Simbolo de Coma
    ('ID', r'[a-zA-Z_]\w*'),            # Identificadores
]

whitespace_and_misc = [
    ('NEWLINE', r'\n'),                 # Salto de linea
    ('SKIP', r'[ \t]+'),                # Reconoce espacios en blanco y tabulaciones para ignorar
    ('MISMATCH', r'.'),                 # Reconoce cualquier carácter no válido o inesperado que no coincida con ningún otro patrón definido
]

# Lista de todas las definiciones de tokens en el orden en que se evaluarán.
token_specification = keywords + conditions + commands + constants + literals + control_structures + whitespace_and_misc   

# Expresión regular que reconoce múltiples tipos de tokens al mismo tiempo.
token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

def lexer(code):
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup          # Obtiene el nombre del grupo que coincidió
        value = mo.group()           # Obtiene el valor del texto que coincidió
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'NEWLINE':
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character: {value}")
        tokens.append((kind, value))
    
    # Postprocesamiento para combinar COMMAND2 seguido de ID y para cambiar ID por CONTROL cuando sea necesario
    processed_tokens = []
    i = 0
    while i < len(tokens):
        kind, value = tokens[i]      # Desempaquetar la tupla contenida en la lista de tokens segun el indice
        
        # Verifica si el token es 'COMMAND2' y el siguiente es 'ID'
        if kind == 'COMMAND2' and i + 1 < len(tokens):
            next_kind, next_value = tokens[i + 1]
            if next_kind == 'ID':
                # Unir COMMAND2 e ID en un solo token 'ID'
                combined_value = value + next_value
                processed_tokens.append(('ID', combined_value))
                i += 2  # Saltar el siguiente token
                continue
        
        # Cambio de tipo si el token es 'ID' y corresponde a una palabra clave específica
        if kind == 'ID' and value in {'if','fi','do','od','then','else','repeat','times','per','while'}:
            kind = 'CONTROL'  # Cambiar el tipo solo si es una palabra clave específica
        
        processed_tokens.append((kind, value))
        i += 1
    
    return processed_tokens

