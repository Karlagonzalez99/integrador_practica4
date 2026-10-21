{{ config(materialized='table') }}

select
    id_variedad,
    nombre_variedad,
    especie,
    perfil_sensorial_base,
    resistencia_roya,
    rendimiento_promedio_qq_mz
from {{ ref('stg_variedades_cafe') }}
where id_variedad is not null
