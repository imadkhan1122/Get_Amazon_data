# ........................................Important Packages...................................#
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import random
import json
from fake_useragent import UserAgent

# ............................CLASS GET AMAZON DATA...........................................#
class GET_AMAZON_DATA:
    # ............................CLASS Constructor............................#
    def __init__(self):
        self.options = Options()
        self.ua = UserAgent()
        user_agent = self.ua.random
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument('--headless')
        self.main()
        
    # ............................Retrieve Product URLs........................#
    def GET_PRODUCT_LNKS(self,URL):   
        LNK_LST = []
        URL = 'https://www.amazon.com/'
        # open chrome browser
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
        # Go to given URL
        driver.get(URL)
        # wait for 5 seconds
        delay = 10 # seconds
        try:
            # wait untill page loads
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'nav-logo-sprites')))
            # locate searchbar and type product name
            SearchBar = driver.find_element_by_id("twotabsearchtextbox")
            SearchBar.send_keys("laptops")
            time.sleep(1)
            SearchBut = driver.find_element_by_id('nav-search-submit-button')
            SearchBut.send_keys(Keys.ENTER)
            time.sleep(1)
            
            time.sleep(3)
            
            n = 1
                # pagination of all pages
            while n:
                try:
                    PRODUCTS_TABLE = driver.find_elements_by_css_selector('h2.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2')
                    time.sleep(3)
                    for e, PRODUCT in enumerate(PRODUCTS_TABLE):
                        PRODUCTS_LNK = PRODUCT.find_element_by_tag_name('a')
                        LNK_LST.append(PRODUCTS_LNK.get_attribute('href'))
                    # Scroll page down to Next Button
                    Next = driver.find_element_by_css_selector("span.s-pagination-strip")
                    actions = ActionChains(driver)
                    actions.move_to_element(Next).perform()
                    time.sleep(3)
                    n = n + 1
                    Next.find_element_by_link_text(str(n)).click()
            
                except:
                    break                        
        except TimeoutException:
            print ("Loading took too much time!")
        
        driver.quit()
        return LNK_LST
    
    # ............................Retrieve Product Details.....................#
    def GET_PRODUCT_DETAILS(self,URL):
        dic = {}
        # initialize and declare an empty list
        # use header to send request with different agents to avoid blocking
        hdr = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        # send request to url
        req = Request(URL,headers=hdr)
        # visiting html page
        page = urlopen(req)
        # check while page status code not equal to 200
        while page.getcode() != 200:
            page = urlopen(req)
        # put page content to beautiful soup parser to convert it to html contents
        soup = BeautifulSoup(page, "html.parser")
        # check if url is home page url
        
        try:
            PROD_NAME = soup.find('h1', id='title').text
        except:
            PROD_NAME = ''
        Name = {'PROD_NAME':PROD_NAME}
        dic.update(Name)
        try:
            PROD_PRICE_ = soup.find('span', class_='a-price a-text-price a-size-medium apexPriceToPay')
            PROD_PRICE = PROD_PRICE_.find('span', class_='a-offscreen').text
        except:
            PROD_PRICE = ''
        PRICE = {'PROD_PRICE':PROD_PRICE}
        dic.update(PRICE)
        SPEC_TABLE = soup.find("table", class_="a-normal a-spacing-micro" )
    
        SPEC_TABLE_ROWS = SPEC_TABLE.find_all('tr')
        for SPEC_TABLE_ROW in SPEC_TABLE_ROWS:   
            try:
                SPEC_NAME = SPEC_TABLE_ROW.find_all('td')[0]
                SPEC_VALUE = SPEC_TABLE_ROW.find_all('td')[1]
                SPEC_DIC = {SPEC_NAME.text:SPEC_VALUE.text}
                dic.update(SPEC_DIC)
            except:
                pass
            
        return dic
    # ............................Main Function................................#
    def main(self):
        url = 'https://www.amazon.com/'
        links = self.GET_PRODUCT_LNKS(url)
        print(links)
        while links == []:
            links = self.GET_PRODUCT_LNKS(url)
        # Directly from dictionary
        print('[INFO] Downloading Data...')
        with open('Output.json', mode='w') as f:
            for url in links:
                print(url)
                dic = self.GET_PRODUCT_DETAILS(url)
                print(dic)
                if dic['PROD_NAME'] != '':
                    f.write(json.dumps(dic, indent=2))
        
        print('[INFO] Downloaded')
        return



