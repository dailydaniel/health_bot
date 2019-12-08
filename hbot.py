#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import argparse
import io

from functools import reduce
import re

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from datetime import datetime
import sqlite3
import pandas as pd

from create_db import *
from methods import *

# sql = SQLiteAdapter3000()

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Привет, я бот, умею запоминать твои болячки и выводить интересную статистику.\nПример 1: болит <что болит>, <предпологаемая причина> (причину писать не обязательно).\nПример 2: Выведи все за последний месяц.\nПример 3: ...")

def text(bot, update):
    text = update.message.text
    ID = update.message.chat_id
    new_sore = if_sore(text)
    if new_sore == 0:
        pt, pc = preproc_record(text)
        sql = SQLiteAdapter3000()
        sql.add_data_to_db(ID, pt, pc, str(datetime.now()))
        sql.close()
        bot.send_message(chat_id=ID,
                         text='записал: болит {0}, потому что {1}'.format(pt, pc))
    elif new_sore == 1:
        column = preproc_stats(text)
        sql = SQLiteAdapter3000()
        df = sql.get_data_by_cond(ID)
        st = StatsMaker(df)
        file_path = st.plot_hist(column)
        with open(file_path, 'rb') as f:
            data = f.read()
        bot.sendDocument(chat_id=ID,
                         document=io.BytesIO(data),
                         filename=file_path)
    elif new_sore == 2:
        cond = preproc_table(text)
        sql = SQLiteAdapter3000()
        df = sql.get_data_by_cond(ID, cond)
        df.to_csv('data.csv', sep=';', encoding='utf-8')
        sql.close()
        with open('data.csv', 'rb') as f:
            data = f.read()
        bot.sendDocument(chat_id=ID,
                         document=io.BytesIO(data),
                         filename='data.csv')
    elif new_sore == 3:
        del_all = preproc_delete(text)
        sql = SQLiteAdapter3000()
        if del_all:
            sql.delete_all(ID)
        else:
            sql.delete_last(ID)
        bot.send_message(chat_id=update.message.chat_id,
                         text='удалил')
    elif new_sore == 5:
        n = preproc_anal(text)
        sql = SQLiteAdapter3000()
        df = sql.get_data_by_cond(ID)
        st = StatsMaker(df)
        if n:
            anal = st.bayessian_analizer(n)
        else:
            anal = st.bayessian_analizer()
        postpr = [(key[:key.find('|')], key[key.find('|')+1:], round(val, 4))
                  for key, val in anal]
        postpr = '\n'.join(['Вероятность причины [{0}] для боли в [{1}]: {2}'.format(x, y, z)
                            for x, y, z in postpr])
        bot.send_message(chat_id=update.message.chat_id,
                         text=postpr)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='пока эта фича недоступна')

if __name__ == '__main__':
    TOKEN = '1018670870:AAFd8rPaku2PQBRIJxNsMf6u89Q2nm1xCKU'
    REQUEST_KWARGS={
        'proxy_url': 'socks5h://s5.priv.opennetwork.cc:1080',
        'urllib3_proxy_kwargs': {
            'username': 'SX1_62016058',
            'password': 'ZckuNd6nX7TkvrgL',
        }
    }
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    mes1 = MessageHandler(Filters.text, text)
    dispatcher.add_handler(mes1)

    updater.start_polling()
