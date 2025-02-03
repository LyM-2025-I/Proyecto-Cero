import Lexer         # Importa el modulo correspondiente al lexer

class Parser:        # Inicializacion de la clase correspondiente al Parser 
    
    def __init__(self, tokens):    
        self.tokens = tokens      # Lista de tokens producida por el lexer.
        self.pos = 0              # Posición actual en la lista de tokens. Inicialmente, es 0
        self.variables_definidas = set()    # Almacena las variables creadas
        self.procedimientos_definidos = {}  # Almacena procedimientos con sus parámetros

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
            elif self.current_token()[0] == 'LBRACKET':
                self.parse_block()
            else:
                raise SyntaxError(f"Unexpected token {self.current_token()}")

    def parse_pipe(self):
        self.expect('PIPE')                              # Verifica el primer token = |
        
        # Procesar la definicion de variables
        while self.current_token()[0] != 'PIPE':                   # Entra al ciclo mientras el token sea diferente a = |
            token = self.current_token()
            if token[0] == 'ID':
                self.variables_definidas.add(token[1])  # Agregar la variable al registro
                self.pos+=1 # Avanza al siguiente token
                if self.current_token()[0] == 'SKIP':
                    self.expect('SKIP')  # Maneja los espacios si hay más variables
                elif self.current_token()[0] == 'PIPE':
                    break  # No más variables, salir del bucle

        self.expect('PIPE')  # Consumir el '|' de cierre
        
        
    def parse_proc(self):
        self.expect('PROC')
        proc_name = self.expect('ID')[1]

        if proc_name in self.procedimientos_definidos:
            raise SyntaxError(f"Procedure '{proc_name}' is already defined.")

        self.procedimientos_definidos[proc_name] = []  # Se registrará con parámetros después

        if self.current_token()[0] == 'LBRACKET':
            self.expect('LBRACKET')
            while self.current_token()[0] != 'RBRACKET':
                self.parse_proc_instructions()
            self.expect('RBRACKET')

        elif self.current_token()[0] == 'COLON':
            self.expect('COLON')

            while self.current_token()[0] != 'LBRACKET':
                token = self.current_token()
                if token[0] == 'ID':
                    self.procedimientos_definidos[proc_name].append(token[1])  # Guardar el parámetro
                    self.pos += 1
                    if self.current_token()[0] in ['AND', 'ANDBALLOONS']:
                        self.expect(self.current_token()[0])
                        self.expect('COLON')
                    elif self.current_token()[0] == 'LBRACKET':
                        break  # Fin de parámetros

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
        elif token[0]== 'CONTROL':
            self.parse_control()            
        
    def parse_assignment_variable(self):
        token = self.expect('ID')
        
        if token[1] not in self.variables_definidas:
            raise SyntaxError(f"Variable '{token[1]}' not defined before assignment.")
        
        self.expect('COLON')
        self.expect('ASSIGN')

        if self.current_token()[0] == 'NUMBER':
            self.expect('NUMBER')
        elif self.current_token()[0] == 'ID':
            self.expect('ID')
        else:
            raise SyntaxError(f"Expected NUMBER or Parameter but got {self.current_token()}")

        self.expect('PERIOD')

        
    def parse_command_complex(self):
        if self.current_token()[1] == "nop":
            self.expect('COMMANDCOMPLEX')
            self.expect('PERIOD')
        elif self.current_token()[1] == "goTo":
            self.expect('COMMANDCOMPLEX')
            self.expect('COLON')
            self.expect('NUMBER')
            self.expect('COMPLEMENT')
            self.expect('COLON')
            self.expect('NUMBER')
            self.expect('PERIOD')
        
        elif self.current_token()[1] == "turn" or self.current_token()[1] == "face":
            self.expect('COMMANDCOMPLEX')
            self.expect('COLON')
            self.expect('CONSTANT')
            self.expect('PERIOD')
        
        elif self.current_token()[1] == "move":
            self.expect('COMMANDCOMPLEX')
            self.expect('COLON')
            if self.current_token()[0] == 'NUMBER':
                self.expect('NUMBER')
            elif self.current_token()[0] == 'ID':
                if self.current_token()[1] not in self.variables_definidas:
                    raise SyntaxError(f"Variable '{self.current_token()[1] }' not defined before assignment.")
                else:
                    self.expect('ID')
            else:
                raise SyntaxError(f"Expected NUMBER or Variable but got {self.current_token()}")

            if self.current_token()[1] == "toThe" or self.current_token()[1] == "inDir" or self.current_token()[1] == "InDir":
                self.expect('COMPLEMENT')
                self.expect('COLON')
                self.expect('CONSTANT')

            self.expect('PERIOD')
        
        else:
            self.expect('COMMANDCOMPLEX')
            self.expect('COLON')
            if self.current_token()[0] == 'NUMBER':
                self.expect('NUMBER')
            elif self.current_token()[0] == 'ID':
                if self.current_token()[1] not in self.variables_definidas:
                    raise SyntaxError(f"Variable '{self.current_token()[1] }' not defined before assignment.")
                else:
                    self.expect('ID')
            else:
                raise SyntaxError(f"Expected NUMBER or Variable but got {self.current_token()}")

            self.expect('COMPLEMENT')
            self.expect('COLON')
            self.expect('CONSTANT')
            self.expect('PERIOD')  
    
    def parse_control(self):
        self.expect('CONTROL')   
        self.expect('COLON')
        if self.current_token()[0] != 'CONDITION':
            self.parse_block()
        elif self.current_token()[1] == "facing":
            self.expect('CONDITION')
            self.expect('COLON')
            self.expect('CONSTANT')
            self.expect('PERIOD') 
        elif self.current_token()[1] == "not":
            self.expect('CONDITION')
            self.expect('COLON')
            self.expect('CONDITION')  
            self.expect('COLON')
            self.expect('NUMBER')
            self.expect('COMPLEMENT')
            self.expect('COLON')
            self.expect('CONSTANT')
            self.expect('CONTROL')
            self.expect('COLON')
            self.parse_block()  
        else:
            self.expect('CONDITION')
            self.expect('COLON')
            self.expect('NUMBER')
            self.expect('COMPLEMENT')
            self.expect('COLON')
            self.expect('CONSTANT')
            self.expect('CONTROL')
            self.expect('COLON')
            self.parse_block()
    
    def procedureCall(self):
        proc_name = self.expect('ID')[1]

        if proc_name not in self.procedimientos_definidos:
            raise SyntaxError(f"Procedure '{proc_name}' is not defined before call.")

        self.expect('COLON')
        self.expect('NUMBER')
        self.expect('ANDBALLOONS')
        self.expect('COLON')
        self.expect('NUMBER')
        self.expect('PERIOD')

        
    def parse_block(self):
        self.expect('LBRACKET')
        if self.current_token()[0] == 'COMMANDCOMPLEX':
            self.parse_command_complex()
        if self.current_token()[0] == 'ID':
            self.procedureCall()
        self.expect('RBRACKET')
        
        

# Prueba del Parser con un archivo de ejemplo que se encuentra en la misma carpeta del proyecto
with open('prueba.txt', 'r') as file:
    code = file.read()
    
tokens = Lexer.lexer(code)            # Genera los tokens
parser = Parser(tokens)               # Parseamos los tokens
parser.parse()
print("Parsing completed successfully.")    #Imprimir mensaje de verificacion exitosa