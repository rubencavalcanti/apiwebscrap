from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
from coletor_dominios import coletar_dominios_e_numeros_telefone
from starlette.responses import FileResponse

app = FastAPI()

# Definindo o diretório para armazenamento dos arquivos CSV
diretorio_csvs = os.path.join(os.getcwd(), "csvs")

class Pesquisa(BaseModel):
    termo_pesquisa: str
    numero_paginas: Optional[int] = 100

@app.post("/coletar_dominios")
async def coletar_dominios(pesquisa: Pesquisa):
    termo_pesquisa = pesquisa.termo_pesquisa
    numero_paginas = pesquisa.numero_paginas
    coletar_dominios_e_numeros_telefone(termo_pesquisa, numero_paginas)
    return {"message": f"Domínios e números de telefone coletados para '{termo_pesquisa}'."}

# Endpoint para listar os arquivos CSV na pasta "csvs"
@app.get("/arquivos_csvs/")
async def listar_arquivos_csvs():
    # Lista todos os arquivos na pasta "csvs"
    arquivos_csvs = os.listdir(diretorio_csvs)
    return {"arquivos_csvs": arquivos_csvs}

# Endpoint para fazer o download de um arquivo CSV específico
@app.get("/download_csv/{nome_arquivo}")
async def baixar_arquivo_csv(nome_arquivo: str):
    # Define o caminho completo para o arquivo CSV
    caminho_arquivo = os.path.join(diretorio_csvs, nome_arquivo)
    
    # Verifica se o arquivo existe
    if os.path.isfile(caminho_arquivo):
        # Retorna o arquivo como resposta, definindo o tipo de conteúdo como CSV
        return FileResponse(caminho_arquivo, media_type="text/csv", filename=nome_arquivo)
    else:
        return {"message": "Arquivo não encontrado"}
