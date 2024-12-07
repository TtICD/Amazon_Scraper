from scraper import AmazonScraper
import pandas as pd
import time


scraper = AmazonScraper()
df = pd.read_csv('./data/cumulative_data.csv')

url_list = df['link'].unique()

for url in url_list:
    scraper.daily_scrape(url=url)
    time.sleep(10)

