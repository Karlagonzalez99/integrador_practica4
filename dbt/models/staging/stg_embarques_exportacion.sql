{{ config(materialized='view') }}
select id_embarque, id_lote, puerto_salida, pais_destino, cliente_comprador,
       fecha_embarque, peso_oro_quintales, precio_quintal_usd,
       flete_transporte_usd, total_usd
from {{ source('raw', 'embarques_exportacion') }}
