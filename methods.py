import re
import pandas as pd
import numpy as np
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from random import random
from itertools import repeat as _repeat

sore_words = ['болит']
get_words = ['выведи']
delete_words = ['удали', 'удоли']
get_stats_words = ['статистику']
get_table_words = ['таблицу', 'данные']
get_anal_words = ['анализ', 'байеса', 'вероятности']
all_words = ['всю', 'все', 'всем']

day_words = ['дням']
time_words = ['часам']
#to do - месяц, неделя и тд
columns = ['id', 'pain_type', 'pain_cause', 'date_time']


dn2id = {'Monday': 0,
         'Tuesday': 1,
         'Wednesday': 2,
         'Thursday': 3,
         'Friday': 4,
         'Saturday': 5,
         'Sunday': 6}

day_time = {0: (pd.Timestamp('00:00').time(), pd.Timestamp('6:00').time()),
            1: (pd.Timestamp('06:00').time(), pd.Timestamp('12:00').time()),
            2: (pd.Timestamp('12:00').time(), pd.Timestamp('18:00').time()),
            3: (pd.Timestamp('18:00').time(), pd.Timestamp('23:59:59').time())}


def if_sore(text):
    text = text.lower()
    if sum(text.find(word) for word in sore_words) != -1 * len(sore_words):
        return 0
    elif sum(text.find(word) for word in get_words) != -1 * len(get_words) and sum(text.find(word) for word in get_stats_words) != -1 * len(get_stats_words):
        return 1
    elif sum(text.find(word) for word in get_words) != -1 * len(get_words) and sum(text.find(word) for word in get_anal_words) != -1 * len(get_anal_words):
        return 5
    elif sum(text.find(word) for word in get_words) != -1 * len(get_words) or sum(text.find(word) for word in get_words) != -1 * len(get_words) and sum(text.find(word) for word in get_table_words) != -1 * len(get_table_words):
        return 2
    elif sum(text.find(word) for word in delete_words) != -1 * len(delete_words) or sum(text.find(word) for word in delete_words) != -1 * len(delete_words) and sum(text.find(word) for word in all_words) != -1 * len(all_words):
        return 3
    else:
        return 4

def preproc_record(text):
    text = text.lower().split(',')
    pt = ' '.join([word for word in re.sub(r'[^а-яa-z ]', '', text[0]).split()
                   if word not in sore_words])

    if len(text) > 1:
        pc = ' '.join([word for word in
                       re.sub(r'[^а-яa-z ]', '', text[1]).split()])
        return pt, pc
    else:
        return pt, '-'

def preproc_table(text):
    text = text.lower()
    if sum(text.find(word) for word in all_words) != -1 * len(all_words):
        return []

def preproc_delete(text):
    text = text.lower()
    if sum(text.find(word) for word in all_words) != -1 * len(all_words):
        return True
    return False

def preproc_stats(text):
    text = text.lower()
    if sum(text.find(word) for word in day_words) != -1 * len(day_words):
        return 0
    elif sum(text.find(word) for word in time_words) != -1 * len(time_words):
        return 1
    else:
        return 2

def preproc_anal(text):
    dec = re.findall(r'\d', text)
    if dec:
        return int(''.join(dec))
    return 0

def cell_t(tst):
    for i, (key, val) in enumerate(day_time.items()):
        if val[0] <= tst < val[1]:
            return i
    return -1

def choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            n += 0.0    # convert to float for a small speed improvement
            return [population[int(random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random() * total, 0, hi)]
            for i in _repeat(None, k)]

class StatsMaker(object):
    def __init__(self, df):
        self.df = df
        self.df['day'] = self.df.date_time.apply(lambda t: dn2id[pd.Timestamp(t).day_name()])
        self.df['time'] = self.df.date_time.apply(lambda t: cell_t(pd.Timestamp(t).time()))
        del self.df['date_time']
        self.df['day_time'] = np.round(self.df.day + self.df.time / 4, 1)


        a = np.arange(7)
        b = np.array([0, 1, 2, 3]) / 4
        c = np.zeros((len(a), len(b)))
        for i in range(len(a)):
            for j in range(len(b)):
                c[i, j] = a[i] + b[j]
        c = sorted(list(set(np.round(c.reshape(-1), 1))))
        self.time = [a, b, c]

    def plot_hist(self, column=2): # 0 => day, 1 => time, 2 => day_time
        idx2col_name = {0: 'day', 1: 'time', 2: 'day_time'}
        cur_df = self.df[['pain_type', idx2col_name[column]]]
        time = self.time[column]
        if column == 0:
            rd = {val: key[:3] for key, val in dn2id.items()}
            ind = [rd[int(x)] for x in time]
        elif column == 2:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri',
                    'Sat', 'Sun']
            pdays = list(range(1, 5))
            all_parts = []
            for day in days:
                for pday in pdays:
                    all_parts.append(day + ' ' + str(pday) + '.')
            rd = {time[i]: all_parts[i] for i in range(len(time))}
            ind = [rd[x] for x in time]
        else:
            ind = time


        dictionary = defaultdict(Counter)
        for p, v in cur_df.values:
            dictionary[v][p] += 1

        d = defaultdict(list)
        all_names = list(set(cur_df.pain_type))
        for t in time:
            if t in dictionary.keys():
                for name in all_names:
                    if name in dictionary[t].keys():
                        d[name].append(dictionary[t][name])
                    else:
                        d[name].append(0)
            else:
                for name in all_names:
                    d[name].append(0)

        N = len(time)
        n = len(all_names)

        colors = list(mcolors.CSS4_COLORS.keys())
        colors = choices(colors, k=n)
        width = 0.35

        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_axes([0,0,1,1])

        for i, name in enumerate(all_names):
            ax.bar(ind, d[name], width, color=colors[i],
                   bottom = np.sum([d[all_names[j]] for j in range(i)], axis=0))

        ax.set_ylabel('Частоты')
        ax.set_title('Части недели')
        ax.legend(labels=all_names)

        path = 'hist.png'
        fig.savefig(path, bbox_inches='tight')
        return path

    def bayessian_analizer(self, n=3):
        cur_df = self.df[['pain_type', 'pain_cause']]
        Pa = Counter(cur_df.pain_cause)
        Pba = Counter(cur_df.pain_type + ['|']*len(cur_df) + cur_df.pain_cause)

        swa = sum(list(Pa.values()))
        Pa = {key: val / swa for key, val in Pa.items()}
        swba = sum(list(Pba.values()))
        Pba = {key: val / swba for key, val in Pba.items()}

        all_pt = list(set(cur_df.pain_type))
        all_pc = list(set(cur_df.pain_cause))

        Bayes_P = {}
        for pt in all_pt:
            Pb = sum([Pa[pc] * (Pba[pt+'|'+pc] if pt+'|'+pc in Pba.keys() else 0.) for pc in all_pc])
            for pc in all_pc:
                Bayes_P[pc + '|' + pt] = (Pa[pc] * (Pba[pt+'|'+pc] if pt+'|'+pc in Pba.keys() else 0.)) / Pb

        Bayes_P = sorted([(key, val) for key, val in Bayes_P.items() if key[0] != '-' and val > 0.],
                         key = lambda x: -x[1])[:n]
        return Bayes_P
