-- Un embarque no puede ocurrir antes de la fecha de corte de su lote
select e.id_embarque, e.fecha as fecha_embarque, l.fecha as fecha_corte
from {{ ref('fct_embarques') }} e
join {{ ref('fct_lotes_acopio') }} l on l.id_lote = e.id_lote
where e.fecha < l.fecha
