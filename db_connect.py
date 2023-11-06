import sqlite3 as sq
import random


class Connect:
    def __init__(self):
        self.base = sq.connect('words.db')
        self.cur = self.base.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS statistics (
                         user_id INTEGER,
                         user_name TEXT,
                         right INTEGER,
                         wrong INTEGER
        )""")
        self.base.commit()

    def create_user(self, user_id, name: str):
        self.cur.execute("""INSERT INTO statistics VALUES (?, ?, 0, 0)""", (user_id, name))
        self.base.commit()

    def update_right(self, user_id):
        self.cur.execute("""UPDATE statistics SET right = right+1 WHERE user_id = '{}'""".format(user_id))
        self.base.commit()
        
    def update_wrong(self, user_id):
        self.cur.execute("""UPDATE statistics SET wrong = wrong+1 WHERE user_id = '{}'""".format(user_id))
        self.base.commit()

    def clear_stat(self, user_id):
        self.cur.execute("""UPDATE statistics SET right = 0, wrong = 0 WHERE user_id = '{}'""".format(user_id))
        self.base.commit()

    def get_words(self):
        self.words = self.cur.execute("SELECT * FROM eng_words WHERE id IN (?, ?, ?, ?)", random.sample(range(1, 5001), 4)).fetchall()
        random.shuffle(self.words)
        return self.words
    
    def get_stat(self, user_id):
        self.stat = self.cur.execute("SELECT right, wrong FROM statistics WHERE user_id = '{}'".format(user_id)).fetchone()
        return self.stat

    
