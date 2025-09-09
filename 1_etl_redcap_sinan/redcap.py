import os
import requests
import psycopg2
from dotenv import load_dotenv
# PERGUNTAR PARA ANDERSON COMO ELE RODARIA EM QUANTO EM QUANTO TEMPO O SCRIPT DO REDCAP.PY (ESSE ARQUIVO). JUNTAMENTE COM O SCRIPT 
# DO carga_violencia.py DA API (OUTRO PROJETO) QUE É RESPONSAVEL POR CARREGAR OS DADOS DO REDCAP PARA O BANCO DA API.
load_dotenv()

REDCAP_API = os.getenv("REDCAP_API")
REDCAP_TOKEN = os.getenv("REDCAP_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def getRespostasRedCap(token):
    payload = {
        'token': token,
        'content': 'record',
        'action': 'export',
        'format': 'json',
        'type': 'eav',
        'csvDelimiter': ';',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'true',
        'exportSurveyFields': 'true',
        'exportDataAccessGroups': 'true',
        'returnFormat': 'json'
    }

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'python-script'
    }

    response = requests.post(REDCAP_API, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro: {response.status_code}")
        return []

def salvar_no_postgres(data):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS redcap_respostas (
            record TEXT,
            field_name TEXT,
            value TEXT
        )
    """)
    conn.commit()

    for row in data:
        cur.execute(
            "INSERT INTO redcap_respostas (record, field_name, value) VALUES (%s, %s, %s)",
            (row.get("record"), row.get("field_name"), row.get("value"))
        )

    conn.commit()
    cur.close()
    conn.close()

data = getRespostasRedCap(REDCAP_TOKEN)
salvar_no_postgres(data)