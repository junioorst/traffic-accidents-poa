with acidentes as (
    select * from {{ ref('stg_acidentes') }}
),

final as (
    select
        idacidente,
        data,
        hora,
        dia_sem,
        regiao,
        log1,
        tipo_acid,
        feridos,
        fatais,
        case ups
            when 1 then 'Danos materiais'
            when 5 then 'Com feridos'
            when 13 then 'Fatal'
        end as gravidade
    from acidentes
)

select * from final