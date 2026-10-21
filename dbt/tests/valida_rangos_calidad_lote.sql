-- Humedad y puntaje de catacion deben estar entre 0 y 100; el costo no puede ser negativo
select id_lote, humedad_porcentaje, puntaje_catacion_scaa, costo_recoleccion_nio
from {{ ref('fct_lotes_acopio') }}
where humedad_porcentaje < 0 or humedad_porcentaje > 100
   or puntaje_catacion_scaa < 0 or puntaje_catacion_scaa > 100
   or costo_recoleccion_nio < 0
