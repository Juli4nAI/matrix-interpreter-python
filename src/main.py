import json
from analizador_lexico import AnalizadorLexico
from analizador_sintactico import AnalizadorSintactico

def probar_compilador():
    # 1. El código fuente escrito en tu lenguaje
    codigo_prueba = """
    program mi_portfolio;
    
    var
    numero : real ;
    matrizA : matrix [2, 2] of real ;
    
    begin
        leer("Ingrese un valor inicial", numero);
        
        matrizA[1, 1] := numero * 2 + 5;
        
        si matrizA[1, 1] > 10 entonces
        begin
            escribir("El valor es grande", matrizA[1, 1]);
        end
        sino
        begin
            escribir("El valor es chico");
        end;
        
        mientras numero < 100 hacer
        begin
            numero := numero + 10;
        end
    end .
    """
    
    print("⏳ Iniciando compilación...\n")

    try:
        # 2. Fase Léxica
        print("🔍 1. Ejecutando Analizador Léxico...")
        lexico = AnalizadorLexico(codigo_prueba)
        tokens = lexico.obtener_tokens()
        print(f"✅ Se generaron {len(tokens)} tokens.\n")

        # 3. Fase Sintáctica
        print("🌳 2. Ejecutando Analizador Sintáctico (Armando el AST)...")
        sintactico = AnalizadorSintactico(tokens)
        arbol_ast = sintactico.parsear_programa()
        print("✅ Análisis sintáctico exitoso sin errores.\n")

        # 4. Mostramos el resultado final
        print("✨ ÁRBOL DE SINTAXIS ABSTRACTA (AST) ✨")
        # Usamos json.dumps para imprimir el diccionario con indentación de 4 espacios
        print(json.dumps(arbol_ast, indent=4, ensure_ascii=False))

    except Exception as e:
        # Si hay un error léxico o sintáctico, lo atrapamos y lo mostramos en rojo (opcional)
        print("\n❌ ¡Ups! Hubo un error de compilación:")
        print(e)

if __name__ == "__main__":
    probar_compilador()