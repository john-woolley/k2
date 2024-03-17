import time
import bs4
import requests
import sqlite3
import pandas as pd

DB_PATH = 'k2.db'


class Reader:
    """A class to read link urls and write text from html pages to a database."""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                url TEXT,
                date TEXT,
                title TEXT,
                ticker TEXT,
                public BOOLEAN
            )
        ''')
        self.conn.commit()


    def _get_links(self):
        df = pd.read_sql_query("select * from links")
        return df
    
    def _get_article(self, url):
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        title = soup.title.string
        return title

    
    
