import requests
import psycopg2
import logging
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
from decouple import config

logging.basicConfig(filename="logs/crypto_data.log", level=logging.DEBUG, format="%(asctime)s: %(levelname)s: %(message)s")

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
                logging.info(f"{name} added.")
            except IntegrityError as e:
                logging.error(f"Error: {e}")
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

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT name, rank, last_update 
        FROM cryptocurrencies 
        ORDER BY name, last_update DESC
        """
    )
    rows = cur.fetchall()

    rank_changes_positive = []
    rank_changes_negative = []
    for i in range(0, len(rows), 2):
        if i + 1 < len(rows):
            current_rank = rows[i]["rank"]
            previous_rank = rows[i + 1]["rank"]
            name = rows[i]["name"]
            rank_change = previous_rank - current_rank
            if rank_change > 0:
                rank_changes_positive.append((name, previous_rank, current_rank, rank_change))
            if rank_change < 0:
                rank_changes_negative.append((name, previous_rank, current_rank, rank_change))

    rank_changes_positive.sort(key=lambda x: abs(x[3]), reverse=True)
    rank_changes_negative.sort(key=lambda x: abs(x[3]), reverse=True)

    cur.close()
    conn.close()

    return rank_changes_positive, rank_changes_negative

def main():
    crypto_data = get_crypto_data()
    save_data(crypto_data)

    positive_changes, negative_changes = compare_ranks()
    logging.info("Positive Rank Changes:")
    for change in positive_changes:
        name, previous_rank, current_rank, rank_change = change
        logging.info(f"{name} {current_rank} to {previous_rank} ({rank_change})")

    logging.info("Negative Rank Changes:")
    for change in negative_changes:
        name, previous_rank, current_rank, rank_change = change
        logging.info(f"{name} {current_rank} to {previous_rank} ({rank_change})")

if __name__ == "__main__":
    main()
