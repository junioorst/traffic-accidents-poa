-- Vítimas com as colunas relevantes, prontos para uso nos modelos de análise.

with origem as (
    select * from {{ source('raw', 'vitimas') }}
),

limpo as (
    select
        id,
        idacidente,
        idade,
        sexo,
        sit_vitima,
        fx_et,
        tipo_veic,
        periododia
    from origem
)

select * from limpo
