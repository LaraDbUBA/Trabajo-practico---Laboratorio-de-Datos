# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:23:09 2026

Integrantes: Ayala Ignacio, Della Bonzana Lara, Mile, Lu (completar)

Descripcion: En el presente archivo se muestra el código realizado para limpiar datos, visualizarlos y 
generar consultas 

Otros datos:  :)
"""

#import sys 
#print(sys.executable)
import pandas as pd
import duckdb as dd

#Ignoren esto es de un problema de mi carpeta local
#import os
#os.chdir(r"C:\Users\della\OneDrive\Documents\labo_datos\TP1")

#Observacion: Todo lo que esta escrito de lo que se decidio hacer con los datos tiene que figurar en el informe (Nacho o Lu)

#%% Subimos archivos
carpeta = "~/Documents/TP1/data/TablasOriginales/" #Fijense el tema de la carpeta, descarguense los archivos

censo2010 = pd.read_excel(carpeta + "censo2010.xlsx", header= None, skiprows= 15) #Son la cantidad de filas innecesarias con info extra
censo2022 = pd.read_excel(carpeta + "censo2022.xlsx", header= None, skiprows= 15) #Lo mismo
nacidos2010 = pd.read_csv(carpeta + "nacweb10.csv" , encoding= 'latin-1') #Tiene latin-1 porque saltaba un error, lo vi en un chico de reddit y funciona asi que dejenlo asi
nacidos2022 = pd.read_csv(carpeta + "nacweb22_0.csv", sep= ";") #Tiene distinta separacion
establecimientos = pd.read_excel(carpeta + "establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

#%% Subimos archivos adicionales
provincias = pd.read_excel(carpeta + "Listado De Provincias - 11-09-2026.xlsx")

#%% Emprolijamos la tabla del censo 2010
#Observacion: En este excel, tenemos una gran cantidad de filas que no porporcionan informacion, 
#fueron eliminadas con skiprows, eliminamos tambien el header que no era util pues decia A,B,C,..
#Tambien notamos que por cada provincia habia una tabla distinta, nuestro objetivo ahora es juntarlo
#Todo en una columna de Provincia. tambien habian filas de "totales" metidas en la columna de edad
#y una tabla al final de todo que era la suma de todos los valores, esa tabla nos es inutil, decidimos
#eliminarla




#%%Analizamos la tabla de nacidos de 2022 y nacidos 2010
#Aca podemos ver que no es tan obvio lo que nos quiere expresar el csv

def ver_valores_nacidos(nacidos):
    print("\nCantidad de datos vacios por columna =======\n")
    print(nacidos.isna().value_counts())
    #No hay ningun null, pero
    print("Valores de los pesos en gramos: ")
    print(nacidos['IPESONAC'].value_counts()) 
    print("Valores de sexo: ")
    print(nacidos['SEXO'].value_counts())
    print("Valores de grupo de edad de la madre: ")
    print(nacidos['IMEDAD'].value_counts()) 
    print("Tiempo de gestacion: ")
    print(nacidos['ITIEMGEST'].value_counts())
    print("Valores de niveles de educacion de madre: ")
    print(nacidos['IMINSTRUC'].value_counts()) 
    print()
    
ver_valores_nacidos(nacidos2010)
ver_valores_nacidos(nacidos2022)

#En todos estos apareces un numero n y n.Sin especificar 
#Despues hay que preguntarnos, sirve de algo tener datos vacios en este caso? Los puedo eliminar? 
#Ademas de que las columnas no son muy declarativas, no se leen muy bien


#Otra cosa a notas en estas ultimas dos tablas, los datos arrancan como si estuvieran en una lista
# n.Sin espeificar, n.Hasta Primaria... , estaria bueno eliminarlo


# Creamos variable para luego usarla con la funcion modificar_censo, para sacar el formato de lista de datos
columnas_a_limpiar = [
    "grupo_edad_madre",
    "grupo_semanas_gestacion",
    "nivel_educativo_madre",
    "peso_nacimiento"
]

# Creamos variable de analisis de calidad de los datos sin especificar, para luego usar en la funcion analizar_variable_calidad -- Esto es para el punto de análisis de calidad
variables_calidad = [
    "peso_nacimiento",
    "grupo_edad_madre",
    "grupo_semanas_gestacion",
    "nivel_educativo_madre"
]


def modificar_censo(columnas, censo):
    #renombrar columnas a columnas mas declarativas
    censo = censo.rename(columns={
        "PROVRES": "provincia_residencia",
        "TIPPARTO": "tipo_parto",
        "SEXO": "sexo",
        "IMEDAD": "grupo_edad_madre",
        "ITIEMGEST": "grupo_semanas_gestacion",
        "IMINSTRUC": "nivel_educativo_madre",
        "IPESONAC": "peso_nacimiento",
        "CUENTA": "cantidad"
    })
    
    #sacamos el formato de lista que tienen los datos en esas columnas
    for columna in columnas:
        censo[columna] = censo[columna].str.replace(
            r"^\d+\.", "", regex=True
        ).str.strip()
        
    #Cambiamos los valores que no se entienden
    censo["sexo"] = censo["sexo"].replace({
        1: "Varón",
        2: "Mujer",
        9: "Sin especificar"
    })
    censo["tipo_parto"] = censo["tipo_parto"].replace({
        1: "Simple",
        2: "Múltiple",
        9: "Sin especificar"
    })
    
    return censo
    
def analizar_variables_calidad(variables_calidad, censo):
    
    for variable in variables_calidad:
        
        sin_especificar = censo.loc[
             censo[variable] == "Sin especificar",
            "cantidad"
        ].sum()
        
        total = censo["cantidad"].sum()
        
        porcentaje = sin_especificar / total * 100
        
        print("Columna: ", variable)
        print("Nacimientos sin especificar:", sin_especificar)
        print("Porcentaje:", porcentaje)
        print()

nacidos2022_limpio = modificar_censo(columnas_a_limpiar, nacidos2022)
nacidos2022_limpio.to_csv('~/Documents/TP1/data/TablasLimpias/nacidos2022.csv')
analizar_variables_calidad(variables_calidad, nacidos2022_limpio )

nacidos2010_limpio = modificar_censo(columnas_a_limpiar, nacidos2010)
nacidos2010_limpio.to_csv('~/Documents/TP1/data/TablasLimpias/nacidos2010.csv')
analizar_variables_calidad(variables_calidad, nacidos2010_limpio )

#%% Analziamos la tabla de establecimientos
print('Columnas de tabla ========= \n')
print(establecimientos.columns + "\n")
print("\nInformación ======== \n")
print(establecimientos.info)
print("\nCantidad de datos vacios por columna =======\n")
print(establecimientos.isna().sum()) #Aca vemos que en la oclumna de codent hay 816 Nan y en el sitioweb 33188, cosa que no aporta mucha informacion de lo que nos interesa
#establecimientos[establecimientos['sitio_web'] =='<br>']

print("\nHay duplicados? =======\n")
print(establecimientos[establecimientos.duplicated(keep=False)]) #No hay repetidos
print("\nValores de financiamiento =======\n")
print(establecimientos["origen_financiamiento"].value_counts(dropna=False)) #Se ve bien
print("\nValores de siglas de tipologia =====\n")
print(establecimientos["tipologia_sigla"].value_counts(dropna=False))
print("\nValores de nombres de tipologia =======\n")
print(establecimientos["tipologia_nombre"].value_counts(dropna=False))


#cambio los Null por "Sin especificar" para evitar inconsistencias y erorres en las consultas
establecimientos["sitio_web"] = establecimientos["sitio_web"].fillna("Sin especificar")
establecimientos["codent"] = establecimientos["codent"].fillna("Sin especificar")

# Analisis de calidad: porcentaje de valores "Sin especificar", valores desconocidos.
def analisis_calidad_porcnull_establecimientos(columna,censo):
    porcentaje_columna = (
        (censo[columna] == "Sin especificar").sum()
        / len(censo)
        * 100
    )
    
    return porcentaje_columna

porcentaje_web = analisis_calidad_porcnull_establecimientos("sitio_web", establecimientos)
print("Porcentaje de vacios de sitio web:", porcentaje_web)
porcentaje_codent = analisis_calidad_porcnull_establecimientos("codent", establecimientos)
print("Porcentaje de vacios de codent:", porcentaje_codent)

#%% Armo tabla de la provincia y los codigos
#Vamos a utilziar la tabla que encontramos de provincias para relacionar las tablas anteriores, pues aparecen los codigos de provincia en algunas de estas
#De la tabla solo me interesa el codigo y el nombre de la provincia asi que
provincias.columns
provincias[(provincias['Código UTA 2010'] != provincias['Código UTA 2020'])] #son los mismos codigos
provincias_tabla = provincias[['Nombre', 'Código UTA 2010']]
provincias_tabla = provincias_tabla.rename(columns ={
    'Nombre': 'provincia',
    'Código UTA 2010': 'codigo'
    })

provincias_tabla.to_csv('~/Documents/TP1/data/TablasModelo/provincias.csv')

#%%
