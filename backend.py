import requests
import pandas as pd

BASE_URL = "https://api-finanto.cobansist.cloud"

def login_api(email: str, password: str) -> str:
    """Realiza login e retorna o token."""
    login_url = f"{BASE_URL}/usr/userDoLogin"
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Erro no login: {response.status_code} - {response.text}")
    
    return response.json().get("token")


def extrair_dados(
    token: str,
    data_inicio: str,
    data_fim: str,
    unidades_dict: dict[str, int],
    unidades_selecionadas: list[str]
) -> pd.DataFrame:
    """Consulta a API para as unidades e período selecionados."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/reportResult/resultScreen"
    resultados = []

    for nome_unidade in unidades_selecionadas:
        unidade_id = unidades_dict[nome_unidade]

        payload = {
            "idFinancialTable": "",
            "idTableModel": [],
            "dateType": 4,
            "commissionCompany": {"label": "Esperado", "value": 2},
            "contractNumber": "",
            "finalDate": data_fim,
            "groupBy": {"label": "Convenio", "value": 2},
            "hasReceipt": {"label": "Todos", "value": 0},
            "idCompany": "",
            "idFinancial": "",
            "idGroupProduct": "",
            "idProduct": "",
            "idProductModality": "",
            "idPromoter": "",
            "idSubGroupProduct": "",
            "idTableCommission": "",
            "idUser": "",
            "idUserCommercial": "",
            "idUserExecutive": "",
            "idUserMultiStore": "",
            "idUserRegion": "",
            "idUserUnit": unidade_id,
            "individualCommission": {"label": "Todas", "value": 1},
            "initialDate": data_inicio,
            "justSaleMonth": {"label": "Originadas no Mes", "value": 1},
            "loginFinancial": "",
            "commercialClosing": {"label": "Todos", "value": 2}
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json().get("result", [])
            if data:
                df_temp = pd.DataFrame(data)
                df_temp["unidade"] = nome_unidade
                df_temp["idUserUnit"] = unidade_id
                df_temp["data_inicio"] = data_inicio
                df_temp["data_fim"] = data_fim
                resultados.append(df_temp)
        else:
            print(f"Erro {response.status_code} ao consultar unidade {nome_unidade}")

    if not resultados:
        return pd.DataFrame()

    df_final = pd.concat(resultados, ignore_index=True)

    # Seleciona apenas as colunas úteis
    colunas = [
        "data_inicio", "data_fim", "unidade", "idUserUnit",
        "description", "quantity", "baseValue", "valuePaid", 
        "resultFromReceived"
    ]
    colunas_existentes = [c for c in colunas if c in df_final.columns]
    return df_final[colunas_existentes]