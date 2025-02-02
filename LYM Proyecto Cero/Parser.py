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
            if self.current_token()[0] == 'PIPE':          
                self.parse_pipe()
            elif self.current_token()[0] == 'PROC':
                self.parse_proc()
            else:
                raise SyntaxError(f"Unexpected token {self.current_token()}")

    def parse_pipe(self):
        self.expect('PIPE')                              # Verifica el primer token = |
        
        # Procesar la definicion de variables
        while self.current_token()[0] != 'PIPE':                   # Entra al ciclo mientras el token sea diferente a = |
            token = self.current_token()
            if token[0] == 'ID':
                self.pos+=1 # Avanza al siguiente token
                if self.current_token()[0] == 'SKIP':
                    self.expect('SKIP')  # Maneja los espacios si hay más variables
                elif self.current_token()[0] == 'PIPE':
                    break  # No más variables, salir del bucle

        self.expect('PIPE')  # Consumir el '|' de cierre
        
        
    def parse_proc(self):
        self.expect('PROC')                               # Verifica el primer token = PROC
        self.expect('ID')                                 # Nombre del procedimiento
        if self.current_token()[0] == 'LBRACKET':
           self.expect('LBRACKET') 
           self.expect('RBRACKET')
        elif self.current_token()[0] == 'COLON':
            self.expect('COLON')
            while self.current_token()[0] != 'LBRACKET':                   # Entra al ciclo mientras el token sea diferente a = |
                token = self.current_token()
                if token[0] == 'ID':
                    self.pos+=1 # Avanza al siguiente token
                    if self.current_token()[0] in ['AND', 'ANDBALLOONS']:    # Maneja los procedimientos si hay más parametros
                        self.expect(self.current_token()[0])
                        self.expect('COLON') 
                    elif self.current_token()[0] == 'LBRACKET':
                        break  # No más parametros, salir del bucle
            
        self.expect('LBRACKET')
        while self.current_token()[0] != 'RBRACKET':
            self.parse_proc_instructions()  
        self.expect('RBRACKET') 
        
    def parse_proc_instructions(self):         # Espera la logica para crear un bloque de instrucciones
        token = self.current_token()
        
        if token[0] == 'PIPE':
            self.parse_pipe()          # Procesa la creación de variables
        elif token[0] == 'ID':  # Si el token es una variable existente
            self.parse_assignment_variable()
        elif token[0]== 'COMMANDCOMPLEX':
            self.parse_command_complex()
        
    def parse_assignment_variable(self):
        self.expect('ID')
        self.expect('COLON')
        self.expect('ASSIGN')
        self.expect('NUMBER')
        self.expect('PERIOD')
        
    def parse_command_complex(self):
        self.expect('COMMANDCOMPLEX')
        self.expect('COLON')
        self.expect('NUMBER')
        self.expect('COMPLEMENT')
        self.expect('COLON')
        self.expect('CONSTANT')
        self.expect('PERIOD')            

# Prueba del Parser con un archivo de ejemplo que se encuentra en la misma carpeta del proyecto
with open('procedures_script_v2.txt', 'r') as file:
    code = file.read()
    
tokens = Lexer.lexer(code)            # Genera los tokens
parser = Parser(tokens)               # Parseamos los tokens
parser.parse()
print("Parsing completed successfully.")    #Imprimir mensaje de verificacion exitosa

