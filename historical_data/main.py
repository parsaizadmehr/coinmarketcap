import datetime
import time

from decouple import config
from psycopg2 import OperationalError
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import psycopg2

website = "https://coinmarketcap.com/historical/20130428/"

def smooth_scroll(driver, scroll_amount, interval):
    current_position = 0
    total_height = driver.execute_script("return document.body.scrollHeight")

    while current_position < total_height:
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        current_position += scroll_amount
        time.sleep(interval)

def get_data_from_website(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        smooth_scroll(driver, 500, 0.1)
        all_elements = driver.find_elements(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[3]/div/table/tbody/tr")
        data = [element.text.strip() for element in all_elements]
        return data
    except WebDriverException as e:
        print(f"An error occurred while accessing the website: {e}")
        return []

def insert_data(data, date):
    try:
        conn = psycopg2.connect(
            dbname=config("DB_NAME"),
            user=config("DB_USER"),
            password=config("DB_PASSWORD"),
            host=config("DB_HOST"),
            port=config("DB_PORT"),
        )
        cursor = conn.cursor()
        
        for item in data:
            try:
                item_data = item.split("\n")
                rank = int(item_data[0])
                name = item_data[1]
                market_cap = float(item_data[3].replace("$", "").replace(",", ""))
                price = float(item_data[4].replace("$", "").replace(",", ""))
                circulating_supply_text = item_data[5].split(" ")[0]
                circulating_supply = float(circulating_supply_text.replace(",", ""))

                if len(item_data) == 10:
                    volume_24h_str = item_data[6].replace("$", "").replace(",", "")
                    volume_24h = float(volume_24h_str) if volume_24h_str != "--" else None
                    
                    percent_1h_str = item_data[7].replace(",", "") 
                    percent_1h = float(percent_1h_str.replace("%", "")) if percent_1h_str != "--" else None

                    percent_24h_str = item_data[8].replace(",", "")
                    percent_24h = float(percent_24h_str.replace("%", "")) if percent_24h_str != "--" else None
                    
                    percent_7d_str = item_data[9].replace(",", "")
                    percent_7d = float(percent_7d_str.replace("%", "")) if percent_7d_str != "--" else None
                    
                else:
                    volume_24h = None
                    percent_1h_str = item_data[6].replace(",", "") 
                    percent_1h = float(percent_1h_str.replace("%", "")) if percent_1h_str != "--" else None

                    percent_24h_str = item_data[7].replace(",", "")
                    percent_24h = float(percent_24h_str.replace("%", "")) if percent_24h_str != "--" else None
                    
                    percent_7d_str = item_data[8].replace(",", "")
                    percent_7d = float(percent_7d_str.replace("%", "")) if percent_7d_str != "--" else None

                sql = """
                INSERT INTO historical_data (rank, name, price, market_cap, circulating_supply, percent_change_1h, percent_change_24h, percent_change_7d, volume_24h, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (rank, name, price, market_cap, circulating_supply, percent_1h, percent_24h, percent_7d, volume_24h, date))
            except (IndexError, ValueError) as e:
                print(f"An error occurred while processing data: {e}")
                continue

        print("Data saved.")
        conn.commit()
    except (OperationalError, psycopg2.Error) as e:
        print(f"An error occurred while connecting to the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_urls():
    '''Get all previous urls as list for crawl'''
    start_date = datetime.date(2014, 1, 26)
    end_date = datetime.date(2024, 2, 28)
    week_delta = datetime.timedelta(days=7)

    current_date = start_date
    urls = []

    while current_date <= end_date:
        url = f"https://coinmarketcap.com/historical/{current_date.strftime('%Y%m%d')}/"
        urls.append(url)
        current_date += week_delta
    return urls

urls = get_urls()

for url in urls:
    print("-------------------------")
    print(f"requesting to {url}")

    # getting date from url to use in insert data
    date = datetime.datetime.strptime(url.split("/")[-2], "%Y%m%d").strftime("%Y-%m-%d")

    data = get_data_from_website(url)
    insert_data(data, date)
