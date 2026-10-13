import pandas as pd
import requests
from math import ceil

BASE_URL="http://20.228.134.116:8000/volcan"
MAX_LIMIT_ORDENES=200

def get_num_batches(path: str):

#SOLICITUD DE METADATA 
    res = requests.get(f"{BASE_URL}{path}", params={'limit':1}).json()

# EXTRAER TOTAL DE ITEMS 
    print(res)
    total: int = res["total"]  

#CALCULAR CANTIDAD DE batchs
    num_batchs = ceil(total / MAX_LIMIT_ORDENES)

    return num_batchs

def get_data(path: str):
    dfs = []
    num_batchs = get_num_batches(path)

    for i in range(num_batchs):
        offset = i * MAX_LIMIT_ORDENES
        params = {
            "offset": offset,
            "limit": MAX_LIMIT_ORDENES
        }
        print(f"{i}| obteniendo datos de {path} con: {params}")

        res = requests.get(F"{BASE_URL}{path}", params=params).json()
        print(res['total'])

        #crear dataframe
        batch_df = pd.DataFrame(res["items"])

        dfs.append(batch_df)

    df = pd.concat(dfs)   

    return df 