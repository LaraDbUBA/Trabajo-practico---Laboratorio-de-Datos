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
  
def analizar_censo(censo):
    print("=" * 60)
    print("ANÁLISIS DEL CENSO")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Columnas y tipos de datos
    # ---------------------------------------------------------
    print("\n1. COLUMNAS Y TIPOS DE DATOS")
    print("-" * 40)
    print(censo.dtypes)

    # ---------------------------------------------------------
    # 2. Valores de cobertura
    # ---------------------------------------------------------
    print("\n2. VALORES DE COBERTURA")
    print("-" * 40)
    print(censo.iloc[:, 1].value_counts(dropna=False))

    # ---------------------------------------------------------
    # 3. Valores de edad
    # ---------------------------------------------------------
    print("\n3. VALORES DE EDAD")
    print("-" * 40)
    print(censo.iloc[:, 2].value_counts(dropna=False).head(30))

    # ---------------------------------------------------------
    # 4. Valores no numéricos en cantidad de mujeres
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 5. Valores no numéricos en cantidad de hombres
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 6. Valores de total
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 7. Filas con AREA
    # ---------------------------------------------------------
    print("\n7. FILAS QUE IDENTIFICAN PROVINCIAS")
    print("-" * 40)

    filas_area = censo[
        censo.iloc[:, 1].astype(str).str.startswith("AREA")
    ]

    print("Cantidad de filas AREA:", len(filas_area))
    print("\nEjemplos:")
    print(filas_area.head(10))

    # ---------------------------------------------------------
    # 8. Filas que contienen TOTAL
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 9. Valores nulos por columna
    # ---------------------------------------------------------
    print("\n9. VALORES NULOS POR COLUMNA")
    print("-" * 40)
    print(censo.isna().sum())

    # ---------------------------------------------------------
    # 10. Cantidad de filas y columnas
    # ---------------------------------------------------------
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

tablaNacidos = tablaRelacion2.drop(columns = ["provincia_residencia", "cantidad"])
tablaNacidos.to_csv(carpetaModelos / "nacidos.csv")
#dependencia funcional
tablaRelacion2.groupby(["provincia_residencia", "tipo_parto", "sexo", "grupo_edad_madre", "grupo_semanas_gestacion", "nivel_educativo_madre",  "peso_nacimiento", "año"])["cantidad"].nunique().loc[lambda x : x>1]
#Todas las columnas son una clave


#%% Tabla establecimientos

# Analizamos tabla establecimientos
def ver_valores_establecimientos(establecimientos):
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


#cambio los Null por "Sin especificar" para evitar inconsistencias y erorres en las consultas
establecimientos["sitio_web"] = establecimientos["sitio_web"].fillna("Sin especificar")
establecimientos["codent"] = establecimientos["codent"].fillna("Sin especificar")


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


