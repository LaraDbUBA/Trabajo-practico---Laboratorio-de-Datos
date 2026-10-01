# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:23:09 2026

Integrantes: Ayala Ignacio, Della Bonzana Lara, Ventroni Milena, Posse Lucila

Descripcion: En el presente archivo se muestra el código realizado para limpiar datos, visualizarlos y 
generar consultas 

Otros datos:  :)
"""

#import sys 
#print(sys.executable)
import pandas as pd
import duckdb as dd
from pathlib import Path
import matplotlib.pyplot as plt

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
establecimientosOriginal = pd.read_excel(carpetaOriginales / "establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

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

#%% Analisis de atributos de calidad

# Tabla establecimientos 

# Atributo de calidad: COMPLETITUD
# conteo de valores null en sitio web, codent y valores incompletos en domicilio

pct_val_incompletos_establecimientos = """
                                SELECT
                                    COUNT(*) AS total_registros,
                                    -- Sitio Web
                                    SUM(
                                        CASE
                                            WHEN e.sitio_web IS NULL 
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_null_sitio_web,
                                    ROUND(100.0 * cant_null_sitio_web / COUNT(*), 2) AS pct_null_web,
                                    
                                    -- Codent
                                    SUM(
                                        CASE
                                            WHEN e.codent IS NULL 
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_null_codent,
                                    ROUND(100.0 * cant_null_codent / COUNT(*), 2) AS pct_null_codent,
                                    
                                    -- Domicilio
                                    SUM(
                                        CASE
                                            WHEN e.domicilio IS NULL OR LOWER(e.domicilio) LIKE '%sin%'
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_incompletos_domicilio,
                                    ROUND(100.0 * cant_incompletos_domicilio / COUNT(*), 2) AS pct_incompletos_domicilio
                                FROM establecimientosOriginal e
                              
                            
                        """
    
dataframeResultado = dd.sql(pct_val_incompletos_establecimientos).df()

print(dataframeResultado) 
#escribir conclusion y decision tomada
# Atributo de calidad : CONSISTENCIA
# mismo id tiene dos valores diferentes

# Hay localidades que tienen el mismo id pero son distintas(hay variantes en el nombre), creemos que sigue siendo la misma localidad
pct_id_inconsistentes_establecimientos = """
                            SELECT
                                COUNT(*) AS total_registros,
                                SUM(
                                    CASE
                                        -- Mismo id distintas localidades(hay inconsistencias en localidad_nombre(pero en realidad es la misma))
                                        WHEN e.localidad_id IN (
                                            SELECT e.localidad_id
                                            FROM establecimientosOriginal e
                                            WHERE e.localidad_id IS NOT NULL
                                            GROUP BY localidad_id
                                            HAVING COUNT(DISTINCT localidad_nombre) > 1)
                                        THEN 1
                                        ELSE 0
                                        END) AS cant_registros_afectados,
                                        ROUND(100.0 * cant_registros_afectados / COUNT(*), 2) AS pct_localidadid_inconsistente
                            FROM establecimientosOriginal e
                            
                        """

                    
dataframeResultado2 = dd.sql(pct_id_inconsistentes_establecimientos).df()
#escribir conclusion y decision.
print(dataframeResultado2)                  

# Tabla nacidos

# Atributo de calidad: COMPLETITUD
# valores incompletos en columnas ITIEMGEST, IMEDAD, IMINSTRUC, IPESONAC en tabla nacidos2010

# lo hicimos con nacidos2010 pero se puede hacer con la tabla general de nacidos

pct_val_incompletos_nacidos = """
                                SELECT
                                    COUNT(*) AS total_registros,
                                    -- ITIEMGEST
                                    SUM(
                                        CASE
                                            WHEN n.ITIEMGEST IS NULL OR LOWER(n.ITIEMGEST) LIKE '%sin%'
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_incompleto_ITIEMGEST,
                                    ROUND(100.0 * cant_incompleto_ITIEMGEST / COUNT(*), 2) AS pct_incompleto_ITIEMGEST,
                                    
                                    -- IMEDAD
                                    SUM(
                                        CASE
                                            WHEN n.IMEDAD IS NULL OR LOWER(n.IMEDAD) LIKE '%sin%'
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_incompleto_IMEDAD,
                                    ROUND(100.0 * cant_incompleto_IMEDAD / COUNT(*), 2) AS pct_incompleto_IMEDAD,
                                    
                                    -- IMINSTRUC
                                    SUM(
                                        CASE
                                            WHEN n.IMINSTRUC IS NULL OR LOWER(n.IMINSTRUC) LIKE '%sin%'
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_incompleto_IMINSTRUC,
                                    ROUND(100.0 * cant_incompleto_IMINSTRUC / COUNT(*), 2) AS pct_incompleto_IMINSTRUC,
                                    
                                    -- IPESONAC
                                    SUM(
                                        CASE
                                            WHEN n.IPESONAC IS NULL OR LOWER(n.IPESONAC) LIKE '%sin%'
                                            THEN 1 
                                            ELSE 0 
                                            END) AS cant_incompleto_IPESONAC,
                                    ROUND(100.0 * cant_incompleto_IPESONAC / COUNT(*), 2) AS pct_incompleto_IPESONAC,
                                FROM nacidos2010 n

                         """
dataframeResultado3 = dd.sql(pct_val_incompletos_nacidos).df()

print(dataframeResultado3) 
#la conclusion de esto seria que nos quedamos con todo porque representa poco problema

## Estaria buenisimo agregar el analisis de legibilidad que dijo guada del formato lista que tienen (daria un 100% que justifica el cambio)

#%% Emprolijamos la tabla de los censos
#Observacion: En este excel, tenemos una gran cantidad de filas que no porporcionan informacion, 
#fueron eliminadas con skiprows, eliminamos tambien el header que no era util pues decia A,B,C,..
#Tambien notamos que por cada provincia habia una tabla distinta, nuestro objetivo ahora es juntarlo
#Todo en una columna de Provincia. tambien habian filas de "totales" metidas en la columna de edad
#y una tabla al final de todo que era la suma de todos los valores, esa tabla nos es inutil, decidimos
#eliminarla
#Ademas debemos juntar las dos tablas de los censos 
#Como adicional, vamos a retirar las columnas de varon y mujer y transformaremos las celdas de cobertura a: Con cobertura o sin cobertura, que es lo que nos interesa

#Segun nuestro DER final, debemos hacer una tabla que relaciona los censos y las provincias.
# normalizar los archivos de censo
provincias = pd.read_csv(carpetaModelos / "provincias.csv")
  
#el objetivo de esta funcion es resumir un poco el analisis que hicimos porque fuimos y vinimos con la limpieza de datos
def analizar_censo(censo):
    print("=" * 60)
    print("ANÁLISIS DEL CENSO")
    print("=" * 60)

    print("\n1. COLUMNAS Y TIPOS DE DATOS")
    print("-" * 40)
    print(censo.dtypes)

    print("\n2. VALORES DE COBERTURA")
    print("-" * 40)
    print(censo.iloc[:, 1].value_counts(dropna=False))

    print("\n3. VALORES DE EDAD")
    print("-" * 40)
    print(censo.iloc[:, 2].value_counts(dropna=False).head(30))

    print("\n4. CANTIDAD DE MUJERES")
    print("-" * 40)

    mujeres = censo.iloc[:, 4]

    print("Valores nulos:", mujeres.isna().sum())
    print("Valores '-':", (mujeres.astype(str).str.strip() == "-").sum())

    mujeres_numericas = pd.to_numeric(mujeres, errors="coerce")

    print(
        "Valores que no son números:",
        mujeres_numericas.isna().sum() - mujeres.isna().sum()
    )

    print("\nValores no numéricos encontrados:")
    print(
        mujeres[
            mujeres_numericas.isna() & mujeres.notna()
        ].value_counts()
    )


    print("\n5. CANTIDAD DE HOMBRES")
    print("-" * 40)

    hombres = censo.iloc[:, 3]

    print("Valores nulos:", hombres.isna().sum())

    hombres_numericos = pd.to_numeric(hombres, errors="coerce")

    print(
        "Valores que no son números:",
        hombres_numericos.isna().sum() - hombres.isna().sum()
    )

    print("\nValores no numéricos encontrados:")
    print(
        hombres[
            hombres_numericos.isna() & hombres.notna()
        ].value_counts()
    )

    print("\n6. TOTAL")
    print("-" * 40)

    total = censo.iloc[:, 5]

    print("Valores nulos:", total.isna().sum())

    total_numerico = pd.to_numeric(total, errors="coerce")

    print(
        "Valores que no son números:",
        total_numerico.isna().sum() - total.isna().sum()
    )

    print("\nValores no numéricos encontrados:")
    print(
        total[
            total_numerico.isna() & total.notna()
        ].value_counts()
    )

    print("\n7. FILAS QUE IDENTIFICAN PROVINCIAS")
    print("-" * 40)

    filas_area = censo[
        censo.iloc[:, 1].astype(str).str.startswith("AREA")
    ]

    print("Cantidad de filas AREA:", len(filas_area))
    print("\nEjemplos:")
    print(filas_area.head(10))

    print("\n8. FILAS CON TOTAL")
    print("-" * 40)

    filas_total = censo[
        censo.astype(str)
        .apply(lambda columna:
               columna.str.strip().str.lower().eq("total"))
        .any(axis=1)
    ]

    print("Cantidad de filas con algún TOTAL:", len(filas_total))
    print("\nEjemplos:")
    print(filas_total.head(10))


    print("\n9. VALORES NULOS POR COLUMNA")
    print("-" * 40)
    print(censo.isna().sum())


    print("\n10. DIMENSIONES")
    print("-" * 40)
    print("Filas:", censo.shape[0])
    print("Columnas:", censo.shape[1])

#Aca hay dos cosas para hacer: generar la tabla de Censos y la de la tabla que la relaciona con provincia 
def normalizar_datos_censo(censo):
    censo_limpio = censo.drop(columns= 0) # eliminamos la primera columna que eran todos Nan
    censo_limpio.columns =['cobertura', 'edad', 'cantidad_hombres', 'cantidad_mujeres', 'total'] # Definimos las columnas con los valores que queremos
    
    censo_limpio['provincia'] = None #Iniciamos una nueva columna cuyos valores son NaN
    provincia_actual = None 
    
    for i in range(len(censo_limpio)):
        fila = censo_limpio.iloc[i] 
    
        if str(fila.iloc[0]).startswith("AREA"): #En este punto sabemos que las provincias estaban separadas por "Area" en la columna de cobertura, y el nombre de la privncia en la columna de Edad
            provincia_actual = fila.iloc[1] #Nos quedamos con el nombre de la provincia
    
        censo_limpio.loc[i, "provincia"] = provincia_actual #Agregamos 
    
    
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
    
    
    #Hay que normalizar los datos entre las dos tablas
    censo_limpio["cobertura"] = censo_limpio["cobertura"].replace({
        "Programas o planes estatales de salud": "Con cobertura",
        "Obra social o prepaga (incluye PAMI)": "Con cobertura",
        "Obra social (incluye PAMI)": "Con cobertura",
        "Prepaga a través de obra social": "Con cobertura",
        "Prepaga sólo por contratación voluntaria": "Con cobertura",
        "No tiene obra social, prepaga ni plan estatal": "Sin cobertura",
        "No tiene obra social, prepaga o plan estatal": "Sin cobertura"
        })
    #Hay que ver si es valida para la materia
    
    #Sacamos la pseudo tablita de los totales (la podemos calcular nosotros a mano, es redundante)
    censo_limpio = censo_limpio[
    (censo_limpio["edad"].astype(str).str.strip().str.lower() != "total") &
    (censo_limpio["cobertura"].astype(str).str.strip().str.lower() != "total") &
    (censo_limpio["edad"].astype(str).str.strip().str.lower() != "edad") &
    (censo_limpio["total"].astype(str).str.strip().str.lower() != "total") &
    (censo_limpio["cobertura"].astype(str).str.strip().str.lower() != "resumen")
    ]
    
    censo_limpio["cantidad_mujeres"] = censo_limpio["cantidad_mujeres"].replace("-", 0)
    censo_limpio["cantidad_hombres"] = censo_limpio["cantidad_hombres"].replace("-", 0)
    
   
    return censo_limpio
    
#vemos un poco el analisis
analizar_censo(censo2010)
analizar_censo(censo2022)

#dentro de la funcion encontramos mas cosas como que los nomrbes entre las tablas eran distintas (en un solo caso) pero esta todo bien comentado
dfcenso2022_limpio = normalizar_datos_censo(censo2022)
dfcenso2022_limpio.to_csv(carpetaLimpias / "censo2022.csv")
dfcenso2010_limpio = normalizar_datos_censo(censo2010)
dfcenso2010_limpio.to_csv(carpetaLimpias / "censo2010.csv")

#Ahora agregamos la columna de año a cada uno y los juntamos en una misma tabla
dfcenso2022_limpio["año"] = 2022
dfcenso2010_limpio["año"] = 2010

tablaRelacion = pd.concat([dfcenso2010_limpio, dfcenso2022_limpio])
tablaCensos = tablaRelacion.drop(columns = ["cantidad_mujeres", "cantidad_hombres", "total", "provincia_id"])
tablaRelacion = tablaRelacion.drop(columns = ["total"]).dropna() #Sacamos la columna de total que era redundante

#Chequeamos dependencias funcionales
tablaRelacion.groupby(["cobertura",  "edad", "provincia_id", "año"])[["cantidad_mujeres", "cantidad_hombres"]].nunique() 
#Como no quedo bien, suponemos, logicamente que al cambiarla por Con cobertura y Sin cobertura, vamos a sumar los que son iguales
tablaRelacion = (
    tablaRelacion
    .groupby(
        ["cobertura", "edad", "provincia_id", "año"],
        as_index=False
    )[["cantidad_mujeres", "cantidad_hombres"]]
    .sum()
)

tablaRelacion.to_csv(carpetaModelos / "se_registran_censos.csv")
tablaCensos.to_csv(carpetaModelos / "censos.csv")
#Volvemos a chequear
tablaRelacion.groupby(["cobertura",  "edad", "provincia_id", "año"])[["cantidad_mujeres", "cantidad_hombres"]].nunique() 
#Queda una clave primaria compuesta de: cobertura, edad, provincia_id, año


#%%Analizamos la tabla de nacidos de 2022 y nacidos 2010
#Aca podemos ver que no es tan obvio lo que nos quiere expresar el csv

def ver_valores_nacidos(nacidos):
    print("=" * 60)
    print("ANÁLISIS DE NACIDOS VIVOS")
    print("=" * 60)
    
    print("\n1. DATOS VACÍOS")
    print("-" * 40)
    print(nacidos.isna().sum()) #No encontramos ninguno pero sin embargo existen datos sin especificar
    
    print("\n2. PESO AL NACER")
    print("-" * 40)
    print(nacidos["IPESONAC"].value_counts())
    
    print("\n3. SEXO")
    print("-" * 40)
    print(nacidos["SEXO"].value_counts())
    
    print("\n4. GRUPO DE EDAD DE LA MADRE")
    print("-" * 40)
    print(nacidos["IMEDAD"].value_counts())
    
    print("\n5. TIEMPO DE GESTACIÓN")
    print("-" * 40)
    print(nacidos["ITIEMGEST"].value_counts())
    
    print("\n6. NIVEL EDUCATIVO DE LA MADRE")
    print("-" * 40)
    print(nacidos["IMINSTRUC"].value_counts())
    
ver_valores_nacidos(nacidos2010)
ver_valores_nacidos(nacidos2022)

#En todos estos aparece un numero n y n.Sin especificar 
# sirve de algo tener datos vacios en este caso? Los puedo eliminar? Veremos mas adelante en las consultas
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



def modificar_tabla(columnas, tabla):
    #renombrar columnas a columnas mas declarativas
    tabla = tabla.rename(columns={
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
        tabla[columna] = tabla[columna].str.replace(
            r"^\d+\.", "", regex=True
        ).str.strip()
        
    #Cambiamos los valores que no se entienden
    tabla["sexo"] = tabla["sexo"].replace({
        1: "Varón",
        2: "Mujer",
        9: "Sin especificar"
    })
    tabla["tipo_parto"] = tabla["tipo_parto"].replace({
        1: "Simple",
        2: "Múltiple",
        9: "Sin especificar"
    })
    
    return tabla


nacidos2022_limpio = modificar_tabla(columnas_a_limpiar, nacidos2022)
nacidos2022_limpio["año"] = 2022
nacidos2022_limpio.to_csv(carpetaLimpias / "nacidos2022.csv")


nacidos2010_limpio = modificar_tabla(columnas_a_limpiar, nacidos2010)
nacidos2010_limpio["año"] = 2010
nacidos2010_limpio.to_csv(carpetaLimpias / "nacidos2010.csv")


tablaRelacion2 = pd.concat([nacidos2022_limpio, nacidos2010_limpio])

tablaRelacion2.to_csv(carpetaModelos / "se_registran_nacidos.csv")

tablaNacidos = tablaRelacion2.drop(columns = ["provincia_residencia", "cantidad"]).drop_duplicates()
tablaNacidos.to_csv(carpetaModelos / "nacidos.csv")
#dependencia funcional
tablaRelacion2.groupby(["provincia_residencia", "tipo_parto", "sexo", "grupo_edad_madre", "grupo_semanas_gestacion", "nivel_educativo_madre",  "peso_nacimiento", "año"])["cantidad"].nunique().loc[lambda x : x>1]
#Todas las columnas son una clave


#%% Tabla establecimientos

# Analizamos tabla establecimientos
def ver_valores_establecimientos(establecimientos):
    print("=" * 60)
    print("ANÁLISIS DE ESTABLECIMIENTOS")
    print("=" * 60)
    
    print("\n1. COLUMNAS DE LA TABLA")
    print("-" * 40)
    print(establecimientos.columns)
    
    print("\n2. INFORMACIÓN DE LA TABLA")
    print("-" * 40)
    print(establecimientos.info())
    
    print("\n3. DATOS VACÍOS")
    print("-" * 40)
    print(establecimientos.isna().sum())
    
    print("\n4. REGISTROS DUPLICADOS")
    print("-" * 40)
    print(establecimientos[establecimientos.duplicated(keep=False)])
    
    print("\n5. ORIGEN DE FINANCIAMIENTO")
    print("-" * 40)
    print(establecimientos["origen_financiamiento"].value_counts(dropna=False))
    
    print("\n6. SIGLAS DE TIPOLOGÍA")
    print("-" * 40)
    print(establecimientos["tipologia_sigla"].value_counts(dropna=False))
    
    print("\n7. NOMBRES DE TIPOLOGÍA")
    print("-" * 40)
    print(establecimientos["tipologia_nombre"].value_counts(dropna=False))
    
    print("\n8. RELACIÓN ENTRE TIPOLOGÍA, SIGLA, NOMBRE E ID")
    print("-" * 40)
    
    print("\n¿Una sigla tiene más de un ID?")
    print(establecimientos.groupby("tipologia_sigla")["tipologia_id"].nunique()
          .loc[lambda x: x > 1])
    
    print("\n¿Un nombre tiene más de un ID?")
    print(establecimientos.groupby("tipologia_nombre")["tipologia_id"].nunique()
          .loc[lambda x: x > 1])
    
    print("\n¿Una sigla tiene más de un nombre?")
    print(establecimientos.groupby("tipologia_sigla")["tipologia_nombre"].nunique()
          .loc[lambda x: x > 1])
    
    print("\n¿Un ID tiene más de una sigla?")
    print(establecimientos.groupby("tipologia_id")["tipologia_sigla"].nunique()
          .loc[lambda x: x > 1])
    
    print("\n¿Un ID tiene más de un nombre?")
    print(establecimientos.groupby("tipologia_id")["tipologia_nombre"].nunique()
          .loc[lambda x: x > 1])
    
    print("\n9. DEPENDENCIAS FUNCIONALES")
    print("-" * 40)
    
    print("\n¿(provincia_id, departamento_id) -> departamento_nombre?")
    print(
        establecimientos
        .groupby(["provincia_id", "departamento_id"])
        .agg({"departamento_nombre": "nunique"})
        .query("departamento_nombre > 1")
    )
    
    print("\n¿localidad_id -> departamento_id?")
    print(
        establecimientos
        .groupby("localidad_id")
        .agg({"departamento_id": "nunique"})
        .query("departamento_id > 1")
    )
    
    print("\n¿localidad_id -> provincia_id?")
    print(
        establecimientos
        .groupby("localidad_id")
        .agg({"provincia_id": "nunique"})
        .query("provincia_id > 1")
    )
    
    print("\n¿localidad_id -> localidad_nombre?")
    print(
        establecimientos
        .groupby("localidad_id")
        .agg({"localidad_nombre": "nunique"})
        .query("localidad_nombre > 1")
    )
    
    print("\n¿establecimiento_id -> provincia_id?")
    print(
        establecimientos
        .groupby("establecimiento_id")
        .agg({"provincia_id": "nunique"})
        .query("provincia_id > 1")
    )
    
    print("\n¿establecimiento_id -> departamento_id?")
    print(
        establecimientos
        .groupby("establecimiento_id")
        .agg({"departamento_id": "nunique"})
        .query("departamento_id > 1")
    )

#La conclusion de todo esto es que localidadid tiene problemas pues esta formado por:provinciaid, codloc, deptoid, codent
#y vimos que hay algunos de esos que son null y en algunos pocos casos, (que lo vimos a ojo), estan mal cargados
   
        
ver_valores_establecimientos(establecimientos)


establecimientos["origen_financiamiento"] = establecimientos["origen_financiamiento"].replace({
    "Provincial": "Estatal",
    "Municipal": "Estatal",
    "FFAA/Seguridad": "Estatal",
    "Nacional": "Estatal",
    "Servicio Penitenciario Provincial": "Estatal",
    "Universitario público": "Estatal",
    "Servicio Penitenciario Federal": "Estatal",
    
    "Mutual": "Privado",
    "Universitario privado": "Privado"
})


#Me gustaria cambiar el departmanto id aprovechando su relacion con provincia id
establecimientos["depto_id"] = establecimientos["provincia_id"].astype(str).str.zfill(2) + establecimientos["departamento_id"].astype(str).str.zfill(3)
departamentos = establecimientos[["depto_id", "departamento_nombre", "provincia_id"]].drop_duplicates()
establecimientos_limpio = establecimientos[["establecimiento_id", "establecimiento_nombre", "origen_financiamiento", "depto_id","tipologia_nombre"]]
departamentos.to_csv(carpetaModelos / "departamentos.csv")
establecimientos_limpio.to_csv(carpetaModelos / "establecimientos.csv")



#%% Consultas (archivos)
censo = pd.read_csv(carpetaModelos / 'censos.csv')
se_registran_censos = pd.read_csv(carpetaModelos / "se_registran_censos.csv")
departamentos = pd.read_csv(carpetaModelos / 'departamentos.csv')
provincias = pd.read_csv(carpetaModelos / "provincias.csv")
nacidos = pd.read_csv(carpetaModelos / "nacidos.csv")
se_registran_nacidos = pd.read_csv(carpetaModelos / "se_registran_nacidos.csv")
establecimientos = pd.read_csv(carpetaModelos / "establecimientos.csv")



#%% Cobertura de salud

#Hay que cambiar los rangos de edad, no se bien cual poner

consulta = """
        SELECT
        p.provincia,

        CASE
            WHEN src.edad BETWEEN 0 AND 14 THEN '0-14'
            WHEN src.edad BETWEEN 15 AND 29 THEN '15-29'
            WHEN src.edad BETWEEN 30 AND 44 THEN '30-44'
            WHEN src.edad BETWEEN 45 AND 64 THEN '45-64'
            WHEN src.edad >= 65 THEN '65+'
        END AS grupo_etario,

        SUM(
            CASE
                WHEN src.cobertura = 'Con cobertura'
                 AND src.año = 2010
                THEN src.cantidad_mujeres + src.cantidad_hombres
                ELSE 0
            END
        ) AS habitantes_con_cobertura_2010,

        SUM(
            CASE
                WHEN src.cobertura = 'Sin cobertura'
                 AND src.año = 2010
                THEN src.cantidad_mujeres + src.cantidad_hombres
                ELSE 0
            END
        ) AS habitantes_sin_cobertura_2010,

        SUM(
            CASE
                WHEN src.cobertura = 'Con cobertura'
                 AND src.año = 2022
                THEN src.cantidad_mujeres + src.cantidad_hombres
                ELSE 0
            END
        ) AS habitantes_con_cobertura_2022,

        SUM(
            CASE
                WHEN src.cobertura = 'Sin cobertura'
                 AND src.año = 2022
                THEN src.cantidad_mujeres + src.cantidad_hombres
                ELSE 0
            END
        ) AS habitantes_sin_cobertura_2022

    FROM se_registran_censos src

    INNER JOIN provincias p
        ON p.codigo = src.provincia_id

    WHERE src.año IN (2010, 2022)

    GROUP BY
        p.provincia,
        grupo_etario

    ORDER BY
        p.provincia,
        grupo_etario
"""

dataframeResultado = dd.sql(consulta).df()

dataframeResultado.to_csv(
    raiz / "consulta_cobertura_de_salud.csv",
    index=False
)

#%% Establecimientos de terapia intensiva
consulta = """
    SELECT
        depto_id,
        COUNT(*) AS cantidad
    FROM departamentos
    GROUP BY depto_id
    HAVING COUNT(*) > 1
"""
print(dd.sql(consulta).df())
consulta = """
    SELECT
        COUNT(*) AS filas_join,
        COUNT(DISTINCT e.establecimiento_id) AS establecimientos_distintos
    FROM establecimientos e
    INNER JOIN departamentos d
        ON d.depto_id = e.depto_id
"""
print(dd.sql(consulta).df())
consulta_establecimientos_terapia_intensiva = """
            SELECT 
                p.provincia, 
                e.origen_financiamiento, 
                COUNT(e.establecimiento_id) AS cantidad 
        
            FROM establecimientos e
        
            INNER JOIN departamentos d
                ON d.depto_id = e.depto_id
        
            INNER JOIN provincias p
                ON p.codigo = d.provincia_id
        
            WHERE e.origen_financiamiento IN ('Estatal', 'Privado') 
              AND LOWER(e.tipologia_nombre) LIKE '%terapia intensiva%'
        
            GROUP BY 
                p.provincia, 
                e.origen_financiamiento
        
            ORDER BY
                p.provincia,
                e.origen_financiamiento
        """

dataframeResultado = dd.sql(consulta_establecimientos_terapia_intensiva).df()

dataframeResultado.to_csv(raiz / "consulta_establecimientos_terapia_intensiva.csv",index=False)

#%% características de los nacimientos 
consulta = """
    SELECT
        grupo_edad_madre,
        tipo_parto,
        año,
        grupo_semanas_gestacion,
        peso_nacimiento,
        nivel_educativo_madre,
        sexo,
        COUNT(*) AS cantidad_filas
    FROM nacidos
    GROUP BY
        grupo_edad_madre,
        tipo_parto,
        año,
        grupo_semanas_gestacion,
        peso_nacimiento,
        nivel_educativo_madre,
        sexo
    HAVING COUNT(*) > 1
"""

df = dd.sql(consulta).df()
print(df)

consulta_caracteristicas_nacimientos = """
            SELECT 
                p.provincia,
                n.grupo_edad_madre,
                n.año,
        
                SUM(srn.cantidad) AS cantidad_nacidos,
        
                SUM(
                    CASE
                        WHEN n.peso_nacimiento = 'Menos de 2500 gramos'
                        THEN srn.cantidad
                        ELSE 0
                    END
                ) AS cantidad_bajo_peso,
        
                100.0 * SUM(
                    CASE
                        WHEN n.peso_nacimiento = 'Menos de 2500 gramos'
                        THEN srn.cantidad
                        ELSE 0
                    END
                ) / NULLIF(
                    SUM(
                        CASE
                            WHEN n.peso_nacimiento != 'Sin especificar'
                            THEN srn.cantidad
                            ELSE 0
                        END
                    ),
                    0
                ) AS porcentaje_bajo_peso
        
            FROM nacidos n
        
            INNER JOIN se_registran_nacidos srn
                ON srn.grupo_edad_madre = n.grupo_edad_madre
                AND srn.tipo_parto = n.tipo_parto
                AND srn.año = n.año
                AND srn.grupo_semanas_gestacion = n.grupo_semanas_gestacion
                AND srn.peso_nacimiento = n.peso_nacimiento
                AND srn.nivel_educativo_madre = n.nivel_educativo_madre
                AND srn.sexo = n.sexo
        
            INNER JOIN provincias p
                ON p.codigo = srn.provincia_residencia
        
            WHERE n.grupo_edad_madre != 'Sin especificar'
            
            GROUP BY
                p.provincia,
                n.grupo_edad_madre,
                n.año
        
            ORDER BY
                p.provincia ASC,
                n.grupo_edad_madre ASC,
                n.año ASC
        """

dataframeResultado = dd.sql(consulta_caracteristicas_nacimientos).df()

dataframeResultado.to_csv(
    raiz / "caracteristicas_nacimientos.csv",
    index=False
)

#%% Tasa de fecundidad por provincia
consulta = """
    SELECT
        provincia_id,
        año,
        cobertura,
        edad,
        COUNT(*) AS cantidad_filas
    FROM se_registran_censos
    GROUP BY
        provincia_id,
        año,
        cobertura,
        edad
    HAVING COUNT(*) > 1
"""
print(dd.sql(consulta).df())
consulta_fecundidad = """
                        SELECT
                        p.provincia,
                        n.grupo_edad_madre,
                
                        1000.0 * n.cantidad_nacimientos
                        / NULLIF(m.cantidad_mujeres, 0) AS tasa_fecundidad
                
                    FROM (
                        SELECT
                            srn.provincia_residencia,
                            nac.grupo_edad_madre,
                            SUM(srn.cantidad) AS cantidad_nacimientos
                
                        FROM nacidos nac
                
                        INNER JOIN se_registran_nacidos srn
                            ON srn.grupo_edad_madre = nac.grupo_edad_madre
                            AND srn.tipo_parto = nac.tipo_parto
                            AND srn.año = nac.año
                            AND srn.grupo_semanas_gestacion = nac.grupo_semanas_gestacion
                            AND srn.peso_nacimiento = nac.peso_nacimiento
                            AND srn.nivel_educativo_madre = nac.nivel_educativo_madre
                            AND srn.sexo = nac.sexo
                
                        WHERE nac.año = 2022
                
                        GROUP BY
                            srn.provincia_residencia,
                            nac.grupo_edad_madre
                    ) n
                
                    INNER JOIN (
                        SELECT
                            src.provincia_id,
                
                            CASE
                                WHEN src.edad BETWEEN 0 AND 14 THEN 'Menor de 15'
                                WHEN src.edad BETWEEN 15 AND 19 THEN '15 a 19'
                                WHEN src.edad BETWEEN 20 AND 24 THEN '20 a 24'
                                WHEN src.edad BETWEEN 25 AND 29 THEN '25 a 29'
                                WHEN src.edad BETWEEN 30 AND 34 THEN '30 a 34'
                                WHEN src.edad BETWEEN 35 AND 39 THEN '35 a 39'
                                WHEN src.edad BETWEEN 40 AND 44 THEN '40 a 44'
                                WHEN src.edad >= 45 THEN 'De 45 y más'
                            END AS grupo_edad,
                
                            SUM(src.cantidad_mujeres) AS cantidad_mujeres
                
                        FROM se_registran_censos src
                
                        WHERE src.año = 2022
                
                        GROUP BY
                            src.provincia_id,
                            grupo_edad
                    ) m
                
                        ON m.provincia_id = n.provincia_residencia
                        AND m.grupo_edad = n.grupo_edad_madre
                
                    INNER JOIN provincias p
                        ON p.codigo = n.provincia_residencia
                
                    ORDER BY
                        p.provincia,
                        n.grupo_edad_madre
                """

dataframeResultado = dd.sql(consulta_fecundidad).df()

dataframeResultado.to_csv(
    raiz / "tasa_fecundidad_provincia.csv",
    index=False
)
           
#%% Cambios en la edad de las madres

consulta_cambios_en_madres = """
    SELECT
        p.provincia,

        100.0 * SUM(
            CASE
                WHEN n.año = 2010
                 AND n.grupo_edad_madre IN ('Menor de 15', '15 a 19')
                THEN srn.cantidad
                ELSE 0
            END
        ) / NULLIF(
            SUM(
                CASE
                    WHEN n.año = 2010
                    THEN srn.cantidad
                    ELSE 0
                END
            ), 0
        ) AS porcentaje_2010,

        100.0 * SUM(
            CASE
                WHEN n.año = 2022
                 AND n.grupo_edad_madre IN ('Menor de 15', '15 a 19')
                THEN srn.cantidad
                ELSE 0
            END
        ) / NULLIF(
            SUM(
                CASE
                    WHEN n.año = 2022
                    THEN srn.cantidad
                    ELSE 0
                END
            ), 0
        ) AS porcentaje_2022,

        (
            100.0 * SUM(
                CASE
                    WHEN n.año = 2022
                     AND n.grupo_edad_madre IN ('Menor de 15', '15 a 19')
                    THEN srn.cantidad
                    ELSE 0
                END
            ) / NULLIF(
                SUM(
                    CASE
                        WHEN n.año = 2022
                        THEN srn.cantidad
                        ELSE 0
                    END
                ), 0
            )
        )
        -
        (
            100.0 * SUM(
                CASE
                    WHEN n.año = 2010
                     AND n.grupo_edad_madre IN ('Menor de 15', '15 a 19')
                    THEN srn.cantidad
                    ELSE 0
                END
            ) / NULLIF(
                SUM(
                    CASE
                        WHEN n.año = 2010
                        THEN srn.cantidad
                        ELSE 0
                    END
                ), 0
            )
        ) AS cambio

    FROM nacidos n

    INNER JOIN se_registran_nacidos srn
        ON srn.grupo_edad_madre = n.grupo_edad_madre
        AND srn.tipo_parto = n.tipo_parto
        AND srn.año = n.año
        AND srn.grupo_semanas_gestacion = n.grupo_semanas_gestacion
        AND srn.peso_nacimiento = n.peso_nacimiento
        AND srn.nivel_educativo_madre = n.nivel_educativo_madre
        AND srn.sexo = n.sexo

    INNER JOIN provincias p
        ON p.codigo = srn.provincia_residencia

    GROUP BY p.provincia
    ORDER BY cambio
"""
dataframeResultado = dd.sql(consulta_cambios_en_madres).df()

dataframeResultado.to_csv(
    raiz / "consulta_cambios_en_madres.csv",
    index=False
)

#%% Visualizaciones 
#cantidad de habitantes por provincia
consulta_habitantes_provincia = """
            SELECT
            p.nombre AS provincia,
    
            SUM(
                CASE
                    WHEN c.año = 2010
                    THEN src.cantidad_mujeres + src.cantidad_hombres
                    ELSE 0
                END
            ) AS cantidad_habitantes_2010,
    
            SUM(
                CASE
                    WHEN c.año = 2022
                    THEN src.cantidad_mujeres + src.cantidad_hombres
                    ELSE 0
                END
            ) AS cantidad_habitantes_2022
    
        FROM censo c
    
        INNER JOIN se_registran_censo src
            ON src.cobertura = c.cobertura
            AND src.año = c.año
            AND src.edad = c.edad
    
        INNER JOIN provincia p
            ON p.codigo = src.provincia_id
    
        WHERE c.año IN (2010, 2022)
    
        GROUP BY
            p.nombre
    
        ORDER BY
            cantidad_habitantes_2022 DESC
    """

dataframeResultado = dd.sql(consulta_habitantes_provincia).df()
print(dataframeResultado)
