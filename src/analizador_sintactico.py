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
        declaraciones =self.parsear_declaracion()

        self.avanzar('tbegin')

        # Finalmente, se parsea el cuerpo del programa, que contiene las instrucciones a ejecutar.
        cuerpo = self.parsear_cuerpo()

        self.avanzar('tend')
        self.avanzar('tpunto')

        print(f"✅ Análisis sintáctico exitoso. Programa: '{nombre_programa}'")
        
        # Aquí devolveremos el Árbol de Sintaxis Abstracta (AST)
        return {"tipo": "Programa", "nombre": nombre_programa, "declaraciones": declaraciones, "cuerpo": cuerpo}


    def parsear_declaracion(self):

        """Sirve para parsear la sección de declaraciones del programa, que puede contener variables, funciones, etc."""

        # <Declaracion> ::= “var” <Variables> 

        self.avanzar('tvar')
        self.parsear_variables()

        return {"tipo": "Declaracion"}


    def parsear_cuerpo(self):
        """
        Sirve para parsear un bloque de sentencias agrupadas en el cuerpo del programa,
        un if o un while. Consume los puntos y comas separadores.
        """
        sentencias = []
        
        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba al menos una sentencia en el cuerpo.")
            
        # 1. Parseamos la primera sentencia (siempre es obligatoria)
        sentencias.append(self.parsear_sentencia())
        
        # 2. El bucle devorador: Mientras haya un punto y coma, seguimos leyendo sentencias
        while self.token_actual is not None and self.token_actual.tipo == 'tpuntoycoma':
            self.avanzar('tpuntoycoma')
            
            # ESCUDO: Si después del ';' viene el final del bloque ('end') o un 'sino', 
            # significa que ese ';' era el último y no hay más sentencias para leer. Cortamos.
            if self.token_actual is not None and self.token_actual.tipo in ['tend', 'tSino']:
                break
                
            # Si no era el final, agregamos la siguiente sentencia a la lista
            sentencias.append(self.parsear_sentencia())
            
        return sentencias


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

        if self.token_actual is None:
            return
        
        # 1. Si el token actual es la palabra reservada "real" (treal), se consume el token, se espera un punto y coma, 
        # se parsea el resto de las variables, y se devuelve un nodo de tipo de variable con subtipo "real".
        if self.token_actual.tipo == 'tnumreal':
            self.avanzar('tnumreal')
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
        """Sirve para parsear una sentencia dentro del cuerpo del programa."""
        # <Sentencia> ::= <Asignación> | <Lectura> | <Escribir> | <If> | <While>

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia pero se encontró el fin de archivo.")

        # 1. Asignación
        if self.token_actual.tipo == 'tid':
            return self.parsear_asignacion()
        
        # 2. Lectura
        elif self.token_actual.tipo == 'tLeer':
            return self.parsear_lectura()

        # 3. Escritura
        elif self.token_actual.tipo == 'tEscribir':
            return self.parsear_escritura()

        # 4. Condicional If
        elif self.token_actual.tipo == 'tSi':
            return self.parsear_if()

        # 5. Ciclo While
        elif self.token_actual.tipo == 'tMientras':
            return self.parsear_while()

        # 6. Error
        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            linea = self.token_actual.linea if self.token_actual else "Desconocida"
            raise SyntaxError(f"Error Sintáctico en la linea {linea}: Token inesperado '{token_erroneo}' al intentar parsear una sentencia.")
        
    
    def parsear_lectura(self):

        """Sirve para parsear una sentencia de lectura dentro del cuerpo del programa."""

        # <Lectura> ::= “leer” “(“ “constCadena” “,” “id” “)”

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia de lectura pero se encontró el fin de archivo.")
        
        self.avanzar('tLeer')
        self.avanzar('tabreparent')
        token_cadena = self.avanzar('tconstcadena')
        self.avanzar('tcoma')
        token_id = self.avanzar('tid')
        self.avanzar('tcierraparent')
        return {"tipo": "Lectura", "mensaje": token_cadena.lexema, "variable": token_id.lexema}
    

    def parsear_escritura(self):

        """Sirve para parsear una sentencia de escritura dentro del cuerpo del programa."""

        # <Escribir> ::= “escribir” “(“ <Lista> “)”

        if self.token_actual.tipo is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia de escritura pero se encontró el fin de archivo.")
        
        self.avanzar('tEscribir')
        self.avanzar('tabreparent')
        elementos_lista = self.parsear_lista()
        self.avanzar('tcierraparent')
        return {"tipo": "Escritura", "elementos": elementos_lista}


    def parsear_lista(self):

        """
        Regla original: <Lista> ::= "constCadena" <Repetir>       <Lista> ::= <ExpArit> <Repetir>
        Regla optimizada (EBNF): <Lista> ::= <Elemento> { "," <Elemento> }
        Un elemento puede ser una cadena de texto o una expresión aritmética.
        """

        elementos = []
        
        # 1. Parseamos el primer elemento
        elementos.append(self._parsear_elemento_lista())
        
        # 2. El equivalente a <Repetir>: Mientras haya una coma, seguimos leyendo elementos
        while self.token_actual is not None and self.token_actual.tipo == 'tcoma':
            self.avanzar('tcoma')
            elementos.append(self._parsear_elemento_lista())
            
        return elementos


    def _parsear_elemento_lista(self):

        """Método auxiliar para saber si leemos un texto o una expresión matemática"""
        
        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba un elemento en la lista, pero se encontró el fin del archivo.")
            
        # Si es una cadena entre comillas, la consumimos directamente
        if self.token_actual.tipo == 'tconstcadena':
            token_cadena = self.avanzar('tconstcadena')
            return {"tipo": "Cadena", "valor": token_cadena.lexema}
            
        # Si no es cadena, por descarte tiene que ser una variable, número o fórmula (ExpArit)
        else:
            return self.parsear_exp_arit()
        

    def parsear_while(self):

        """Sirve para parsear una sentencia condicional while dentro del cuerpo del programa."""

        # <While> ::= “mientras” <Cond> “hacer” “begin” <Cuerpo> “end”

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia while pero se encontró el fin de archivo.")
        
        self.avanzar('tMientras')
        condicion = self.parsear_cond()
        self.avanzar('tHacer')
        self.avanzar('tbegin')
        cuerpo_while = self.parsear_cuerpo()
        self.avanzar('tend')
        return {"tipo": "While", "condicion": condicion, "cuerpo": cuerpo_while}
    
    
    def parsear_if(self):

        """Sirve para parsear una sentencia condicional if dentro del cuerpo del programa."""

        #<If> ::= “si” <Cond> “entonces” “begin” <Cuerpo> “end” <If’>
        #<If’> ::= “sino” “begin” <Cuerpo> “end” “;” | epsilon

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia if pero se encontró el fin de archivo.")
        
        self.avanzar('tSi')
        condicion = self.parsear_cond()
        self.avanzar('tEntonces')
        self.avanzar('tbegin')
        cuerpo_if = self.parsear_cuerpo()
        self.avanzar('tend')

        cuerpo_else = None

        # Verificamos si hay un bloque "sino"
        if self.token_actual.tipo == 'tSino':
            self.avanzar('tSino')
            self.avanzar('tbegin')
            cuerpo_else = self.parsear_cuerpo()
            self.avanzar('tend')

        return {"tipo": "If", "condicion": condicion, "cuerpo_verdadero": cuerpo_if, "cuerpo_falso": cuerpo_else}
    

    def parsear_asignacion(self):

        """ Sirve para parsear una sentencia de asignación dentro del cuerpo del programa."""

        # <Asignación> ::= "id" <Tipo2>
        # <Tipo2> ::= ":=" <ExpArit>        
        # <Tipo2> ::= "[" <ExpArit> "," <ExpArit> "]" ":=" <ExpArit>

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una sentencia de asignación pero se encontró el fin de archivo.")
        
        token_id = self.avanzar('tid')

        if self.token_actual.tipo == 'topasig':
            self.avanzar('topasig')
            valor_asignacion = self.parsear_exp_arit()
            return {"tipo": "Asignacion", "variable": token_id.lexema, "valor": valor_asignacion}
        
        if self.token_actual.tipo == 'tabrecorch':
            self.avanzar('tabrecorch')
            indice_fila = self.parsear_exp_arit()
            self.avanzar('tcoma')
            indice_columna = self.parsear_exp_arit()
            self.avanzar('tcierracorch')
            self.avanzar('topasig')
            valor_asignacion = self.parsear_exp_arit()
            return {"tipo": "AsignacionMatrix", "variable": token_id.lexema, "indice_fila": indice_fila, "indice_columna": indice_columna, "valor": valor_asignacion}
        
        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            raise SyntaxError(f"Error Sintáctico: Se esperaba ':=' o '[', pero se encontró '{token_erroneo}' en la asignación.")
        

    def parsear_cond(self):

        """Sirve para parsear una condición de nivel bajo (OR) dentro de una sentencia if o while."""

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una condición pero se encontró el fin de archivo.")

        # 1. Parseamos la primera parte (lado izquierdo)
        nodo_izquierdo = self.parsear_cond2()

        # 2. Si viene un OR, armamos el árbol binario
        while self.token_actual is not None and self.token_actual.tipo == 'too':
            self.avanzar('too')
            nodo_derecho = self.parsear_cond2()

            # El nuevo nodo izquierdo pasa a ser la operación completa
            nodo_izquierdo = {
                "tipo": "OperacionLogica",
                "operador": "OR",
                "izquierda": nodo_izquierdo,
                "derecha": nodo_derecho
            }

        # Si no hubo OR, devuelve el nodo simple. Si hubo, devuelve el árbol anidado.
        return nodo_izquierdo
    

    def parsear_cond2(self):

        """Sirve para parsear una condición de nivel medio (AND) dentro de una sentencia if o while."""

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una condición pero se encontró el fin de archivo.")

        # 1. Parseamos la primera parte (lado izquierdo)
        nodo_izquierdo = self.parsear_cond3()

        # 2. Si viene un AND, armamos el árbol binario
        while self.token_actual is not None and self.token_actual.tipo == 'ty':
            self.avanzar('ty')
            nodo_derecho = self.parsear_cond3()
            
            nodo_izquierdo = {
                "tipo": "OperacionLogica",
                "operador": "AND",
                "izquierda": nodo_izquierdo,
                "derecha": nodo_derecho
            }

        return nodo_izquierdo
    

    def parsear_cond3(self):

        """Sirve para parsear una condición de nivel más alto dentro de una sentencia if o while."""

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una condición pero se encontró el fin de archivo.")

        if self.token_actual.tipo == 'tnot':
            self.avanzar('tnot')
            condicion_interna = self.parsear_cond3()
            return {"tipo": "CondicionNot", "condicion": condicion_interna}
        
        if self.token_actual.tipo == 'tabrellave':
            self.avanzar('tabrellave')
            condicion_interna = self.parsear_cond()
            self.avanzar('tcierrallave')
            return condicion_interna
        
        else:
            exp_izquierda = self.parsear_exp_arit()
            operador_relacional = self.avanzar('toprel')
            exp_derecha = self.parsear_exp_arit()
            return {"tipo": "CondicionRelacional", "exp_izquierda": exp_izquierda, "operador": operador_relacional.lexema, "exp_derecha": exp_derecha}
        

    def parsear_exp_arit(self):

        """ Sirve para parsear una expresión aritmética dentro de una sentencia de asignación o dentro de una condición."""

        # <ExpArit> ::= <ExpArit2> <ExpArit’>  |  <ExpArit’> ::= "+" <ExpArit2> <ExpArit’> | "-" <ExpArit2> <ExpArit’> | epsilon

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una expresión aritmética pero se encontró el fin de archivo.")
        
        nodo_izquierdo = self.parsear_exp_arit2()

        while self.token_actual is not None and self.token_actual.tipo in ['tsuma', 'tresta']:
            operador = self.token_actual.tipo
            self.avanzar(self.token_actual.tipo) 
            nodo_derecho = self.parsear_exp_arit2()
            nodo_izquierdo = {
                "tipo": "OperacionAritmetica",
                "operador": operador,
                "izquierda": nodo_izquierdo,
                "derecha": nodo_derecho
            }

        return nodo_izquierdo
    

    def parsear_exp_arit2(self):

        """Sirve para parsear una expresión aritmética de nivel medio dentro de una sentencia de asignación o dentro de una condición."""

        # <ExpArit2> ::= <ExpArit3> <ExpArit2’> | <ExpArit2’> ::= "*" <ExpArit3> <ExpArit2’> | "/" <ExpArit3> <ExpArit2’> | epsilon

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una expresión aritmética pero se encontró el fin de archivo.")
        
        nodo_izquierdo = self.parsear_exp_arit3()

        while self.token_actual is not None and self.token_actual.tipo in ['tmult', 'tdiv']:
            operador = self.token_actual.tipo
            self.avanzar(self.token_actual.tipo)
            nodo_derecho = self.parsear_exp_arit3()
            nodo_izquierdo = {
                "tipo": "OperacionAritmetica",
                "operador": operador,
                "izquierda": nodo_izquierdo,
                "derecha": nodo_derecho
            }

        return nodo_izquierdo
    

    def parsear_exp_arit3(self):

        """Sirve para parsear una expresión aritmética de nivel más alto dentro de una sentencia de asignación o dentro de una condición."""

        # <ExpArit3> ::= <ExpArit4> <ExpArit3’> | <ExpArit3’> ::= "^" <ExpArit4> <ExpArit3’> | epsilon

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba una expresión aritmética pero se encontró el fin de archivo.")
        
        nodo_izquierdo = self.parsear_exp_arit4()

        while self.token_actual is not None and self.token_actual.tipo == 'tpot':
            operador = self.token_actual.tipo
            self.avanzar(self.token_actual.tipo)
            nodo_derecho = self.parsear_exp_arit4()
            nodo_izquierdo = {
                "tipo": "OperacionAritmetica",
                "operador": operador,
                "izquierda": nodo_izquierdo,
                "derecha": nodo_derecho
            }

        return nodo_izquierdo
    

    def parsear_exp_arit4(self):

        """Sirve para parsear un factor dentro de una expresión aritmética, que puede ser un número, una variable o una expresión entre paréntesis."""

        # <ExpArit4> ::= “(“ <ExpArit> “)” | “id” | “constReal”

        if self.token_actual is None:
            raise SyntaxError("Error Sintáctico: Se esperaba un factor en la expresión aritmética pero se encontró el fin de archivo.")
        
        if self.token_actual.tipo == 'tabreparent':
            self.avanzar('tabreparent')
            nodo_interno = self.parsear_exp_arit()
            self.avanzar('tcierraparent')
            return nodo_interno
        
        if self.token_actual.tipo == 'tid':
            token_id = self.avanzar('tid')

            if self.token_actual is not None and self.token_actual.tipo == 'tabrecorch':
                self.avanzar('tabrecorch')
                indice_fila = self.parsear_exp_arit()
                self.avanzar('tcoma')
                indice_columna = self.parsear_exp_arit()
                self.avanzar('tcierracorch')
                
                return {"tipo": "AccesoMatriz", "variable": token_id.lexema, "indice_fila": indice_fila, "indice_columna": indice_columna}
            
            # Si no había corchete, entonces era una variable normal
            return {"tipo": "Variable", "nombre": token_id.lexema}
        
        if self.token_actual.tipo == 'tconstreal':
            token_num = self.avanzar('tconstreal')
            return {"tipo": "Constante", "valor": token_num.lexema}
        
        if self.token_actual.tipo == 'ttamfila':
            self.avanzar('ttamfila')
            self.avanzar('tabreparent')
            parametro = self.parsear_exp_arit()
            self.avanzar('tcierraparent')
            return {"tipo": "FuncionMatriz", "funcion": "filas", "parametro": parametro}
            
        if self.token_actual.tipo == 'ttamcol':
            self.avanzar('ttamcol')
            self.avanzar('tabreparent')
            parametro = self.parsear_exp_arit()
            self.avanzar('tcierraparent')
            return {"tipo": "FuncionMatriz", "funcion": "columnas", "parametro": parametro}
            
        if self.token_actual.tipo == 'ttransp':
            self.avanzar('ttransp')
            self.avanzar('tabreparent')
            parametro = self.parsear_exp_arit()
            self.avanzar('tcierraparent')
            return {"tipo": "FuncionMatriz", "funcion": "transpuesta", "parametro": parametro}

        else:
            token_erroneo = self.token_actual.lexema if self.token_actual else "Fin de archivo"
            raise SyntaxError(f"Error Sintáctico: Se esperaba un factor válido en la expresión aritmética, pero se encontró '{token_erroneo}'.")