from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime
import time

website = "https://coinmarketcap.com/historical/20130428/"


def smooth_scroll(driver, scroll_amount, interval):
    current_position = 0
    total_height = driver.execute_script("return document.body.scrollHeight")

    while current_position < total_height:
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        current_position += scroll_amount
        time.sleep(interval)

def get_data_from_website(url):
    driver = webdriver.Chrome()
    driver.get(url)
    smooth_scroll(driver, 500, 0.1)
    all_elements = driver.find_elements(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[3]/div/table/tbody/tr")
    data = [element.text.strip() for element in all_elements]
    driver.quit()
    return data

def insert_data(data):
    for item in data:
        item_data = item.split("\n")
        rank = int(item_data[0])
        name = item_data[1]
        market_cap = float(item_data[3].replace("$", "").replace(",", ""))
        price = float(item_data[4].replace("$", ""))
        circulating_supply_text = item_data[5].split(" ")[0]
        circulating_supply = float(circulating_supply_text.replace(",", ""))
        
        percent_1h_str = item_data[6]
        percent_1h = float(item_data[6].replace("%", "")) if percent_1h_str != "--" else None

        percent_24h_str = item_data[7]
        percent_24h = float(percent_24h_str.replace("%", "")) if percent_24h_str != "--" else None
        
        percent_7d_str = item_data[8]
        percent_7d = float(percent_7d_str.replace("%", "")) if percent_7d_str != "--" else None

def get_urls():
    '''Get all privous urls as list for crawl'''
    start_date = datetime.date(2013, 4, 28)
    end_date = datetime.date(2024, 2, 28)
    week_delta = datetime.timedelta(days=7)

    current_date = start_date
    urls = []

    while current_date <= end_date:
        url = "https://coinmarketcap.com/historical/{}/".format(current_date.strftime("%Y%m%d"))
        urls.append(url)
        current_date += week_delta

    return urls

urls = get_urls()

for url in urls:
    print(url)
    data = get_data_from_website(url)
    insert_data(data)

