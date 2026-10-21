-- El total de cada embarque debe ser peso * precio + flete (tolerancia 0.05 USD)
select id_embarque, peso_oro_quintales, precio_quintal_usd, flete_transporte_usd, total_usd
from {{ ref('fct_embarques') }}
where abs(total_usd - (peso_oro_quintales * precio_quintal_usd + flete_transporte_usd)) > 0.05
