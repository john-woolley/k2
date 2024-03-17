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
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, service=service)
    driver.set_window_size(1920, 1080)

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

    def _get_data_args(self, data):
        url = data['ir']
        parent_class = data['class']
        date_class = data['date_class']
        link_class = data['link_class']
        title_class = data.get('title_class', None) # Optional
        unwrap = data.get('unwrap_link', False) # Optional
        return url, parent_class, date_class, link_class, title_class, unwrap
    
    def _parse_dates(self, item, date_class):
        if date_class[0] == '$':
            tags = item.find_elements(By.TAG_NAME, 'time')
            dates = [tag.get_attribute("datetime") for tag in tags]
        else:
            dates = item.find_elements(By.CLASS_NAME, date_class)
            dates = [date.text for date in dates]
        return dates
    
    def _insert_links(self, ticker, dates, links, titles=None, unwrap_link=False):
        for i in range(len(links)):
            try:
                date = dates[i]
                if unwrap_link:
                    a = links[i].find_element(By.TAG_NAME, 'a')
                    link = a.get_attribute('href')
                    title = a.get_attribute('text')
                else:
                    link = links[i].get_attribute('href')
                    title = links[i].get_attribute('text')

                if titles:
                    title = titles[i].text

                if not link or not title:
                    continue
            except IndexError:
                continue

            self.cursor.execute('''
                INSERT INTO links (url, date, title, ticker, public)
                VALUES (?, ?, ?, ?, ?)
            ''', (link, date, title, ticker, False))

    def scan(self, ticker, data):
        url, c_parent, c_date, c_link, c_title, unwrap = self._get_data_args(data)
        self.driver.get(url)
        time.sleep(2)
        items = self.driver.find_elements(By.CLASS_NAME, c_parent)
        for item in items:
            try:
                dates = self._parse_dates(item, c_date)
                links = item.find_elements(By.CLASS_NAME, c_link)
                titles = None
                if c_title:
                    titles = item.find_elements(By.CLASS_NAME, c_title)
                if links:
                    self._insert_links(ticker, dates, links, titles, unwrap)
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
        s.scan(stock, data)
    s.close()