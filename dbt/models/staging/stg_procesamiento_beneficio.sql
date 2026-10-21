{{ config(materialized='view') }}
select id_proceso, id_lote, id_beneficio, etapa, fecha_inicio, fecha_fin,
       merma_porcentaje, peso_salida_kg
from {{ source('raw', 'procesamiento_beneficio') }}
