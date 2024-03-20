import time
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import pandas as pd

DB_PATH = 'k2.db'


class Reader:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, service=service)
    driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': True})
    driver.implicitly_wait(2)
    driver.set_window_size(1920, 1080)

    """A class to read link urls and write text from html pages to a database."""
    def __init__(self):
        
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                link_id INTEGER,
                article TEXT
            )
        ''')
        self.conn.commit()


    def _get_links(self):
        df = pd.read_sql_query("select * from links", self.conn)
        return df
    
    def _get_article(self, url):
        self.driver.get(url)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, 'html.parser')
        body = soup.find('body')
        article = body.get_text()
        return article
    

    def _write_article(self, article, link_id):
        self.cursor.execute('''
            INSERT INTO articles (link_id, article)
            VALUES (?, ?)
        ''', (link_id, article))
        self.conn.commit()

    def _check_exists(self, link_id):
        self.cursor.execute('''
            SELECT * FROM articles WHERE link_id = ?
        ''', (link_id,))
        return self.cursor.fetchone()

    
    def read_all(self):
        links = self._get_links()
        for i, link in links.iterrows():
            url = link['url']
            link_id = link['id']
            if not self._check_exists(link_id):
                article = self._get_article(url)
                self._write_article(article, link_id)
                time.sleep(5)

if __name__ == '__main__':
    reader = Reader()
    reader.read_all()

    
    
