"""Analizador Léxico para el lenguaje de programación simple."""

import re    #Libreria de Expresiones Regulares para reducir los while y simplificar codigo
from typing import NamedTuple


class Token(NamedTuple):

    """
     Definicion de la clase Token para representar los tokens generados por el analizador léxico.
     Cada token tiene un tipo, un lexema, una línea y una columna.

    """
    
    tipo : str
    lexema: str
    linea: int
    columna: int


class AnalizadorLexico:

    """
     Definición de la clase AnalizadorLexico para realizar el análisis léxico del código fuente. 
     Esta clase contiene un diccionario de palabras reservadas y métodos para tokenizar el código fuente.

    """

    PALABRAS_RESERVADAS = {
        'program': 'tprogram', 'var': 'tvar', 'begin': 'tbegin', 'end': 'tend',
        'real': 'tnumreal', 'matrix': 'tmatrix', 'of': 'tof', 'leer': 'tLeer',
        'escribir': 'tEscribir', 'si': 'tSi', 'entonces': 'tEntonces', 'sino': 'tSino',
        'mientras': 'tMientras', 'hacer': 'tHacer', 'filas': 'ttamfila', 
        'columnas': 'ttamcol', 'true': 'ttrue', 'false': 'tfalse', 
        'not': 'tnot', 'and': 'ty', 'or': 'too'
    }

    REGLAS_LEXICAS = [
        ('tconstreal',   r'\d+\.\d+|\d+'),           # Números enteros o decimales
        ('tconstcadena', r'"[^"]*"'),                # Cadenas entre comillas dobles
        ('topasig',      r':='),                     # Asignación
        ('toprel',       r'<=|>=|<>|<|>|='),         # Operadores relacionales
        ('tid',          r'[A-Za-z][A-Za-z0-9_]*'),  # Identificadores (variables)
        ('tsuma',        r'\+'),
        ('tresta',       r'-'),
        ('tmult',        r'\*'),
        ('tdiv',         r'/'),
        ('tpot',         r'\^'),
        ('tabreparent',  r'\('),
        ('tcierraparent',r'\)'),
        ('tabrecorch',   r'\['),
        ('tcierracorch', r'\]'),
        ('tabrellave',   r'\{'),
        ('tcierrallave', r'\}'),
        ('tdospuntos',   r':'),
        ('tpuntoycoma',  r';'),
        ('tcoma',        r','),
        ('tpunto',       r'\.'),
        ('SALTO_LINEA',  r'\n'),                     # Para contar las líneas
        ('ESPACIOS',     r'[ \t]+'),                 # Espacios y tabulaciones (se ignoran)
        ('ERROR',        r'.'),                      # Cualquier otro carácter es error
    ]   


    # El constructor de la clase AnalizadorLexico recibe el código fuente como argumento 
    # y compila las reglas léxicas en una expresión regular maestra para facilitar el proceso de tokenización.
    def __init__(self, codigo_fuente: str):
        self.codigo_fuente = codigo_fuente

        #Construye una expresión regular maestra a partir de las reglas léxicas definidas. Cada regla se convierte en un grupo nombrado para facilitar la identificación del tipo de token durante el proceso de tokenización.
        partes_regex = '|'.join(f'(?P<{nombre}>{regex})' for nombre, regex in self.REGLAS_LEXICAS) 

        self.regex_maestro = re.compile(partes_regex)


   
    def obtener_tokens(self):

        """
         Realiza el proceso de tokenización del código fuente. Utiliza la expresión regular maestra para encontrar coincidencias en el código fuente 
         y generar una lista de tokens.

        """
        tokens = []
        linea = 1
        columna = 1

        for coincidencia in self.regex_maestro.finditer(self.codigo_fuente):
            tipo_token = coincidencia.lastgroup
            lexema = coincidencia.group(tipo_token)

            if tipo_token == 'SALTO_LINEA':
                linea += 1
                columna = 1
            elif tipo_token == 'ESPACIOS':
                columna += len(lexema)
            elif tipo_token == 'ERROR':
                raise SyntaxError(f"Caracter no reconocido '{lexema}' en línea {linea}, columna {columna}")
            else:

                # Si el token es un identificador (tid) y su lexema coincide con una palabra reservada 
                # se actualiza el tipo de token al correspondiente en el diccionario de palabras reservadas.
                if tipo_token == 'tid' and lexema.lower() in self.PALABRAS_RESERVADAS:
                    tipo_token = self.PALABRAS_RESERVADAS[lexema.lower()]
                
                tokens.append(Token(tipo=tipo_token, lexema=lexema, linea=linea, columna=columna))
                columna += len(lexema)
        
        tokens.append(Token(tipo='pesos', lexema='$', linea=linea, columna=columna))

        return tokens



# Bloque de código para pruebas.
# Se define un código de prueba que contiene varias construcciones del lenguaje, se crea una
# instancia del analizador léxico con ese código y se obtiene la lista de tokens generados.
# Finalmente, se imprime la lista de tokens en un formato tabular.
if __name__ == '__main__':
    CODIGO_PRUEBA = """
    program MultiplicarMatrices;
    var
      matrizA : matrix;
    begin
      matrizA := 10.5;
      Mientras matrizA <> 0 Hacer
      begin
        Escribir("Hola mundo");
      end
    end
    """

    lexer = AnalizadorLexico(CODIGO_PRUEBA)
    lista_tokens = lexer.obtener_tokens()
    
    print(f"{'TIPO':<15} | {'LEXEMA':<20} | {'LÍNEA':<5} | {'COLUMNA'}")
    print("-" * 55)
    for token in lista_tokens:
        print(f"{token.tipo:<15} | {token.lexema:<20} | {token.linea:<5} | {token.columna}")

