#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import pandas as pd

class SQLiteAdapter3000(object):
    def __init__(self, db_path='records.db'):
        self.conn = sqlite3.connect("records.db")
        self.cursor = self.conn.cursor()


    def add_data_to_db(self, *data):
        self.cursor.execute("""INSERT INTO records
                            VALUES (?, ?, ?, ?)""",
                            data)
        self.conn.commit()

    def get_data_by_cond(self, ID, conditions=[]): # conditions example: ["pain_type == 'head'", "date_time > 2018-12-07"]
        sql_req = "SELECT * FROM records where id == {0}".format(ID)
        sql_req += " and " + " and ".join(conditions) if conditions else ""
        self.cursor.execute(sql_req)
        res = self.cursor.fetchall()
        return pd.DataFrame(res, columns=['ID', 'pain_type', 'pain_cause', 'date_time'])

    def get_data(self, ID, dt_type=1, **kwargs): #0 : ==, 1: >=, 2: <=
        dt = {0: '==', 1: '>=', 2: '<='}

        sql = "SELECT * FROM records where id == {0}".format(ID)
        sql += " and " + " and ".join(["{0} == '{1}'".format(key, val) for key, val in kwargs.items() if key != 'date_time'])
        sql += " and date_time {0} {1}".format(dt[dt_type], kwargs['date_time']) if 'date_time' in kwargs.keys() else ""

        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return pd.DataFrame(res, columns=['ID', 'pain_type', 'pain_cause', 'date_time'])

    def close(self):
        self.conn.close()

    def delete_last(self, ID):
        sql = """DELETE FROM records WHERE id == {0} and date_time == (SELECT MAX(date_time) FROM records WHERE id = {1});""".format(ID, ID)
        self.cursor.execute(sql)
        self.conn.commit()

    def delete_all(self, ID):
        sql = """DELETE FROM records WHERE id == {0};""".format(ID)
        self.cursor.execute(sql)
        self.conn.commit()


if __name__ == '__main__':
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE records
                    (id ID,
                    pain_type str,
                    pain_cause str,
                    date_time datetime)
                """)
    conn.commit()
