{{ config(materialized='table') }}

select
    id_beneficio,
    nombre_beneficio,
    tipo_beneficio,
    municipio,
    latitud,
    longitud,
    capacidad_quintales_dia,
    costo_procesamiento_qq
from {{ ref('stg_beneficios') }}
where id_beneficio is not null
