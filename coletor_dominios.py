import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse, urlunparse
import random
import re
import datetime
import os
import urllib3

# Configuração para desabilitar avisos de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações do proxy
host = 'brd.superproxy.io'
port = 22225
username = 'brd-customer-hl_e9104e6a-zone-googlescrap'
password = '6hm0q9x73v5x'
proxy_url = f'http://{username}:{password}@{host}:{port}'
proxies = {
    'http': proxy_url,
    'https': proxy_url,
}

# Definindo o diretório para armazenamento dos arquivos CSV
diretorio_csvs = os.path.join(os.getcwd(), "csvs")
if not os.path.exists(diretorio_csvs):
    os.makedirs(diretorio_csvs)

def coletar_dominios_e_numeros_telefone(termo_pesquisa, numero_paginas):
    # Definindo a URL base para pesquisa no Google Shopping
    url_base = f"https://www.google.com/search?q={termo_pesquisa}&tbm=shop&start="

    # Obtendo a data e hora atual
    data_e_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Nome do arquivo CSV onde os domínios serão armazenados
    nome_arquivo_csv = f"{termo_pesquisa}_{data_e_hora_atual}.csv"

    # Lista para armazenar os domínios já coletados
    dominios_coletados = []

    # Função para extrair número de telefone de uma página HTML
    def extrair_numero_telefone(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=4)
            response.raise_for_status()
            content = response.content

            soup = BeautifulSoup(content, 'lxml')

            phone_regex = re.compile(r'''
                (\+?\d{1,3}[\s-]?)?             # Código do país opcional
                (\(?\d{1,4}\)?[\s-]?)?          # Código de área opcional
                (\d{2,3}[\s-]?\d{2,3}[\s-]?\d{2,4})  # Número local
                ''', re.VERBOSE)

            phone_numbers = set()

            for element in soup.find_all(text=phone_regex):
                matches = phone_regex.findall(element)
                matches = [''.join(match).strip() for match in matches]
                phone_numbers.update(matches)

            # Normalizar números de telefone
            unique_phone_numbers = [re.sub(r'[^\d\+]', '', number) for number in phone_numbers]

            return unique_phone_numbers
        except requests.Timeout:
            print(f"Timeout ao processar a URL {url}.")
            return []
        except requests.RequestException as e:
            print(f"Erro na solicitação ao processar a URL {url}: {str(e)}")
            return []
        except Exception as e:
            print(f"Erro ao processar a URL {url}: {str(e)}")
            return []


    # Loop através das páginas de resultados da pesquisa
    for pagina in range(numero_paginas):
        # Construindo a URL da página atual
        url = url_base + str(pagina)

        # Fazendo uma solicitação HTTP para obter o conteúdo da página
        response = requests.get(url,  proxies=proxies, verify=False)

        # Verificando se a solicitação foi bem-sucedida (status_code 200)
        if response.status_code == 200:
            # Analisando o conteúdo HTML da página usando BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrando todos os links na página
            links_pagina = soup.find_all('a')

            # Adicionando os links da página atual à lista de links encontrados
            links_encontrados = []
            for link in links_pagina:
                
                hrefs = link.get('href')
                if hrefs and "www." in hrefs:
                    # cleaned_link = href.split("/url?q=")[-1].split("&")[0]
                    # parsed_link = urlparse(cleaned_link)
                    url_limpado = hrefs.split('/url?url=')[-1].split("&")[0]
                    links_encontrados.append(url_limpado)
                    
            # Limpando os links e coletando apenas os endereços principais
            
            
            
            # Definindo palavras-chave a serem filtradas
            palavras_chave = ["shein", "mercaolivre", "magazineluiza", "kabum", "submarino", "extra",
                              "casasbahia", "renner", "shopee", "google", "cea", "pontofrio", "riachuelo",
                              "centauro", "decathlon", "carrefour", "amazon", "ebay", "mercadolivre",
                              "americanas", "submarino", "shopee", "magazineluiza", "olx", "netshoes",
                              "dafiti", "zoom", "centauro", "casasbahia", "extra", "pontofrio", "carrefour",
                              "walmart", "leroymerlin", "zattini", "mercadoshops", "elo7", "kabum",
                              "madeiramadeira", "etna", "cea", "lojasrenner", "enjoei", "tricae", "girafa",
                              "petlove", "casasbahiamarketplace", "pernambucanas", "fastshop", "mercadopago",
                              "melhorenvio", "colombo", "b2wmarketplace", "bebestore", "drogasil",
                              "maquinadevendas", "onofreeletro", "todaoferta.uol", "saraiva", "ciadoslivros",
                              "fnac", "havan", "shoptime", "ricardoeletro", "gazinmarketplace",
                              "centauromarketplace", "olist", "vivaramarketplace", "paguemenos", "bebe",
                              "bebemamao", "globoplay.globo", "puket", "dinda", "posthaus",
                              "lojasmorenarosa", "gpa"]

            # Filtrando os links removendo os que contêm palavras-chave
            links_finais_filtrados = [link for link in links_encontrados if not any(palavra in link for palavra in palavras_chave)]

            # Extraindo apenas os endereços principais (domínios) dos links filtrados
            for link in links_finais_filtrados:
                parsed_url = urlparse(link)
                dominio = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
                if dominio not in dominios_coletados:
                    dominios_coletados.append(dominio)

                    # Escrevendo os domínios e números de telefone em um arquivo CSV
                    with open(os.path.join(diretorio_csvs, nome_arquivo_csv), 'a', newline='', encoding='utf-8') as arquivo_csv:
                        phone_numbers = extrair_numero_telefone(dominio)
                        if phone_numbers:
                            phone_numbers_str = ', '.join(phone_numbers)
                        else:
                            phone_numbers_str = "Nenhum número encontrado"
                        writer = csv.writer(arquivo_csv)
                        writer.writerow([dominio, phone_numbers_str])
 
            # Adicionando um pequeno atraso entre as solicitações com intervalo aleatório
            intervalo_aleatorio = random.uniform(1, 3) #ate 400 paginas sem travar
            print(f"Aguardando {intervalo_aleatorio:.2f} segundos antes da próxima solicitação. Página {pagina + 1}")
            time.sleep(intervalo_aleatorio)
        else:
            print(f"Falha ao acessar a página {pagina + 1}")

# Exemplo de uso da função:
# coletar_dominios_e_numeros_telefone("vinhos", 100)
