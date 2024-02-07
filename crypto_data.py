import requests
from tabulate import tabulate

def get_crypto_data():
    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
    params = {
        'start': '1',
        'limit': '100',
        'sortBy': 'market_cap',
        'sortType': 'desc',
        'convert': 'USD',
        'cryptoType': 'all',
        'tagType': 'all',
    }
    response = requests.get(url, params=params).json()
    return response

def extract_currency_info(currency):
    name = currency["name"]
    price = round(currency["quotes"][0]["price"], 4)
    percent_change_1h = round(currency["quotes"][0]["percentChange1h"], 2)
    percent_change_24h = round(currency["quotes"][0]["percentChange24h"], 2)
    percent_change_7d = round(currency["quotes"][0]["percentChange7d"], 2)
    market_cap = round(currency["quotes"][0]["marketCap"], 2)
    volume_24h = round(currency["quotes"][0]["volume24h"], 2)
    circulating_supply = round(currency["circulatingSupply"], 2)
    return (name, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, circulating_supply)

def print_crypto_table(crypto_data):
    results = []
    for currency in crypto_data["data"]["cryptoCurrencyList"]:
        results.append(extract_currency_info(currency))

    headers = ["Name", "Price (USD)", "1h Change (%)", "24h Change (%)", "7d Change (%)", "Market Cap (USD)", "Volume (24h)", "Circulating Supply"]
    print(tabulate(results, headers=headers, tablefmt="pretty"))


crypto_data = get_crypto_data()
print_crypto_table(crypto_data)

