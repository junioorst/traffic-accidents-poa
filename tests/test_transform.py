import pandas as pd

from transform import transform_numeric_types


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
