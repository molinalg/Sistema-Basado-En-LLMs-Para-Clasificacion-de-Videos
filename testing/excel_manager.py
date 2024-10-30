### ---------------- Clase Excel_Manager para manejar los excels usados en el proceso de tests ----------------

# Librería de para el manejo de datos
import pandas as pd
import os

class Excel_Manager:
    """Clase para manejar excels"""
    def __init__(self):
        # Cargamos la ruta actual
        self.ruta_actual = os.getcwd()

    def generar_excel(self,excel, nombre_excel):
        """Función que genera un nuevo Excel para usar de test a partir del original reduciendo el tamaño y eliminando columnas innecesarias"""
        # Leemos el archivo Excel
        data = self.devolver_datos(excel)

        # Se selecciona las filas que tienen un '-' en la columna de ODS VALIDADO y se cuentan
        filas_sin_ods = data[data["ODS VALIDADO"].astype(str).str.contains("-")]
        guiones = len(filas_sin_ods)

        # Se cuentan las filas totales
        filas_totales = len(data)

        # Se calcula el número de filas vacías a eliminar (3/5 de las mismas)
        filas_a_eliminar = int(guiones * 3 / 5)

        # Se seleccionan ese número de filas de forma aleatoria
        filas_borrar = filas_sin_ods.sample(n=filas_a_eliminar, random_state=20)

        # Se eliminan las filas seleccionadas
        data_nuevo = data.drop(filas_borrar.index)

        # Se eliminan las filas duplicadas
        data_nuevo = data_nuevo.drop_duplicates(subset='[Texto]')

        # Eliminamos las columnas que no son necesarias para el caso
        columnas_sobrantes = ["[Keyword]", "ODS V3", "Resultado V3", "[Fecha]", "[FranjaHoraria]", "[Milisegudos]", "[Cluster]"]
        data_nuevo = data_nuevo.drop(columns=columnas_sobrantes)

        # Se crea el nuevo archivo de excel
        data_nuevo.to_excel(os.path.join(self.ruta_actual,"testing/excels/generados/excel_test_modificado_{}.xlsx".format(nombre_excel)), index=False)

        # Imprimimos datos sobre las operaciones realizadas
        print("Filas del Excel original: {}".format(filas_totales))
        print("De las cuales son vacías: {}".format(guiones))
        print("Filas del nuevo Excel: {}".format(len(data_nuevo)))
        print("Número de filas que se han eliminado: {}".format(filas_totales-len(data_nuevo)))
        print("\n---Nuevo Excel generado satisfactoriamente---\n")

        return data_nuevo
    
    
    def devolver_datos(self,nombre):
        """Función para leer un Excel y devolver sus datos"""
        ruta_carpeta = os.path.join(self.ruta_actual, nombre)
        return pd.read_excel(ruta_carpeta)
