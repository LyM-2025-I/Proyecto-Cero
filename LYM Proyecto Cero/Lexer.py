import re      # Importacion de la libreria de regular expressions

# Especificacion de Tokens
keywords = [
    ('PIPE',  r'\|'),                 # Simbolo de |
    ('PROC', r'\bproc\b'),           # Simbolo de PROC
]

commands = [
    ('COMMANDCOMPLEX', r'(goto|move|turn|face|put|pick|jump|nop)'), # Comandos que incluyen instrucciones adicionales
    ('COMMANDCAPITAL', r'[MRCBP]'),                                 # Comandos compuestos de una sola letra mayuscula (M,R,C,B,P)
    ('COMPLEMENT', r'(with|ofType|toThe|inDir)'),                   # Comandos de complemento para los complejos
]

control_structures = [
    ('CONTROL', r'(if|then|else|while|do|for|repeat)'), 
]

constants = [
    ('CONSTANT', r'(#left|#right|#around|#north|#south|#east|#west|#balloons|#chips|#front|#back)'),
]

literals = [
    ('NUMBER', r'\b\d+\b'),             # Secuencia de uno o mas digitos
    ('ASSIGN', r'='),                   # Simbolo de Igual
    ('COLON', r':'),                    # Simbolo de dos puntos
    ('SEMICOLON', r';'),                # Simbolo de Punto y Coma
    ('PERIOD', r'\.'),                   # Simbolo de Punto 
    ('ANDBALLOONS', r'andBalloons'),    # Simbolo de andBalloons
    ('AND', r'and'),                    # Simbolo de And
    ('LPAREN', r'\('),                  # Simbolo de Parentesis Derecho
    ('RPAREN', r'\)'),                  # Simbolo de Parentesis Izquierdo
    ('LBRACE', r'\{'),                  # Simbolo de Corchete Derecho
    ('RBRACE', r'\}'),                  # Simbolo de Corchete Izquierdo
    ('RBRACKET', r'\]'),                # Simbolo de llave derecha
    ('LBRACKET', r'\['),                # Simbolo de llave izquierda
    ('COMMA', r','),                    # Simbolo de Coma
    ('ID', r'[a-zA-Z_]\w*'),            # Identificadores
]

whitespace_and_misc = [
    ('NEWLINE', r'\n'),                 # Salto de linea
    ('SKIP', r'[ \t]+'),                # Reconoce espacios en blanco y tabulaciones para ignorar
    ('MISMATCH', r'.'),                 # Reconoce cualquier carácter no válido o inesperado que no coincida con ningún otro patrón definido
]

# Lista de todas las definiciones de tokens en el orden en que se evaluarán.
token_specification = keywords + commands + constants + control_structures + literals + whitespace_and_misc   

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
        
        # Verifica si el token es 'COMMANDCOMPLEX' y el siguiente es 'ID'
        if kind == 'COMMANDCOMPLEX' and i + 1 < len(tokens):
            next_kind, next_value = tokens[i + 1]
            next_kind_posible, next_value_posible = tokens[i + 2]
            
            if next_kind == 'ID':
                # Unir COMMANDCOMPLEX e ID en un solo token 'ID'
                combined_value = value + next_value
                processed_tokens.append(('ID', combined_value))
                i += 2  # Saltar el siguiente token
                continue
            elif next_kind == 'COMMANDCAPITAL':
                 # Unir COMMANDCOMPLEX, COMMANDCAPITAL e ID en un solo token 'ID'
                combined_value = value + next_value + next_value_posible
                processed_tokens.append(('ID', combined_value))
                i += 3  # Saltar el siguiente token
                continue
                
        # Cambio de tipo si el token es 'ID' y corresponde a una palabra clave específica
        if kind == 'ID' and value in {'if','then','else','while','do','for','repeat'}:
            kind = 'CONTROL'  # Cambiar el tipo solo si es una palabra clave específica
        
        
        processed_tokens.append((kind, value))
        i += 1
    
    return processed_tokens

