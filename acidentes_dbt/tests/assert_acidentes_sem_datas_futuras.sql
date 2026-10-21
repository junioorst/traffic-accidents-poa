{{ config(severity='warn') }}

-- Nenhum acidente pode ter data posterior à extração dos dados (01/10/2026).

SELECT
    idacidente,
    data
FROM {{ source('raw', 'acidentes') }}
WHERE data >= '2026-10-01'