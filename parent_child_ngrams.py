"""Generates an excel file with the top 20 child and adult ngrams and their
counts, analyzed grouped by periods. Yellow cells indicate ngrams that are
shared by parent and adult.

Outputs to an excel file named 'parent_child_ngrams.xls'

"""

import xlwt
import numpy as np
import pandas as pd

from analyze import top_20_by_speaker_session_split
from dataset import get_manchester

BOLD = xlwt.easyxf('font: bold True;')
HIGHLIGHT = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')

def child_adult_two_col(df):
    data = (df
            .groupby(['corpus', 'period', 'speaker'])
            .apply(lambda x: x.assign(uid=np.sum([
                x.corpus,
                x.period.astype(str),
                '/',
                np.arange(len(x)).astype(str)], axis=0))))
    data = pd.merge(data[data.speaker == 'CHI'],
                    data[data.speaker == 'MOT'],
                    on='uid',
                    suffixes=(' 1', ' 2'),
                    how='outer')
    data['corpus'] = data['corpus 1'].combine_first(data['corpus 2'])
    data['period'] = data['period 1'].combine_first(data['period 2'])
    for key in ['speaker 1', 'speaker 2', 'ngram 1', 'ngram 2']:
        data[key] = data[key].fillna('')
    data = (data
            .drop(['uid', 'corpus 1', 'corpus 2', 'period 1', 'period 2'], axis='columns'))
    cols = data.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    return data[cols]

def get_shared_words(df, item):
    key = (item.corpus, item.period)
    if np.nan in key:
        return {}
    # if key in cache:
    #     return cache[key]
    df = df[(df.corpus.eq(item.corpus) & df.period.eq(item.period))]
    words = set(df['ngram 1'].values).intersection(df['ngram 2'].values)
    # cache[key] = words
    return words

def to_excel(workbook, sheetname, df):
    table = workbook.add_sheet(sheetname, cell_overwrite_ok=True)
    for index, text in enumerate(df.columns):
        table.write(0, index + 1, text, BOLD)
    XLROW = 1
    PREV_PERIOD = 1
    for row in df.index:
        shared_words = get_shared_words(df, df.loc[row])
        period = df.loc[row, 'period']
        if period != PREV_PERIOD:
            XLROW += 1
        PREV_PERIOD = period
        for index, col in enumerate(df.columns):
            val = df.loc[row, col]
            shared = val in shared_words
            if col in ['ngram 1', 'ngram 2'] and shared:
                table.write(XLROW, index + 1, str(val), HIGHLIGHT)
            else:
                table.write(XLROW, index + 1, str(val))
        XLROW += 1

workbook = xlwt.Workbook()

# bins = [(i * 6)+1 for i in range(7)]
bins = [1, 7, 13, 19, 25, 31, 36]

unigrams, bigrams, trigrams = get_manchester('/home/paul/Downloads/Manchester/**/*.xml')

to_excel(workbook, 'bigrams',
         child_adult_two_col(top_20_by_speaker_session_split(bigrams, bins)))
to_excel(workbook, 'trigrams',
         child_adult_two_col(top_20_by_speaker_session_split(trigrams, bins)))
workbook.save('parent_child_ngrams.xls')
