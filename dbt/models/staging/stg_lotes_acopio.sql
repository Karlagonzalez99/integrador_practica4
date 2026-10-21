{{ config(materialized='view') }}
select id_lote, id_finca, id_variedad, id_cuadrilla, fecha_corte, peso_cereza_kg,
       humedad_porcentaje, puntaje_catacion_scaa, certificacion,
       costo_recoleccion_nio, estado_lote
from {{ source('raw', 'lotes_acopio') }}
