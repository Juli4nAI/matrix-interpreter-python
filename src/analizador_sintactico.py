"""Analizador Sintáctico para el lenguaje de programación simple."""

from analizador_lexico import Token

class AnalizadorSintactico:

    """
     Clase AnalizadorSintactico para realizar el análisis sintáctico del código fuente.
     Esta clase contiene métodos para parsear las diferentes reglas de la gramática del lenguaje.

    """

    def __init__(self, tokens : list[Token]):
        self.tokens = tokens
        self.posicion = 0

        # Comienza apuntando al primer token de la lista.
        self.token_actual = self.tokens[self.posicion]


    # Verifica si el token actual coincide con el tipo esperado y avanza al siguiente token.
    def avanzar(self, tipo_esperado : str = None) -> Token:

        """ 
         Si se proporciona un tipo esperado, verifica que el token actual coincida con ese tipo. 
         Si no coincide, se lanza un error de sintaxis indicando el tipo esperado y el tipo encontrado, 
         junto con la ubicación del error en el código fuente (línea y columna).
        """


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

        """  
        El método parsear_programa es el punto de entrada para el análisis sintáctico. 
        Comienza verificando que el programa comience con la palabra reservada "program", seguida de un identificador (nombre del programa) 
        y un punto y coma. Luego, se parsea la sección de declaraciones, que puede contener variables, funciones, etc. 
        Después, se verifica la palabra reservada "begin" y se parsea el cuerpo del programa, que contiene las instrucciones a ejecutar. 
        Finalmente, se verifica la palabra reservada "end" y un punto para marcar el final del programa.

        """

        # Regla: <Programa> ::= “program” “id” “;” <Declaracion> “begin” <Cuerpo> “end" ".”  

        # Se espera que el programa comience con la palabra reservada "program", seguida de un identificador (nombre del programa) 
        # y un punto y coma.

        self.avanzar('tprogram')
        token_id = self.avanzar('tid')
        nombre_programa = token_id.lexema
        self.avanzar('tpuntoycoma')

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

        """Sirve para parsear la sección de declaraciones del programa, que puede contener variables, funciones, etc."""

        # <Declaracion> ::= “var” <Variables> 

        self.avanzar('tvar')
        self.parsear_variables()

        return {"tipo": "Declaracion"}


    def parsear_cuerpo(self):

        """Sirve para parsear el cuerpo del programa, que contiene las instrucciones a ejecutar."""

        # <Cuerpo> ::=  <Sentencia> ”;” <Cuerpo> | epsilon

        inicios_de_sentencia = {'tid', 'tLeer', 'tEscribir', 'tSi', 'tMientras'}

        # 1. Si el token actual es un identificador (tid) o una palabra reservada que inicia una sentencia (tLeer, tEscribir, tSi, tMientras), 
        # se parsea la sentencia, se espera un punto y coma, y luego se parsea el cuerpo recursivamente.
        if self.token_actual.tipo is not None and self.token_actual.tipo in inicios_de_sentencia:
            self.parsear_sentencia()
            self.avanzar('tpuntoycoma')
            self.parsear_cuerpo()
            return {"tipo": "Cuerpo", "vacio": False}

        # 2. Si el token actual es la palabra reservada "end" (tend), esto indica que el cuerpo está vacío (epsilon), 
        # y se devuelve un nodo de cuerpo vacío.
        if self.token_actual.tipo is not None and self.token_actual.tipo == 'tend':
            return {"tipo": "Cuerpo", "vacio": True}
        
        # 3. Si el token actual no coincide con ninguno de los casos anteriores, se lanza un error de sintaxis 
        # indicando que se encontró un token inesperado en el cuerpo del programa.
        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            raise SyntaxError(f"Error Sintáctico: Token inesperado '{token_erroneo}' en el cuerpo del programa.")


    def parsear_variables(self):

        """Sirve para parsear la sección de declaración de variables del programa."""

        # <Variables> ::= “id” “:” <Tipo1> | epsilon

        if self.token_actual is None:
            return

        # 1. Si el token actual es un identificador (tid), se consume el token, se espera un dos puntos, se parsea el tipo de la variable,
        # y se devuelve un nodo de declaración de variable con el nombre del identificador.
        if self.token_actual.tipo == 'tid':
            token_id = self.avanzar('tid')
            self.avanzar('tdospuntos')
            self.parsear_tipo1()
            return {"tipo": "DeclaracionVariable", "nombre": token_id.lexema}
        
        # 2. Si el token actual es la palabra reservada "begin" (tbegin) o "end" (tend) o el token de fin de entrada (pesos), 
        # esto indica que no hay variables declaradas (epsilon),
        if self.token_actual.tipo in ['tbegin', 'tend', 'pesos']:
            return {"tipo": "Variables", "vacio": True}
        
        # 3. Si el token actual no coincide con ninguno de los casos anteriores, se lanza un error de sintaxis 
        # indicando que se encontró un token inesperado en la sección de declaración de variables.
        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            raise SyntaxError(f"Error Sintáctico: Token inesperado '{token_erroneo}' en la sección de declaración de variables.")


    def parsear_tipo1(self):
        """Sirve para parsear el tipo de una variable declarada en el programa."""

        # <Tipo1> ::= "real" ";" <Variables>
        # <Tipo1> ::= "matrix" "[" "const" "," "const" "]" "of" "real" ";" <Variables>

        if self.token_actual.tipo is None:
            return
        
        # 1. Si el token actual es la palabra reservada "real" (treal), se consume el token, se espera un punto y coma, 
        # se parsea el resto de las variables, y se devuelve un nodo de tipo de variable con subtipo "real".
        if self.token_actual.tipo == 'treal':
            self.avanzar('treal')
            self.avanzar('tpuntoycoma')
            self.parsear_variables()
            return {"tipo": "Tipo", "subtipo": "real"}
        
        # 2. Si el token actual es la palabra reservada "matrix" (tmatrix), se consume el token, y se avanza por la secuencia de tokens
        # que definen el tipo matrix, se parsea el resto de las variables, y se devuelve un nodo de tipo de variable con subtipo "matrix".
        if self.token_actual.tipo == 'tmatrix':
            self.avanzar('tmatrix')
            self.avanzar('tabrecorch')
            self.avanzar('tconstreal')
            self.avanzar('tcoma')
            self.avanzar('tconstreal')
            self.avanzar('tcierracorch')
            self.avanzar('tof')
            self.avanzar('tnumreal')
            self.avanzar('tpuntoycoma')
            self.parsear_variables()
            return {"tipo": "Tipo", "subtipo": "matrix"}
        
        # 3. Finalmente, si el token actual no coincide con ninguno de los casos anteriores, se lanza un error de sintaxis
        # indicando que se encontró un token inesperado en la sección de tipo de variable.
        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            raise SyntaxError(f"Error Sintáctico: Token inesperado '{token_erroneo}' en la sección de tipo de variable.")


    def parsear_sentencia(self):