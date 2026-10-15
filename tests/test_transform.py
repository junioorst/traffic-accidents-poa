import pandas as pd

from transform import transform_numeric_types, transform_date_types, drop_columns, select_columns, replace_unknown_values, transform_age

def test_idacidente_remove_sufixo_e_vira_inteiro():
    df = pd.DataFrame(
        {
            "idacidente": ["678074,0", "678080,0"],
            "queda_arr": [0.0, 1.0],
        }
    )

    resultado = transform_numeric_types(df)

    assert resultado["idacidente"].tolist() == [678074, 678080]
    assert resultado["idacidente"].dtype == "int64"


def test_queda_arr_vira_inteiro():
    df = pd.DataFrame(
        {
            "idacidente": ["678074,0", "678080,0"],
            "queda_arr": [0.0, 1.0],
        }
    )

    resultado = transform_numeric_types(df)

    assert resultado["queda_arr"].tolist() == [0, 1]
    assert resultado["queda_arr"].dtype == "int64"
    


def test_data_converte_sem_nulos():
    df = pd.DataFrame(
        {
            "data": ["2021-01-02 00:00:00"],
            "hora": ["12:30:00.0000000"],
        }
    )
    
    resultado = transform_date_types(df)
    assert resultado["data"].isnull().sum() == 0
    assert pd.api.types.is_datetime64_any_dtype(resultado["data"])
    
def test_hora_remove_sufixo_e_preserva_nulo():
    df = pd.DataFrame(
        {
            "data": ["2021-01-02 00:00:00", "2021-01-03 00:00:00"],
            "hora": ["12:30:00.0000000", None],
        }
    )
    
    resultado = transform_date_types(df)
    assert resultado["hora"].isnull().sum() == 1
    
def test_drop_columns_remove_colunas_desnecessarias():
    df = pd.DataFrame(
        {
            "data_extracao": ["2026-10-01 01:34:27"],
            "predial1": [2696.0],
            "consorcio": [None],
            "idacidente": [678074],
        }
    )
    resultado = drop_columns(df)
    assert resultado.columns.tolist() == ["idacidente"]
    
def test_select_columns_mantem_apenas_colunas_da_vitima():
    df = pd.DataFrame(
        {
            "id": [113150],
            "idacidente": [678071],
            "idade": [33.0],
            "sexo": ["MASCULINO"],
            "sit_vitima": ["CONDUTOR"],
            "fx_et": ["26 A 35"],
            "tipo_veic": ["MOTOCICLETA"],
            "periododia": ["NOITE"],
            "log1": ["R FELIPE DE OLIVEIRA"],
        }
    )
    
    resultado = select_columns(df)
    assert resultado.columns.tolist() == ["id", "idacidente", "idade", "sexo", "sit_vitima", "fx_et", "tipo_veic", "periododia"]
    
    
def test_replace_unknown_values_troca_rotulos_por_nulo():
    df = pd.DataFrame(
        {
            "sexo": ["NAO INFORMADO", "FEMININO"],
            "sit_vitima": ["NAOINFORMADO", "CONDUTOR"],
            "fx_et": ["NI", "26 A 35"],
        }
    )
    resultado = replace_unknown_values(df)
    assert resultado["sexo"].isnull().sum() == 1
    assert resultado["sit_vitima"].isnull().sum() == 1
    assert resultado["fx_et"].isnull().sum() == 1
    
    assert resultado["sexo"].iloc[1] == "FEMININO"
    assert resultado["sit_vitima"].iloc[1] == "CONDUTOR"
    assert resultado["fx_et"].iloc[1] == "26 A 35"
    
def test_transform_age_vira_inteiro_e_preserva_nulo():
    df = pd.DataFrame({"idade": [33.0, None]})
    
    resultado = transform_age(df)
    
    assert resultado["idade"].dtype == "Int64"
    assert resultado["idade"].iloc[0] == 33
    assert resultado["idade"].isnull().sum() == 1