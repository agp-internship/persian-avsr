import os
import time
import jdatetime
from tqdm import tqdm
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TelewebionScraper(webdriver.Firefox):

    """
    :param: webdriver_path - path to firefox geckodriver.exe
    """
    def __init__(self, webdriver_path='./geckodriver/geckodriver.exe', close_browser=True):
        self.download_dict = dict()
        self.download_quality = ['480', '720', '1080']
        self.service = Service(webdriver_path)
        self.close_browser = close_browser
        super(TelewebionScraper, self).__init__(service=self.service)
        self.implicitly_wait(20)
        self.maximize_window()


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_browser:
            self.quit()

    def get_archive(self, date=jdatetime.date.today(), channel='irinn'):
        date_str = date.strftime("%Y-%m-%d")
        date_str_without_zeropad = date_str.replace('-0', '-')
        self.get(f"https://telewebion.com/archive/{channel}/{date_str_without_zeropad}")

    def set_cookie_auth(self):
        load_dotenv()

        self.add_cookie({'name': '__asc', 'value': os.getenv('__asc')})
        self.add_cookie({'name': '__auc', 'value': os.getenv('__auc')})
        self.add_cookie({'name': '_uniqueId', 'value': os.getenv('_uniqueId')})
        self.add_cookie({'name': 'token', 'value': os.getenv('token')})

    def click_load_more_button(self):
        load_more_elem = WebDriverWait(self, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'load-more'))
        )
        if load_more_elem:
            print('load more button clicked!')
            load_more_elem.click()

    def get_episodes(self):
        elems = WebDriverWait(self, 20).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/episode/"]'))
        )
        elems = list(set([elem.get_attribute('href') for elem in elems])) # remove duplicate links
        print(len(elems))
        return elems

    def extract_link(self, elem): 
        try:
            self.get(elem)
            self.implicitly_wait(20)

            # play_elem = WebDriverWait(driver, 20).until(
            #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Pause"]'))
            # )
            # play_elem.click()

            download_elem = WebDriverWait(self, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'fa-cloud-download'))
            )
            download_elem.click()

            download_items = WebDriverWait(self, 20).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'download-item'))
            )

            download_links = {}
            for i in range(len(download_items)):
                download_links[self.download_quality[i]] = download_items[i].find_element(By.CSS_SELECTOR, 'a[href*="dl.telewebion.com"]').get_attribute('href')

            self.download_dict[elem] = download_links

            time.sleep(2)
        except:
            print('Not Found')

    def run(self):
        self.get_archive()
        self.set_cookie_auth()
        self.click_load_more_button()
        elems = self.get_episodes()
        for elem in tqdm(elems):
            self.extract_link(elem)

if __name__ == "__main__":
    with TelewebionScraper() as tele_obj:
        tele_obj.run()
        print(tele_obj.download_dict)    