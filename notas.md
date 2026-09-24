# Notas
##Siguientes pasos
1. Cambiar el análisis a SQL (profesora no confirmo pero por las dudas)
2. Agregar mas GQM
3. Agregar bien explicito la visualizacion de datos de los censos porque quedo en el aire
4. Revisar consultas
5. Hacer gráficos
6. Elegir gráfico auxiliar
7. Redactar el informe completo

---

## Ideas de gráficos adicionales
1. Proporción de nacimientos por tipo de parto en cada provincia
2. Distribución de nacimientos por sexo
3. Evolución del tipo de parto entre 2010 y 2022

---
## Preguntas
1. Es suficiente el análisis de calidad que hicimos? 
2. Se puede separar en más archivos? 
3. Se puede dejar separado en TablasLimpias? 
4. Se puede usar la tabla extra de provincias que encontramos? 
5. No hay otra cosa mejor que analizar en establecimientos?

---

## Análisis de calidad
### Nacimientos
1. Analizar datos "Sin especificar" y porcentaje con el total
2. Elegimos el mas representativo (educación de madre)

### Establecimientos
1. Analizamos datos null en sitio web

---

##Dependencias funcionales
###Censo
(cobertura, edad, año, provincia_id) -> (total, mujer)

###Nacidos
(provincia_residencia, tipo_parto, sexo, grupo_edad_madre, grupo_semanas_gestacion, nivel_educativo_madre,  peso_nacimiento, año)->("cantidad")

###Establecimientos
(establecimiento_id -> todo)

###Departamento
(departamento_id, provincia_id) -> departamento_nombre

###provincias
(provincia_id) -> (provincia_nombre)

###Tipologia
Aca esta interesante mencionar que la sigla, el id y el nombre no se relacionan entre si

---

##Procesamiento de calidad
###Censo
1. Cambiamos el formato de excel que tenia (filas innecesarias, subtitulos, subtablas de total o resumen adentro de la tabla principal)
2. Habia valores en Mujer que eran "-" en vez de 0
3. Inconsistencia entre 2010 y 2022 con algunos nombres (solo Caba y Ciudad Autonoma de Buenos Aires)
4. Falta poner en el codigo una seccion solamente para ver estas cosas
5. Cambiamos los nombres de cobertura a Con cobertura o Sin cobertura 

###Nacidos
1. Los nombres no eran muy descriptivos
2. Columnas como sexo y tipo de parto tenian el valor como 1,2, 9 y los cambiamos a sus correspondientes (informacion sacada de la tabla descargada)
3. Los datos tenian formato de lista, por ej: "1. Menor a 15", lo retiramos


###Establecimientos
1. La tabla no estaba en 3FN.
2. El 94% de los datos de sitio web eran null
3. Cambiamos el origen de financiamiento a si era Estatal o Privado, los que no sabemos los dejamos como estan
4. Revisamos dependencias funcionales 
5. Sacamos columnas que no aportaban informacion 


