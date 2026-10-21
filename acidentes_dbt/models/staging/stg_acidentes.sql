-- Acidentes com datas válidas, prontos para uso nos modelos de análise.

with origem as (                        
    select * from {{ source('raw', 'acidentes') }}
),

limpo as (                                   
    select
        idacidente,
        data,
        hora,
        dia_sem,
        noite_dia,
        regiao,
        log1,
        log2,
        latitude,
        longitude,
        tipo_acid,
        ups,
        feridos,
        feridos_gr,
        mortes,
        morte_post,
        fatais
    from origem
    where data < '2026-10-01'
)

select * from limpo