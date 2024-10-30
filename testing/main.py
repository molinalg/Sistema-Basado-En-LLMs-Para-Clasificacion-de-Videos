### ---------------- Script para el control y ejecución de los tests para el proyecto de análisis de ODS ----------------

# Librerías necesarias
import pandas as pd
import os

# Módulos creados en otros archivos
from analizador_llama import Analizador_Llama
from excel_manager import Excel_Manager

def realizar_tests(excel, numero, nombre, etiqueta, nombre_excel):
    """Función para hacer testear el funcionamiento del prompt a partir de un Excel de ejemplos"""
    # Obtenemos los datos de prueba e inicializamos el nuevo Excel de corrección
    datos = excel_manager.generar_excel(excel, nombre_excel)
    nuevo_excel = pd.DataFrame(columns=["[Texto]", "ODS LLAMA"])

    total_datos = len(datos["[Texto]"])
    count = 1

    # Se procesa texto por texto
    print("\n---------- Proceso de test del Excel en marcha ----------\n")
    for texto in datos["[Texto]"]:
        # Se genera un análisis
        resultado = analizador.obtener_resultado(numero,nombre,texto)

        # Dependiendo del resultado se crea una nueva fila
        if resultado["Resultado"] == True:
            nueva_fila = {"[Texto]": texto, "ODS LLAMA": "{}".format(etiqueta)}
        elif resultado["Resultado"] == False:
            nueva_fila = {"[Texto]": texto, "ODS LLAMA": "-"}
        else:
            print("Se ha encontrado un error")
            nueva_fila = {"[Texto]": texto, "ODS LLAMA": "Error"}
        
        # Formateamos la nueva fila
        nueva_fila_pd = pd.DataFrame([nueva_fila])

        # Nos aseguramos del orden correcto de las columnas
        columnas = ["[Texto]", "ODS LLAMA"]
        nueva_fila_pd = nueva_fila_pd[columnas]

        # Concatenamos la nueva fila al nuevo Excel
        nuevo_excel = pd.concat([nuevo_excel, nueva_fila_pd], ignore_index=True)

        print("Porcentaje de textos procesados: {} %".format((count/total_datos)*100))
        count += 1
    
    nuevo_excel.to_excel(os.path.join(os.getcwd(),"testing/excels/generados/excel_test_llama_{}.xlsx".format(nombre_excel)), index=False)
    print("\n---------- Tests terminados ----------\n")

    # Se corrigen los resultados
    corregir_resultados("testing/excels/generados/excel_test_modificado_{}.xlsx".format(nombre_excel),"testing/excels/generados/excel_test_llama_{}.xlsx".format(nombre_excel),"testing/excels/estadisticas/estadisticas_resultados_{}.txt".format(nombre_excel), nombre_excel, etiqueta)

def corregir_resultados(excel_1, excel_2, nombre_archivo, nombre_excel, tema):
    """Función para corregir los resultados del test"""
    # Se leen ambos archivos
    data_1 = pd.read_excel(os.path.join(os.getcwd(),excel_1))
    data_2 = pd.read_excel(os.path.join(os.getcwd(),excel_2))

    # Se juntan ambos Excels
    data_total = pd.merge(data_1, data_2, on="[Texto]", how="inner")

    # Se crea la columna de corrección
    correcciones = []
    entradas_correctas = 0
    entradas_incorrectas = 0
    for indice, fila in data_total.iterrows():
        if fila["ODS VALIDADO"] == fila["ODS LLAMA"]:
            correcciones.append("BIEN")
            entradas_correctas += 1
        else:
            if fila["ODS VALIDADO"] != "-" and fila["ODS VALIDADO"] != tema:
                correcciones.append("BIEN")
                entradas_correctas += 1
            else:
                correcciones.append("MAL")
                entradas_incorrectas += 1
    data_total["CORRECIÓN"] = correcciones

    # Guardamos el Excel
    data_total.to_excel(os.path.join(os.getcwd(),"testing/excels/generados/excel_test_corregido_{}.xlsx".format(nombre_excel)), index=False)

    # Generamos las estadísticas
    generar_estadisticas(data_total, entradas_correctas, entradas_incorrectas, nombre_archivo, nombre_excel, tema)

def generar_estadisticas(datos, correctas, incorrectas, nombre_archivo, nombre_excel, tema):
    """Función para evaluar los tests realizados y generar las estadísticas"""
    with open(os.path.join(os.getcwd(),nombre_archivo), "w") as archivo:
        # Escribimos el encabezado
        archivo.write("Resultados obtenidos por Llama a partir del Excel '{nombre}' en torno a '{ods}':\n\n".format(nombre=nombre_excel, ods=tema))

        # Se cuentan las filas que tienen el tema detectado en el Excel original
        casos_positivos = datos[datos['ODS VALIDADO'] == tema].shape[0]

        # Después se cuentan las filas que tienen ese valor en el original y en el generado
        correctos_positivos = datos[(datos['ODS VALIDADO'] == tema) & (datos['ODS LLAMA'] == tema)].shape[0]

        # Escribimos las estadísticas
        archivo.write("- Número total de entradas: {}\n".format(len(datos)))
        archivo.write("- Número de entradas bien clasificadas: {correctas} ({porcentaje} %)\n".format(correctas=correctas, porcentaje=(correctas/len(datos))*100))
        archivo.write("- Número de entradas mal clasificadas: {incorrectas} ({porcentaje} %)\n".format(incorrectas=incorrectas, porcentaje=(incorrectas/len(datos))*100))
        archivo.write("- Número de entradas relacionadas al tema '{tema}': {positivos}\n".format(tema=tema, positivos=casos_positivos))
        archivo.write("- Número de entradas relacionadas al tema '{tema}' bien clasificadas: {correctos_positivos} ({porcentaje} %)\n".format(tema=tema, correctos_positivos=correctos_positivos, porcentaje=(correctos_positivos/casos_positivos)*100))
    
    print("---------- Se ha completado la corrección del test ----------")
            

# ---------------------------------- MAIN ----------------------------------

if __name__ == "__main__":
    # Herramientas
    global analizador
    global excel_manager
    analizador = Analizador_Llama()
    excel_manager = Excel_Manager()

    # Se llama a la función que realiza el test
    realizar_tests("testing/excels/ODS_Report_Cantabria - MAR-S1 validado.xlsx", 5, "Igualdad de Género", "«Igualdad de género»", "ODS_Report_Cantabria - MAR-S1 validado")