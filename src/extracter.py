import pandas as pd
import sqlite3

DB_PATH = 'k2.db'

class Extracter:
    """Extracts links table from database as pandas dataframe and writes csv."""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def _get_links(self):
        df = pd.read_sql_query("select * from links", self.conn)
        return df
    
    def _write_csv(self, df):
        df.to_csv('links.csv', index=False)
    
    def run(self):
        df = self._get_links()
        self._write_csv(df)
        self.conn.close()
        return df
    
if __name__ == '__main__':
    Extracter().run()