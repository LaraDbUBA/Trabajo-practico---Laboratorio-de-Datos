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
from pathlib import Path

#Ignoren esto es de un problema de mi carpeta local
#import os
#os.chdir(r"C:\Users\della\OneDrive\Documents\labo_datos\TP1")

#Observacion: Todo lo que esta escrito de lo que se decidio hacer con los datos tiene que figurar en el informe (Nacho o Lu)

#%% Subimos archivos
raiz = Path(__file__).parent
carpetaOriginales = raiz / "data" / "TablasOriginales" #Fijense el tema de la carpeta, descarguense los archivos
carpetaLimpias = raiz / "data" / "TablasLimpias"
carpetaModelos = raiz /"data" / "TablasModelo"

censo2010 = pd.read_excel(carpetaOriginales / "censo2010.xlsx", header= None, skiprows= 15) #Son la cantidad de filas innecesarias con info extra
censo2022 = pd.read_excel(carpetaOriginales / "censo2022.xlsx", header= None, skiprows= 15) #Lo mismo
nacidos2010 = pd.read_csv(carpetaOriginales /  "nacweb10.csv" , encoding= 'latin-1') #Tiene latin-1 porque saltaba un error, lo vi en un chico de reddit y funciona asi que dejenlo asi
nacidos2022 = pd.read_csv(carpetaOriginales / "nacweb22_0.csv", sep= ";") #Tiene distinta separacion
establecimientos = pd.read_excel(carpetaOriginales / "establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

#%% Subimos archivos adicionales
provincias = pd.read_excel(carpetaOriginales / "Listado De Provincias - 11-09-2026.xlsx")

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


provincias_tabla.to_csv(carpetaModelos /'provincias.csv')
#%% Emprolijamos la tabla del censo 2010
#Observacion: En este excel, tenemos una gran cantidad de filas que no porporcionan informacion, 
#fueron eliminadas con skiprows, eliminamos tambien el header que no era util pues decia A,B,C,..
#Tambien notamos que por cada provincia habia una tabla distinta, nuestro objetivo ahora es juntarlo
#Todo en una columna de Provincia. tambien habian filas de "totales" metidas en la columna de edad
#y una tabla al final de todo que era la suma de todos los valores, esa tabla nos es inutil, decidimos
#eliminarla


# normalizar los archivos de censo
provincias = pd.read_csv(carpetaModelos / "provincias.csv")
def normalizar_datos_censo(censo):
    censo_limpio = censo.drop(columns= 0) # eliminamos la primera columna que eran todos Nan
    censo_limpio.columns =['cobertura', 'edad', 'varon', 'mujer', 'total'] # Definimos las columnas con los valores que queremos
    
    censo_limpio['provincia'] = None #Iniciamos una nueva columna cuyos valores son NaN
    provincia_actual = None 
    
    for i in range(len(censo_limpio)):
        fila = censo_limpio.iloc[i] 
    
        if str(fila.iloc[0]).startswith("AREA"): #En este punto sabemos que las provincias estaban separadas por "Area" en la columna de cobertura, y el nombre de la privncia en la columna de Edad
            provincia_actual = fila.iloc[1] #Nos quedamos con el nombre de la provincia
    
        censo_limpio.loc[i, "provincia"] = provincia_actual #Agregamos 
    
    #print(censo_limpio["provincia"].unique())
    
    censo_limpio["provincia"] = censo_limpio["provincia"].str.upper()

    #Notamos que en el censo de 2022 aparece Caba en vez de Ciudad Autonoma de Buenos Aires
    #Lo pasamos a mayuscula para poder usar el DataFrame de provincias
    censo_limpio["provincia"] = censo_limpio["provincia"].replace({
        "CABA": "CIUDAD DE BUENOS AIRES",
        "CIUDAD AUTÓNOMA DE BUENOS AIRES": "CIUDAD DE BUENOS AIRES"
    })
    
    censo_limpio = censo_limpio[
    ~censo_limpio["cobertura"].astype(str).str.startswith("AREA")
]
    
    #Hacemos merge con el dataframe de provincias para sacar los codigos
    
    censo_limpio = censo_limpio.merge(provincias[["provincia", "codigo"]]
    .rename(columns={"codigo": "provincia_id"}),
    on="provincia",
    how="left"
    )
    
    #El merge dejo valor en float
    censo_limpio["provincia_id"] = censo_limpio["provincia_id"].astype("Int64") #Lo cambio a int por las dudas
    
    #Ya no me interesa tener la columna de provincia
    
    censo_limpio = censo_limpio.drop(columns = 'provincia')
    
    #Aca llenamos los espacios vacios que aparecian en cobertura
    censo_limpio["cobertura"] = censo_limpio["cobertura"].ffill() 
    #Hay que ver si es valida para la materia
    
    #Sacamos la pseudo tablita de los totales (la podemos calcular nosotros a mano, es redundante)
    censo_limpio = censo_limpio[
    (censo_limpio["edad"].astype(str).str.strip().str.lower() != "total") &
    (censo_limpio["cobertura"].astype(str).str.strip().str.lower() != "total") &
    (censo_limpio["edad"].astype(str).str.strip().str.lower() != "edad")
]
 
    return censo_limpio
    


dfcenso2022_limpio = normalizar_datos_censo(censo2022)
dfcenso2022_limpio.to_csv(carpetaLimpias / "censo2022.csv")
dfcenso2010_limpio = normalizar_datos_censo(censo2010)
dfcenso2010_limpio.to_csv(carpetaLimpias / "censo2010.csv")

#Ahora agregamos la columna de año a cada uno y los juntamos en una misma tabla
dfcenso2022_limpio["año"] = 2022
dfcenso2010_limpio["año"] = 2010


dffinal = pd.concat([dfcenso2010_limpio, dfcenso2022_limpio])
dffinal = dffinal.drop(columns = ["varon", "mujer"]) #Sacamos la columna de total que era redundante
dffinal.to_csv(carpetaModelos / "censos.csv")

#Chequeamos dependencias funcionales
dffinal.groupby(["cobertura",  "edad", "provincia_id", "año"])["total"].nunique()
#Queda una clave primaria compuesta de: cobertura, edad, provincia_id, año


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
       

nacidos2022_limpio = modificar_censo(columnas_a_limpiar, nacidos2022)
nacidos2022_limpio["año"] = 2022
nacidos2022_limpio.to_csv(carpetaLimpias / "nacidos2022.csv")
analizar_variables_calidad(variables_calidad, nacidos2022_limpio )


nacidos2010_limpio = modificar_censo(columnas_a_limpiar, nacidos2010)
nacidos2010_limpio["año"] = 2010
nacidos2010_limpio.to_csv(carpetaLimpias / "nacidos2010.csv")
analizar_variables_calidad(variables_calidad, nacidos2010_limpio )


dffinal = pd.concat([nacidos2022_limpio, nacidos2010_limpio])

dffinal.to_csv(carpetaModelos / "nacidos.csv")

dffinal.groupby(["provincia_residencia", "tipo_parto", "sexo", "grupo_edad_madre", "grupo_semanas_gestacion", "nivel_educativo_madre",  "peso_nacimiento", "año"])["cantidad"].nunique().loc[lambda x : x>1]
#Todas las columnas son una clave
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

#Anlizamos las dependencias funcionales
establecimientos.groupby(["provincia_id", "departamento_id"])["departamento_nombre"].nunique() #Aca da que cada combinacion es unica, entonces (departamento_id, provincia_id) -> departamento_nombre
establecimientos.groupby('localidad_id')[["departamento_id", "provincia_id", "localidad_nombre"]].nunique() #Lo mismo (localidad_id) -> (departamento_id, provincia_id, localidad_nombre)
establecimientos.groupby("establecimiento_id")[["provincia_id", "departamento_id"]].nunique() # (establecimiento_id) -> (provincia_id, departamento_id)
#Sobre tipologia: Esto lo repetimos con cada uno y lo unico que vimos es que la sigla determina el id
#El resto no se relaciona
#El estableimiento id determina todos individualmente
#Luego, podemos quedarnos solo con el nombre que es lo que nos interesa
establecimientos.groupby(["tipologia_nombre"])["tipologia_id"].nunique().loc[lambda x: x>1]

#localidad = establecimientos[["localidad_id", "departamento_id", "provincia_id", "localidad_nombre"]]
#localidad.to_csv('~/OneDrive/Documents/labo_datos/TP1/data/TablasModelo/localidad.csv')
departamentos = establecimientos[["departamento_id", "departamento_nombre", "provincia_id"]]
establecimientos_limpio = establecimientos[["establecimiento_id", "establecimiento_nombre", "origen_financiamiento", "departamento_id", "provincia_id" ,"tipologia_nombre"]]
departamentos.to_csv(carpetaModelos / "departamentos.csv")
establecimientos_limpio.to_csv(carpetaModelos / "establecimientos.csv")



#%% Consultas


