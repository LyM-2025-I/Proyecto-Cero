import Lexer         # Importa el modulo correspondiente al lexer

class Parser:        # Inicializacion de la clase correspondiente al Parser 
    
    def __init__(self, tokens):    
        self.tokens = tokens      # Lista de tokens producida por el lexer.
        self.pos = 0              # Posición actual en la lista de tokens. Inicialmente, es 0

    def current_token(self):      # Devuelve el token en la posición actual, si no se cumple la condicion retorna None
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def expect(self, expected_type):     
        token = self.current_token()                    # Obtiene el token actual
        if token and token[0] == expected_type:         # Verifica que el token sea del tipo correcto 
            self.pos += 1                               # Accede al siguiente token
            return token
        else:
            raise SyntaxError(f"Expected {expected_type} but got {token}")         # Mensaje de error

    def parse(self):                                    # Verifica el tipo de token e invoca segun sea el caso
        while self.current_token() is not None:
            if self.current_token()[0] == 'EXEC':          
                self.parse_exec()
            elif self.current_token()[0] == 'NEW':
                self.parse_definition()
            else:
                raise SyntaxError(f"Unexpected token {self.current_token()}")

    def parse_exec(self):
        self.expect('EXEC')                              # Verifica el primer token = EXEC
        self.expect('LBRACE')                            # Verifica el segundo token = {
        
        while self.current_token() is not None:  
            # Si el token es RBRACE, rompemos el ciclo
            if self.current_token()[0] == 'RBRACE':
                break  
            self.parse_instruction()                     # Invoca la función de instrucciones que maneja todos los casos posibles  
        if self.current_token() is None or self.current_token()[0] != 'RBRACE':
            raise SyntaxError("Expected 'RBRACE' to close EXEC block, but got end of input or unexpected token.")
        
        self.expect('RBRACE')                            # Al romper el ciclo espera = }

    def parse_definition(self):
        self.expect('NEW')                               # Verifica el primer token = NEW
        if self.current_token()[0] == 'VAR':
            self.parse_var_definition()
        elif self.current_token()[0] == 'MACRO':
            self.parse_macro_definition()
        else:
            raise SyntaxError(f"Unexpected definition type {self.current_token()}")

    def parse_var_definition(self):       # Espera la logica para crear una nueva variable
        self.expect('VAR')
        self.expect('ID')
        self.expect('ASSIGN')
        self.expect('NUMBER')
        

    def parse_macro_definition(self):     # Espera la logica para crear una nueva macro
        self.expect('MACRO')  
        self.expect('ID')     
        self.expect('LPAREN') 

        # Parsear los parámetros de la macro
        while self.current_token()[0] != 'RPAREN':                 # Entra al ciclo mientras el token sea diferente a = )
            token = self.current_token()
            if token[0] in ['ID', 'COMMAND', 'COMMAND2', 'CONSTANT']:
                self.pos += 1  # Avanza al siguiente token
                if self.current_token()[0] == 'COMMA':
                    self.expect('COMMA')  # Maneja la coma si hay más parámetros
                elif self.current_token()[0] == 'RPAREN':
                    break  # No más parámetros, salir del bucle
                else:
                    raise SyntaxError(f"Unexpected token {self.current_token()} after parameter")
            else:
                raise SyntaxError(f"Unexpected token {self.current_token()} in macro parameters")

        self.expect('RPAREN')  # Cierra los paréntesis de los parámetros

        # Espera el bloque de la macro
        self.parse_block()      # Procesa el bloque de la macro


    def parse_instruction(self):
        token = self.current_token()
        if token[0] in ['COMMAND', 'COMMAND2']:
            self.parse_command()
        elif token[0] == 'ID':
            self.parse_assignment_or_macro()
        elif token[0] == 'CONTROL':
            self.parse_control_structure()
        elif token[0] == 'SEMICOLON':
            self.pos += 1                          # Ignorar puntos y comas solitarios
        else:
            raise SyntaxError(f"Unexpected instruction {token}")

    def parse_command(self):
        token = self.current_token()
        
        if token[0] in ['COMMAND', 'COMMAND2']:
            self.pos += 1  # Avanza al siguiente token
            
            if self.current_token()[0] == 'LPAREN':
                self.expect('LPAREN')
                self.parse_params()
                self.expect('RPAREN')
            
            # Esperar el punto y coma solo si no estamos dentro de una lista de parámetros
            if self.current_token()[0] == 'SEMICOLON':
                self.expect('SEMICOLON')
        else:
            raise SyntaxError(f"Unexpected command {token}")

    def parse_params(self):
        while self.current_token()[0] != 'RPAREN':
            token = self.current_token()            
            if token[0] in ['NUMBER', 'ID', 'CONSTANT']:
                self.pos += 1  # Avanza al siguiente token
            elif token[0] in ['COMMAND', 'COMMAND2']:
                self.parse_command()  # Llama a parse_command para manejar comandos anidados como parámetros
            elif token[0] == 'COMMA':
                self.pos += 1  # Avanza al siguiente token después de la coma
            else:
                raise SyntaxError(f"Unexpected parameter {self.current_token()}")
    
    def parse_assignment_or_macro(self):
        token_type, token_value = self.current_token()

        if token_type == 'ID':  # Maneja solo ID para llamadas de macro o asignaciones
            self.pos += 1  # Avanza más allá del ID

            if self.current_token()[0] == 'ASSIGN':
                self.expect('ASSIGN')
                self.expect('NUMBER')
                self.expect('SEMICOLON')
            elif self.current_token()[0] == 'LPAREN':
                self.pos -= 1  # Retrocede para que parse_macro_call lo procese
                self.parse_macro_call()
            
            else:
                raise SyntaxError(f"Unexpected token in assignment or macro {self.current_token()}")
        
            

    def parse_macro_call(self):
        self.expect('ID')  # El nombre de la macro
        self.expect('LPAREN')
        self.parse_params()
        self.expect('RPAREN')
        self.expect('SEMICOLON')  # Termina con punto y coma

    def parse_control_structure(self):
        token = self.expect('CONTROL')
        if token[1] == 'if':
            self.parse_if_statement()
        elif token[1] == 'do':
            self.parse_do_statement()
        elif token[1] == 'repeat':
            self.parse_rep_statement()
        elif token[1] == 'while':
            self.parse_while_statement()
        else:
            raise SyntaxError(f"Unexpected control structure {token}")

    def parse_if_statement(self):
        if self.current_token()[0] == 'CONDITION':
            self.expect('CONDITION')
            self.expect('LPAREN')
            self.parse_condition()  
            self.expect('RPAREN')
            if self.current_token()[0] == 'CONTROL':
                self.expect('CONTROL')  # 'then'
                self.parse_block()
            else: 
                self.parse_block()

        else:
            self.expect('LPAREN')
            self.parse_condition()  # Analizar la condición normalmente  
            self.expect('RPAREN')
            self.expect('CONTROL')  # then
            self.parse_block()
        
        # Verificar si hay un bloque else
        if self.current_token()[0] == 'CONTROL' and self.current_token()[1] == 'else':
            self.expect('CONTROL')  # else
            self.parse_block()
        
        self.expect('CONTROL')  # fi

    def parse_rep_statement(self):
        self.expect('CONSTANT')
        self.expect('CONTROL')  # times
        self.parse_block()

        

    def parse_do_statement(self):
        self.expect('LPAREN')
        self.parse_condition()
        self.expect('RPAREN')
        self.parse_block()
        self.expect('CONTROL')  # od

    def parse_while_statement(self):
        if self.current_token()[0] == 'CONDITION':
            self.expect('CONDITION')
            self.parse_condition()  

            self.parse_block()

        else:
            self.expect('LPAREN')
            self.parse_condition()  # Analizar la condición normalmente  
            self.expect('RPAREN')
            self.expect('CONTROL')  # then
            self.parse_block()
        
        # Verificar si hay un bloque else
        if self.current_token()[0] == 'CONTROL' and self.current_token()[1] == 'else':
            self.expect('CONTROL')  # else
            self.parse_block()
        

    def parse_condition(self):
        token = self.current_token()

        if token[0] == 'not':
            self.expect('not')
            self.expect('LPAREN')
            self.parse_condition()  # Analizar la condición dentro de 'not'
            self.expect('RPAREN')

        elif token[0] == 'CONDITION':  # Blocked?, Facing?, zero?
            self.expect('CONDITION')
            self.expect('LPAREN')
            if self.current_token()[0] in ['ID', 'NUMBER', 'CONSTANT', 'COMMAND']:
                self.pos += 1
            self.expect('RPAREN')

        elif token[0] in ['ID', 'CONSTANT']:  # Una condición puede ser una variable o constante
            self.pos += 1  # Avanza al siguiente token

        else:
            raise SyntaxError(f"Unexpected condition {token}")
      
    def parse_block(self):
        self.expect('LBRACE')
        while self.current_token()[0] != 'RBRACE':
            self.parse_instruction()
        self.expect('RBRACE')

# Prueba del Parser con un archivo de ejemplo que se encuentra en la misma carpeta del proyecto
with open('code-examples.txt', 'r') as file:
    code = file.read()
    
tokens = Lexer.lexer(code)            # Genera los tokens
parser = Parser(tokens)               # Parseamos los tokens
parser.parse()
print("Parsing completed successfully.")    #Imprimir mensaje de verificacion exitosa

