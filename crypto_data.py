import requests
import psycopg2
from psycopg2 import IntegrityError
from decouple import config

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
    rank = currency["cmcRank"]
    name = currency["name"]
    symbol = currency["symbol"]
    price = currency["quotes"][0]["price"]
    percent_change_1h = currency["quotes"][0]["percentChange1h"]
    percent_change_24h = currency["quotes"][0]["percentChange24h"]
    percent_change_7d = currency["quotes"][0]["percentChange7d"]
    market_cap = currency["quotes"][0]["marketCap"]
    volume_24h = currency["quotes"][0]["volume24h"]
    circulating_supply = currency["circulatingSupply"]
    last_update = currency["lastUpdated"]
    return [rank, name, symbol, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, circulating_supply, last_update]

def save_data(crypto_data):
    conn = psycopg2.connect(
        dbname=config("DB_NAME"),
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        host=config("DB_HOST"),
        port=config("DB_PORT"),
    )

    cur = conn.cursor()

    for currency in crypto_data["data"]["cryptoCurrencyList"]:
        currency_info = extract_currency_info(currency)
        name = currency_info[1]
        last_update = currency_info[-1]

        # check if a record with the same name exists in the table
        cur.execute("SELECT last_update FROM cryptocurrencies WHERE name = %s", (name,))
        existing_last_update = cur.fetchone()

        if existing_last_update is None or existing_last_update[0] != last_update:
            try:
                cur.execute(
                    """
                    INSERT INTO cryptocurrencies (rank, name, symbol, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, circulating_supply, last_update)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, currency_info
                )
                conn.commit()
                print(f"{name} added.")
            except IntegrityError as e:
                print(f"Error: {e}")
                conn.rollback()

    cur.close()
    conn.close()

def compare_ranks():
    conn = psycopg2.connect(
        dbname=config("DB_NAME"),
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        host=config("DB_HOST"),
        port=config("DB_PORT"),
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT name, rank, last_update
        FROM cryptocurrencies
        ORDER BY rank, last_update DESC
        """)
    rows = cur.fetchall()

    coin_updates = {}
    for name, rank, last_update in rows:
        if name not in coin_updates:
            coin_updates[name] = []

        coin_updates[name].append((rank, last_update))

    for name, updates in coin_updates.items():
        if len(updates) >= 2:
            rank_change = updates[0][0] - updates[1][0]
            if rank_change != 0:
                change_symbol = "+" if rank_change > 0 else "-"
                print(f"{name} to {updates[0][0]} ({change_symbol}{abs(rank_change)})")

    cur.close()
    conn.close()


def main():
    crypto_data = get_crypto_data()
    save_data(crypto_data)
    compare_ranks()

if __name__ == "__main__":
    main()