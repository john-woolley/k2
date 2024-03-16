import time
import bs4
import sqlite3
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

DB_PATH = 'k2.db'

class Scanner:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY,
                url TEXT,
                date TEXT,
                title TEXT,
                ticker TEXT,
                public BOOLEAN
            )
        ''')
        self.conn.commit()

    def scan(self, url, parent_class, link_class, date_class, ticker):
        self.driver.get(url)
        time.sleep(2)
        items = self.driver.find_elements(By.CLASS_NAME, parent_class)
        for item in items:
            try:
                dates = item.find_elements(By.CLASS_NAME, date_class)
                links = item.find_elements(By.CLASS_NAME, link_class)
                for i, link_field in enumerate(links):
                    link = link_field.find_element(By.TAG_NAME, 'a')
                    link_url = link.get_attribute('href')
                    link_text = link.text
                    if not link_url or not link_text:
                        continue
                    self.cursor.execute('''
                        INSERT INTO links (url, date, title, ticker, public)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (link_url, dates[i].text, link_text, ticker, True))
            except NoSuchElementException:
                pass
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    s = Scanner()
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f, )
    therapeutics = config['portfolio']['Therapeutics']
    for stock, data in therapeutics.items():
        s.scan(data['ir'], data['class'], data['link_class'], data['date_class'], stock)
    s.close()