#Me gustaria cambiar el departmanto id aprovechando su relacion con provincia id
establecimientos["depto_id"] = establecimientos["provincia_id"].astype(str).str.zfill(2) + establecimientos["departamento_id"].astype(str).str.zfill(3)
departamentos = establecimientos[["depto_id", "departamento_nombre", "provincia_id"]]
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
            SELECT p.provincia,
            
                CASE
                    WHEN c.edad BETWEEN 0 AND 15 THEN '0-14'
                    WHEN c.edad BETWEEN 15 AND 29 THEN '15-29'
                    WHEN c.edad BETWEEN 30 AND 44 THEN '30-44'
                    WHEN c.edad BETWEEN 45 AND 64 THEN '45-64'
                    WHEN c.edad >= 65 THEN '65+'
                END AS grupo_etario,
            
                SUM(
                    CASE
                        WHEN c.cobertura = 'Con cobertura'
                         AND c.año = 2010
                        THEN c.total
                        ELSE 0
                    END
                ) AS habitantes_con_cobertura_2010,
            
                SUM(
                    CASE
                        WHEN c.cobertura = 'Sin cobertura'
                         AND c.año = 2010
                        THEN c.total
                        ELSE 0
                    END
                ) AS habitantes_sin_cobertura_2010,
            
                SUM(
                    CASE
                        WHEN c.cobertura = 'Con cobertura'
                         AND c.año = 2022
                        THEN c.total
                        ELSE 0
                    END
                ) AS habitantes_con_cobertura_2022,
            
                SUM(
                    CASE
                        WHEN c.cobertura = 'Sin cobertura'
                         AND c.año = 2022
                        THEN c.total
                        ELSE 0
                    END
                ) AS habitantes_sin_cobertura_2022
            
            FROM censo c
            
            INNER JOIN provincias p
                ON p.codigo = c.provincia_id
            
            GROUP BY
                p.provincia,
                grupo_etario
            
            ORDER BY
                p.provincia,
                grupo_etario
            """
    
dataframeResultado = dd.sql(consulta).df()
dataframeResultado.to_csv(raiz / "consulta_cobertura_de_salud.csv")

#%% Establecimientos de terapia intensiva

consulta = """
            SELECT 
                p.provincia, 
                e.origen_financiamiento, 
                COUNT(e.establecimiento_id) as cantidad 
            FROM establecimientos e
            
            INNER JOIN provincias as p ON p.codigo = e.provincia_id
            
            WHERE e.origen_financiamiento IN ('Estatal', 'Privado') 
            AND LOWER(e.tipologia_nombre) LIKE '%terapia intensiva%'
            
            GROUP BY p.provincia, e.origen_financiamiento
            
            

           """
dataframeResultado = dd.sql(consulta).df()

dataframeResultado.to_csv(raiz / "consulta_establecimientos_terapia_intensiva.csv")

#%% características de los nacimientos 


consulta = """
        SELECT p.provincia, n.grupo_edad_madre, n.año,
         SUM(n.cantidad) AS cantidad_nacidos,
            SUM(
                CASE
                    WHEN n.peso_nacimiento = 'Menos de 2500 gramos'
                    THEN n.cantidad
                    ELSE 0
                END
            ) AS cantidad_bajo_peso,
            100.0 * SUM(
                CASE
                    WHEN n.peso_nacimiento = 'Menos de 2500 gramos'
                    THEN n.cantidad
                    ELSE 0
                END
            )/ SUM(
                CASE
                    WHEN n.peso_nacimiento != 'Sin especificar'
                    THEN n.cantidad
                    ELSE 0
                END
            ) AS porcentaje_bajo_peso
        
        FROM nacidos n
        
        INNER JOIN provincias p ON p.codigo = n.provincia_residencia
        
        GROUP BY p.provincia, n.grupo_edad_madre, n.año
        
        ORDER BY p.provincia ASC, n.grupo_edad_madre ASC, n.año ASC
        
           """
dataframeResultado = dd.sql(consulta).df()

dataframeResultado.to_csv(raiz / "caracteristicas_nacimientos.csv")

#%% Tasa de fecundidad por provincia

#habria que revisarla bien, le pude haber pifiado 
consulta = """
            SELECT
                p.provincia,
                n.grupo_edad_madre,
                1000.0 * SUM(n.cantidad) / c.mujer AS tasa_fecundidad
            
            FROM nacidos n
            
            INNER JOIN provincias p
                ON p.codigo = n.provincia_residencia
            
            INNER JOIN (
                SELECT
                    provincia_id,
                    CASE
                        WHEN edad BETWEEN 0 AND 14 THEN 'Menor de 15'
                        WHEN edad BETWEEN 15 AND 19 THEN '15 a 19'
                        WHEN edad BETWEEN 20 AND 24 THEN '20 a 24'
                        WHEN edad BETWEEN 25 AND 29 THEN '25 a 29'
                        WHEN edad BETWEEN 30 AND 34 THEN '30 a 34'
                        WHEN edad BETWEEN 35 AND 39 THEN '35 a 39'
                        WHEN edad BETWEEN 40 AND 44 THEN '40 a 44'
                        WHEN edad >= 49 THEN 'De 45 y más'
                    END AS grupo_edad,
                    SUM(mujer) AS mujer
                FROM censo
                WHERE año = 2022
                GROUP BY
                    provincia_id,
                    grupo_edad
            ) c
                ON c.provincia_id = n.provincia_residencia
                AND c.grupo_edad = n.grupo_edad_madre
            
            WHERE n.año = 2022
            
            GROUP BY
                p.provincia,
                n.grupo_edad_madre,
                c.mujer
            
            ORDER BY
                p.provincia,
                n.grupo_edad_madre
            """
dataframeResultado = dd.sql(consulta).df()

dataframeResultado.to_csv(raiz / "tasa_fecundidad_provincia.csv")
           
#%% Cambios en la edad de las madres

consulta = """
            SELECT
                p.provincia,
            
                100.0 * SUM(
                    CASE
                        WHEN n.año = 2010
                         AND n.grupo_edad_madre IN ('15 a 19', 'Menor a 15') 
                        THEN n.cantidad
                        ELSE 0
                    END
                ) / SUM(
                    CASE
                        WHEN n.año = 2010
                        THEN n.cantidad
                        ELSE 0
                    END
                ) AS porcentaje_2010,
            
                100.0 * SUM(
                    CASE
                        WHEN n.año = 2022
                         AND n.grupo_edad_madre IN ('15 a 19', 'Menor a 15')
                        THEN n.cantidad
                        ELSE 0
                    END
                ) / SUM(
                    CASE
                        WHEN n.año = 2022
                        THEN n.cantidad
                        ELSE 0
                    END
                ) AS porcentaje_2022,
            
                ABS((
                    100.0 * SUM(
                        CASE
                            WHEN n.año = 2022
                             AND n.grupo_edad_madre IN ('15 a 19', 'Menor a 15')
                            THEN n.cantidad
                            ELSE 0
                        END
                    ) / SUM(
                        CASE
                            WHEN n.año = 2022
                            THEN n.cantidad
                            ELSE 0
                        END
                    )
                )-
                (
                    100.0 * SUM(
                        CASE
                            WHEN n.año = 2010
                             AND n.grupo_edad_madre IN ('15 a 19', 'Menor a 15')
                            THEN n.cantidad
                            ELSE 0
                        END
                    ) / SUM(
                        CASE
                            WHEN n.año = 2010
                            THEN n.cantidad
                            ELSE 0
                        END
                    )
                )) AS diferencia
            
            FROM nacidos n
            INNER JOIN provincias p
                ON p.codigo = n.provincia_residencia
            
            GROUP BY p.provincia
            
            ORDER BY diferencia DESC
            """
dataframeResultado = dd.sql(consulta).df()

dataframeResultado.to_csv(raiz / "consulta_cambios_en_madres.csv")

#%% Visualizaciones 
#cantidad de habitantes por provincia
consulta = """
            SELECT p.provincia, 
            SUM(CASE WHEN c.año = 2010 THEN c.total ELSE 0 END) AS cantidad_habiantes_2010,
            SUM(CASE WHEN c.año = 2022 THEN c.total ELSE 0 END) AS cantidad_habitantes_2022,
            FROM censo c
            INNER JOIN provincias p
                ON p.codigo = c.provincia_id
            WHERE c.año in(2010,2022)
            GROUP BY p.provincia
            ORDER BY cantidad_habitantes_2022 DESC
            
            """

dataframeResultado = dd.sql(consulta).df()
print(dataframeResultado)
