{{ config(materialized='view') }}
select id_variedad, nombre_variedad, especie, perfil_sensorial_base,
       resistencia_roya, rendimiento_promedio_qq_mz
from {{ source('raw', 'variedades_cafe') }}
