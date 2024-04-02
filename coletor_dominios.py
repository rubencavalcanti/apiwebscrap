import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse, urlunparse
import random
import re
import datetime
import os
import ssl
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
            # Cabeçalho User-Agent simulando um navegador Chrome em Windows 10
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            # Enviar uma solicitação HTTP para obter o conteúdo da página com um timeout de 4 segundos
            response = requests.get(url, headers=headers, timeout=4)
            response.raise_for_status()  # Verificar se há erros na solicitação
            content = response.content

            # Parse do HTML com BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Encontrar elementos no footer que podem conter números de telefone
            footer_elements = soup.find_all(['footer', 'div', 'span', 'p', 'a', 'strong'])

            # Lista para armazenar números de telefone encontrados
            phone_numbers = []

            # Expressão regular mais flexível para encontrar números de telefone
            phone_regex = re.compile(r'(?:(?:\+|00)\d{1,3})?[ -]?\(?0?\d{1,3}\)?[ -]?\d{4,5}[ -]?\d{4}')

            for element in footer_elements:
                # Extrair texto do elemento
                element_text = element.get_text()

                # Encontrar números de telefone usando a expressão regular
                matches = phone_regex.findall(element_text)

                # Adicionar números de telefone à lista
                phone_numbers.extend(matches)

            # Remover duplicatas usando um conjunto (set)
            unique_phone_numbers = list(set(phone_numbers))

            return unique_phone_numbers
        except requests.Timeout:
            print(f"Timeout ao processar a URL {url}. Pulando para o próximo URL.")
            return []
        except Exception as e:
            print(f"Erro ao processar a URL {url}: {str(e)}")
            return []

    # Loop através das páginas de resultados da pesquisa
    for pagina in range(numero_paginas):
        # Construindo a URL da página atual
        url = url_base + str(pagina)

        # Fazendo uma solicitação HTTP para obter o conteúdo da página
        response = requests.get(url, proxies=proxies, verify=False)

        # Verificando se a solicitação foi bem-sucedida (status_code 200)
        if response.status_code == 200:
            # Analisando o conteúdo HTML da página usando BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrando todos os links na página
            links_pagina = soup.find_all('a')

            # Adicionando os links da página atual à lista de links encontrados
            links_encontrados = []
            for link in links_pagina:
                href = link.get('href')
                if href:
                    links_encontrados.append(href)

            # Limpando os links e coletando apenas os endereços principais
            links_finais = [link for link in links_encontrados if '/url?q=' in link]
            links_finais_sem_q = [link.replace("/url?q=", "") for link in links_finais]

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
            links_finais_filtrados = [link for link in links_finais_sem_q if not any(palavra in link for palavra in palavras_chave)]

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
            intervalo_aleatorio = random.uniform(1, 3)
            print(f"Aguardando {intervalo_aleatorio:.2f} segundos antes da próxima solicitação.")
            time.sleep(intervalo_aleatorio)
        else:
            print(f"Falha ao acessar a página {pagina + 1}")

# Exemplo de uso da função:
# coletar_dominios_e_numeros_telefone("vinhos", 100)
