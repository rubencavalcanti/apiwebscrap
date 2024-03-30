import pprint
import requests


host = 'brd.superproxy.io'
port = 22225

username = 'brd-customer-hl_e9104e6a-zone-serp'
password = 'w73vg8mysp1t'

proxy_url = f'http://{username}:{password}@{host}:{port}'

proxies = {
    'http': proxy_url,
    'https': proxy_url
}


url = "https://www.google.com/search?q=pizza"
response = requests.get(url, proxies=proxies)
pprint.pprint(response.json())

