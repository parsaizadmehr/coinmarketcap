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
    name = currency["name"]
    price = currency["quotes"][0]["price"]
    percent_change_1h = currency["quotes"][0]["percentChange1h"]
    percent_change_24h = currency["quotes"][0]["percentChange24h"]
    percent_change_7d = currency["quotes"][0]["percentChange7d"]
    market_cap = currency["quotes"][0]["marketCap"]
    volume_24h = currency["quotes"][0]["volume24h"]
    circulating_supply = currency["circulatingSupply"]
    last_update = currency["lastUpdated"]
    return [name, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, circulating_supply, last_update]

def save_data(crypto_data):
    conn = psycopg2.connect(
        dbname=config("DB_NAME"),
        user=config("DB_USER"),
        password=config("DB_PASSWORD"),
        host=config("DB_HOST"),
        port=config("DB_PORT"),
    )

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            price NUMERIC,
            percent_change_1h NUMERIC,
            percent_change_24h NUMERIC,
            percent_change_7d NUMERIC,
            market_cap NUMERIC,
            volume_24h NUMERIC,
            circulating_supply NUMERIC,
            last_update TIMESTAMP,
            CONSTRAINT unique_name_last_update UNIQUE (name, last_update)
        );
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_cryptocurrencies_name ON cryptocurrencies (name);
        CREATE INDEX IF NOT EXISTS idx_cryptocurrencies_last_update ON cryptocurrencies (last_update);
    """)

    for currency in crypto_data["data"]["cryptoCurrencyList"]:
        currency_info = extract_currency_info(currency)
        name = currency_info[0]
        last_update = currency_info[-1]

        # check if a record with the same name exists in the table
        cur.execute("SELECT last_update FROM cryptocurrencies WHERE name = %s", (name,))
        existing_last_update = cur.fetchone()

        if existing_last_update is None or existing_last_update[0] != last_update:
            try:
                cur.execute(
                    """
                    INSERT INTO cryptocurrencies (name, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, circulating_supply, last_update)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, currency_info
                )
                conn.commit()
                print(f"{name} added.")
            except IntegrityError as e:
                print(f"Error: {e}")
                conn.rollback()

    cur.close()
    conn.close()

crypto_data = get_crypto_data()
save_data(crypto_data)

print("Data saved to the database successfully.")