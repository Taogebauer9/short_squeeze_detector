from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd

class FinvizStocks:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()
        self.data = self.get_data()

    def get_soup(self):
        try:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')  # Ensure headless mode is enabled
            # options.add_argument('--accept_untrusted_certs')  

            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.get(self.url)

            # Wait until the table with class 'tab-link' is present
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'content')))
            html = driver.page_source
            
            driver.quit()
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"Error fetching the page: {e}")
            return None

    def get_data(self):
        table = self.soup.find('table', {'class': 'styled-table-new is-rounded is-tabular-nums w-full screener_table'})
        if not table:
            print("'Screener_table' not found.")
            return {}
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue  # Skip rows that do not have at least two columns
            row_data = [ele.text.strip() for ele in cols]
            data.append(row_data)
        headers = ['No.', 'Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap', 'P/E', 'Price', 'Change', 'Volume']
        data = pd.DataFrame(data, columns=headers) 
        return data
    
    
if __name__ == '__main__':
    url = 'https://finviz.com/screener.ashx?v=111&f=sh_float_u10%2Csh_opt_option%2Csh_outstanding_o1%2Csh_price_u5%2Csh_short_high'
    finviz = FinvizStocks(url)
    print(finviz.data)