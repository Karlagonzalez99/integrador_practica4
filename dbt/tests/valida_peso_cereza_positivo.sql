-- Todo lote debe tener un peso de cereza mayor que cero
select id_lote, peso_cereza_kg
from {{ ref('fct_lotes_acopio') }}
where peso_cereza_kg <= 0
