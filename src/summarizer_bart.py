import sqlite3
import pandas as pd
from transformers import BartTokenizer, BartForConditionalGeneration

DB_PATH = "k2.db"


class Summarizer:
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn", vocab_size=1e6)
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn").to(
        "cuda"
    )

    def __init__(self) -> None:
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY,
                link_id INTEGER,
                summary TEXT
            )
        """)
        self.conn.commit()

    def _get_articles(self):
        df = pd.read_sql_query("select * from articles", self.conn)
        return df

    @classmethod
    def summarize(cls, text):
        """Function to get summary by bart model"""
        input_ids = cls.tokenizer.encode(
            text, return_tensors="pt", max_length=1024, truncation=True
        ).to("cuda")
        summary_ids = cls.model.generate(
            input_ids, length_penalty=2.0, num_beams=4, early_stopping=True
        )
        output_summ = [
            cls.tokenizer.decode(
                g, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            for g in summary_ids
        ]
        return output_summ[0]

    def _write_summary(self, summary, link_id):
        self.cursor.execute(
            """
            INSERT INTO summaries (link_id, summary)
            VALUES (?, ?)
        """,
            (link_id, summary),
        )
        self.conn.commit()

    def _check_exists(self, link_id):
        self.cursor.execute(
            """
            SELECT * FROM summaries WHERE link_id = ?
        """,
            (link_id,),
        )
        return self.cursor.fetchone()

    def summarize_all(self, debug=False):
        articles = self._get_articles()
        for i, article in articles.iterrows():
            link_id = article["link_id"]
            text = article["article"]
            summary = self.summarize(text)
            if debug:
                print(summary)
            if not self._check_exists(link_id):
                self._write_summary(summary, link_id)


if __name__ == "__main__":
    summarizer = Summarizer()
    summarizer.summarize_all(debug=True)
