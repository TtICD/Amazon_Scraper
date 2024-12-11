import pandas as pd
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class ScraperConfig():
    def __init__(self):
        self.driver = None

        options = webdriver.ChromeOptions()
        #options.add_experimental_option("detach", True) 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--headless")  # Enable headless mode
        options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional but recommended in headless mode)
        options.add_argument("--no-sandbox")  # Disable sandbox (useful on some systems like Linux)
        
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            },
        )

        
        
        

class AmazonScraper():
    def __init__(self, base_url='https://www.amazon.in/'):
        self.scraper_config = ScraperConfig()
        self.base_url = base_url
        

    def scrape(self,query):
        driver = self.scraper_config.driver
        driver.get(self.base_url)
        time.sleep(5)
       
        #Finding the search feild
        search_feild = driver.find_element(By.ID, value='twotabsearchtextbox')

        for char in query:
            search_feild.send_keys(char)
            time.sleep(0.2)
        search_feild.send_keys(Keys.RETURN)
        

        #Waiting for the main section to load.
        wait = WebDriverWait(driver, 10)
        results = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 's-main-slot')))

        #Finding list of individual search result elements.
        products = results.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
        
        
        
        name_price = []
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, 'h2 a').text
                link_ = product.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
        
                price = product.find_element(By.CLASS_NAME, 'a-price-whole').text
                price = float(price.replace(',',''))
        
                rating = product.find_element(By.CSS_SELECTOR, 'span.a-icon-alt').get_attribute('innerHTML')
                rating = float(rating[:3])
        
                no_of_reviews = product.find_elements(By.CSS_SELECTOR, '[data-cy="reviews-block"] a')[-1].text
                no_of_reviews = int(no_of_reviews.replace(',',''))
        
                name_price.append({
                    'product_name':name,
                    'price_in_inr':price,
                    'rating_out_of_5':rating,
                    'reviews':no_of_reviews,
                    'link':link_
                }
            )
            except:
                pass
        
        df = pd.DataFrame(name_price)
        return df
        
    def daily_scrape(self,url):
        driver = self.scraper_config.driver
        driver.get(url=url)

        time.sleep(50)
        
        product = driver.find_element(By.ID, 'centerCol')
        name = product.find_element(By.ID, 'productTitle').text
        
        price_block = product.find_element(By.ID, 'corePriceDisplay_desktop_feature_div')
        price = price_block.find_element(By.CLASS_NAME, 'a-price-whole').text
        price = float(price.replace(',',''))
        
        review_block = product.find_element(By.ID, 'averageCustomerReviews_feature_div')
        
        star = review_block.find_element(By.ID, 'acrPopover').text
        star = float(star)
        
        ratings = review_block.find_element(By.ID, 'acrCustomerReviewText').text
        
        
        ratings = [char for char in ratings if char.isdigit()]
        
        no_of_ratings = ''
        for num in ratings:
            no_of_ratings += num
        
        no_of_ratings = int(no_of_ratings)
        
        product_data = [[name, date.today(), price, star, no_of_ratings, url]]
        df = pd.DataFrame(product_data, columns=[ 'name', 'date', 'price', 'star', "reveiw_no",'link'])
        df.to_csv('./data/current_day_data.csv')
    
        try:
            cumulative_data = pd.read_csv('./data/cumulative_data.csv')
        except FileNotFoundError:
            cumulative_data = pd.DataFrame(columns=df.columns)
    
        cumulative_data = pd.concat([cumulative_data, df], ignore_index=True)
        cumulative_data = cumulative_data.drop_duplicates(subset=["link", "date"], keep="first")
        cumulative_data.to_csv('./data/cumulative_data.csv', index=False)
    
    
            
                
            
    
        
                
                
