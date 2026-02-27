from AnalizadorLexico import AnalizadorLexico, Token

class AnalizadorSintactico:
    def __init__(self, tokens : list[Token]):
        self.tokens = tokens
        self.posicion = 0

        # Comienza apuntando al primer token de la lista.
        self.token_actual = self.tokens[self.posicion]


    # Verifica si el token actual coincide con el tipo esperado y avanza al siguiente token.
    def avanzar(self, tipo_esperado : str = None) -> Token:

        if tipo_esperado and self.token_actual.tipo != tipo_esperado:
            raise SyntaxError(f"Se esperaba un token de tipo '{tipo_esperado}' pero se encontró '{self.token_actual.tipo}' en línea {self.token_actual.linea}, columna {self.token_actual.columna}")

        token_consumido = self.token_actual
        self.posicion += 1

        # Si se ha alcanzado el final de la lista de tokens, se asigna un token especial de fin de entrada.
        # De lo contrario, se actualiza el token actual al siguiente token en la lista.
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = Token(tipo='pesos', lexema='$', linea=-1, columna=-1)

        return token_consumido



    # ##########################################
    #           REGLAS DE GRAMATICA
    # ##########################################


    def parsear_programa(self):

       # Regla: <Programa> ::= “program” “id” “;” <Declaracion> “begin” <Cuerpo> “end" ".”

        # Se espera que el programa comience con la palabra reservada "program", seguida de un identificador (nombre del programa) 
        # y un punto y coma.
        self.avanzar('program')
        Token.id = self.avanzar('tid')
        nombre_programa = Token.id.lexema
        self.avanzar(';')

        # Luego se parsea la sección de declaraciones, que puede contener variables, funciones, etc.
        self.parsear_declaracion()

        self.avanzar('tbegin')

        # Finalmente, se parsea el cuerpo del programa, que contiene las instrucciones a ejecutar.
        self.parsear_cuerpo()

        self.avanzar('tend')
        self.avanzar('tpunto')

        print(f"✅ Análisis sintáctico exitoso. Programa: '{nombre_programa}'")
        
        # Aquí devolveremos el Árbol de Sintaxis Abstracta (AST)
        return {"tipo": "Programa", "nombre": nombre_programa}
    

    def parsear_declaracion(self):
        # <Declaracion> ::= “var” <Variables> 

        self.avanzar('tvar')
        self.parsear_variables()

        return {"tipo": "Declaracion"}

    def parsear_cuerpo(self):
        # <Cuerpo> ::=  <Sentencia> ”;” <Cuerpo>  

        self.parsear_sentencia()
        self.avanzar('tpuntoycoma')
        self.parsear_cuerpo()

        return {"tipo": "Cuerpo"}
