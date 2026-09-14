# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:23:09 2026

Integrantes: Ayala Ignacio, Della Bonzana Lara

Descripcion: En el presente archivo se muestra el código realizado para limpiar datos, visualizarlos y 
generar consultas 

Otros datos: 
"""

import sys 
print(sys.executable)
import pandas as pd
import duckdb as dd

import os
os.chdir(r"C:\Users\della\OneDrive\Documents\labo_datos\TP1")

#%% Subimos archivos
carpeta = "~/OneDrive/Documents/labo_datos/TP1/data/TablasOriginales/"

censo2010 = pd.read_excel(carpeta + "censo2010.xlsx", header= None, skiprows= 15)
censo2022 = pd.read_excel(carpeta + "censo2022.xlsx", header= None, skiprows= 15)
nacidos2010 = pd.read_csv(carpeta + "nacweb10.csv" , encoding= 'latin-1')
nacidos2022 = pd.read_csv(carpeta + "nacweb22_0.csv", sep= ";")
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
censo2010_limpio = censo2010.drop(columns= 0) # eliminamos la primera columna que eran todos Nan
censo2010_limpio.columns =['cobertura', 'edad', 'varon', 'mujer', 'total'] # Definimos las columnas con los valores que queremos
censo2010_limpio['provincia'] = None #Iniciamos una nueva columna cuyos valores son NaN
provincia_actual = None 

for i in range(len(censo2010_limpio)):
    fila = censo2010_limpio.iloc[i] 

    if str(fila.iloc[0]).startswith("AREA"): #En este punto sabemos que las provincias estaban separadas por "Area" en la columna de cobertura, y el nombre de la privncia en la columna de Edad
        provincia_actual = fila.iloc[1] #Nos quedamos con el nombre de la provincia

    censo2010_limpio.loc[i, "provincia"] = provincia_actual #Agregamos 
censo2010_limpio["cobertura"] = censo2010_limpio["cobertura"].ffill()
censo2010_limpio = censo2010_limpio[(censo2010_limpio["edad"].astype(str).str.strip().str.lower() != "total") & (censo2010_limpio["cobertura"].astype(str).str.strip().str.lower() != "total")] #Eliminamos el resumen de "total" que aparecen en las columnas de cobertura y edad

censo2010_limpio.drop(index = [0,1,2,3], axis = 0, inplace = True) #Eliminamos las primeras filas que no continen informacion
censo2010_limpio.to_csv('../TP1/data/TablasModelo/censo2010_tabla.csv')

#%%Emprolijamos la tabla del censo 2022
censo2022_limpio = censo2022.drop(columns =0)
censo2022_limpio.columns = ['cobertura', 'edad', 'varon', 'mujer', 'total']

censo2022_limpio['provincia'] = None #Iniciamos una nueva columna cuyos valores son NaN
provincia_actual = None 

for i in range(len(censo2022_limpio)):
    fila = censo2022_limpio.iloc[i] 

    if str(fila.iloc[0]).startswith("AREA"): #En este punto sabemos que las provincias estaban separadas por "Area" en la columna de cobertura, y el nombre de la privncia en la columna de Edad
        provincia_actual = fila.iloc[1] #Nos quedamos con el nombre de la provincia

    censo2022_limpio.loc[i, "provincia"] = provincia_actual #Agregamos 
censo2022_limpio["cobertura"] = censo2022_limpio["cobertura"].ffill()
censo2022_limpio = censo2022_limpio[(censo2022_limpio["edad"].astype(str).str.strip().str.lower() != "total") & (censo2022_limpio["cobertura"].astype(str).str.strip().str.lower() != "total")] #Eliminamos el resumen de "total" que aparecen en las columnas de cobertura y edad

censo2022_limpio.drop(index = [0,1,2,3], axis = 0, inplace = True) #Eliminamos las primeras filas que no continen informacion
censo2022_limpio.to_csv('../TP1/data/TablasModelo/censo2022_tabla.csv')

#%%Analizamos la tabla de nacidos de 2022
#Aca podemos ver que no es tan obvio lo que nos quiere expresar el csv
#Entonces deberiamos preguntarnos, que significan PROVRES? -> codigos de provincia
#Como se de que tipo de parto me esta hablando
#Como se de que sexo me esta hablando
nacidos2022.isna().value_counts()
#No hay ningun null, pero
nacidos2022['IPESONAC'].value_counts() #Tiene 445 sin especificar
nacidos2022['SEXO'].value_counts() #Tiene 1, 2 y 9? 
nacidos2022['IMEDAD'].value_counts() #Tiene 202 sin especificar
nacidos2022['ITIEMGEST'].value_counts() #Tiene 613 sin especificar
nacidos2022['IMINSTRUC'].value_counts() #Tiene 1354 sin especificar
#En todos estos apareces un numero n y n.Sin especificar 
#Despues hay que preguntarnos, sirve de algo tener datos vacios en este caso? Los puedo eliminar? 
#Ademas de que las columnas no son muy declarativas, no se leen muy bien

#Para saber de que provincia esta hablando, encontramos una lista de provincias con los codigos de cada una

#Renombramos columnas
nacidos2022_limpio = nacidos2022.rename(columns={
    "PROVRES": "provincia_residencia",
    "TIPPARTO": "tipo_parto",
    "SEXO": "sexo",
    "IMEDAD": "grupo_edad_madre",
    "ITIEMGEST": "grupo_semanas_gestacion",
    "IMINSTRUC": "nivel_educativo_madre",
    "IPESONAC": "peso_nacimiento",
    "CUENTA": "cantidad"
})
nacidos2022_limpio.columns

#Sacamos el formato de lista que tienen los datos
columnas_a_limpiar = [
    "grupo_edad_madre",
    "grupo_semanas_gestacion",
    "nivel_educativo_madre",
    "peso_nacimiento"
]

for columna in columnas_a_limpiar:
    nacidos2022_limpio[columna] = nacidos2022_limpio[columna].str.replace(
        r"^\d+\.", "", regex=True
    ).str.strip()
    

#%%Analizamos la tabla de nacidos de 2010
nacidos2010.isna().value_counts() #Aca vemos de vuelta que no hay ningun na, pero puede haber sin especificar
nacidos2010.columns #Mismo problema de columnas no muy declarativas
nacidos2010['PROVRES'].value_counts() #provincias en codigos
nacidos2010['SEXO'].value_counts() #1, 2 y 9
nacidos2010['IMEDAD'].value_counts() #Sin especificar: 553
nacidos2010['ITIEMGEST'].value_counts() #Sin especificar 1719
nacidos2010['IMINSTRUC'].value_counts() #Sin especificar 1458
nacidos2010['TIPPARTO'].value_counts() #1, 2 y 9?
print(nacidos2010.groupby("SEXO")["CUENTA"].sum()) #Aca esta bueno indicar que la cantidad de nacidos esta indicado por cada suma de cada cuenta
print(nacidos2010.groupby("TIPPARTO")["CUENTA"].sum())
print(nacidos2010['CUENTA'].dtype) #Por las dudas chequeamos que es un numero y no un string
#Otra cosa a notas en estas ultimas dos tablas, los datos arrancan como si estuvieran en una lista
# n.Sin espeificar, n.Hasta Primaria... , estaria bueno eliminarlo

#Renombramos columnas
nacidos2010_limpio = nacidos2010.rename(columns={
    "PROVRES": "provincia_residencia",
    "TIPPARTO": "tipo_parto",
    "SEXO": "sexo",
    "IMEDAD": "grupo_edad_madre",
    "ITIEMGEST": "grupo_semanas_gestacion",
    "IMINSTRUC": "nivel_educativo_madre",
    "IPESONAC": "peso_nacimiento",
    "CUENTA": "cantidad"
})
nacidos2010_limpio.columns

#Sacamos el formato de lista que tienen los datos
columnas_a_limpiar = [
    "grupo_edad_madre",
    "grupo_semanas_gestacion",
    "nivel_educativo_madre",
    "peso_nacimiento"
]

for columna in columnas_a_limpiar:
    nacidos2010_limpio[columna] = nacidos2010_limpio[columna].str.replace(
        r"^\d+\.", "", regex=True
    ).str.strip()

#Dejamos comentado los tipos que no sabemos que significa
#nacidos2010_limpio["sexo"] = nacidos2010_limpio["sexo"].replace({
#    1: "Varón",
#    2: "Mujer",
#    9: "Sin especificar"
#})
#nacidos2010_limpio["tipo_parto"] = nacidos2010_limpio["tipo_parto"].replace({
#    1: "Vaginal",
#    2: "Cesárear",
#    9: "Sin especificar"
#})

