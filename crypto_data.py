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
        WITH ranked_cryptocurrencies AS (
            SELECT
                id,
                rank,
                symbol,
                name,
                price,
                percent_change_1h,
                percent_change_24h,
                percent_change_7d,
                market_cap,
                volume_24h,
                circulating_supply,
                last_update,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY last_update DESC) AS rn
            FROM
                cryptocurrencies
        )
        SELECT
            current.symbol,
            current.name,
            current.rank AS current_rank,
            previous.rank AS previous_rank,
            ( previous.rank - current.rank ) AS rank_change,
            current.price AS current_price,
            previous.price AS previous_price,
            current.percent_change_1h AS current_percent_change_1h,
            previous.percent_change_1h AS previous_percent_change_1h,
            current.percent_change_24h AS current_percent_change_24h,
            previous.percent_change_24h AS previous_percent_change_24h,
            current.percent_change_7d AS current_percent_change_7d,
            previous.percent_change_7d AS previous_percent_change_7d,
            current.market_cap AS current_market_cap,
            previous.market_cap AS previous_market_cap,
            current.volume_24h AS current_volume_24h,
            previous.volume_24h AS previous_volume_24h,
            current.circulating_supply AS current_circulating_supply,
            previous.circulating_supply AS previous_circulating_supply,
            current.last_update AS current_last_update,
            previous.last_update AS previous_last_update
        FROM
            ranked_cryptocurrencies current
        LEFT JOIN
            ranked_cryptocurrencies previous
        ON
            current.symbol = previous.symbol
            AND previous.rn = 2
        WHERE
            current.rn = 1;
        """
    )

    results = cur.fetchall()
    
    if results:
        logging.debug(f"Last update: {results[0]['current_last_update']}")

    for result in results:
        rank_change = result['rank_change']
        if rank_change != 0:
            logging.debug(f"{result['symbol']} {result['current_rank']}, Rank Change: {rank_change}")

    cur.close()
    conn.close()

def main():
    crypto_data = get_crypto_data()
    save_data(crypto_data)
    compare_ranks()

if __name__ == "__main__":
    main()
