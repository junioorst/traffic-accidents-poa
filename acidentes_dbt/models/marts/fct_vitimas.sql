with vitimas as (
    select * from {{ ref('stg_vitimas') }}
),

acidentes as (
    select * from {{ ref('stg_acidentes') }}
),

final as (
    select
        v.id,
        v.idacidente,
        v.idade,
        v.fx_et,
        v.sexo,
        v.sit_vitima,
        v.tipo_veic,
        v.periododia,
        a.data,
        a.hora,
        a.dia_sem,
        a.regiao,
        a.tipo_acid
        from vitimas as v
        inner join acidentes as a on v.idacidente = a.idacidente
)

select * from final