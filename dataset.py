import re
import sqlite3
from os import path
from glob import glob

import numpy as np
import pandas as pd

from main import generate_chunks
from talkbank_parser import MorParser

def read_ngrams_from_files(filenames, gramsize=2):
    """Returns all a generator of all ngrams in files.

    args

    - filenames :: a list of strings, paths to xml files.
    - n :: the size of the ngrams to create

    """
    parser = MorParser()
    for xmlfn in filenames:
        print(xmlfn)
        for uid, speaker, ngram in generate_chunks(parser.parse(xmlfn), gramsize):
            yield xmlfn, uid, speaker, ngram

def read_data(filenames, gramsize):
    """Returns a DataFrame with a row for every ngram in the files.

    args

    - filenames :: a list of strings, paths to xml files.
    - n :: the size of the ngrams to create

    """
    data = pd.DataFrame(read_ngrams_from_files(filenames, gramsize))
    data.columns = 'filename uid speaker ngram'.split()

    return data

def get_dataset(filenames, cached=True, gram_sizes=None):
    """Read xml files specified in `filenames` and returns a dictionary with 3 data
    frames, one for each ngram size of 1, 2 and 3. If data has been loaded
    before, read from a sql DB instead of reparsing XML files.

    NOTE: cacheing is keyed ONLY on directory name!

    args

    - filenames :: a list of strings, paths to xml files.
    - n :: the size of the ngrams to create

    Returns a dictionary with 'unigram', 'bigram' and 'trigram' keys, with
    DataFrames as values.

    """

    gram_sizes = gram_sizes or [1, 2, 3]

    conn = sqlite3.connect('cached.sqlite3')
    filenames = sorted(glob(filenames) if isinstance(filenames, str) else filenames)
    table_prefix = path.commonpath(filenames)
    table_prefix = path.basename(table_prefix) or path.dirname(table_prefix)
    data = {}
    ngrams = {'unigram': 1, 'bigram': 2, 'trigram': 3}
    ngram_rev = {1: 'unigram', 2: 'bigram', 3: 'trigram'}
    ngrams = {key: val
              for key, val in ngrams.items()
              if val in gram_sizes}
    if cached:
        for key in ngrams:
            data[key] = pd.read_sql(
                'select * from "{prefix}-{ngram}"'.format(prefix=table_prefix,
                                                          ngram=key),
                conn)
    else:
        for name, size in ngrams.items():
            print(name)
            data[name] = read_data(filenames, size)
            data[name].to_sql('{prefix}-{ngram}'.format(prefix=table_prefix, ngram=name),
                              conn,
                              if_exists='replace')
    conn.close()
    if gram_sizes == [1, 2, 3]:
        return data['unigram'], data['bigram'], data['trigram']
    return [data[ngram_rev[n]] for n in gram_sizes]

def get_manchester(filenames, cached=True, gram_sizes=None):
    """Calls get_dataset and adds corpus, session and part columns to the resulting
    DataFrames. """
    frames = get_dataset(filenames, cached, gram_sizes)
    for data in frames:
        data['corpus'] = data.filename.apply(lambda x: re.sub(r'^.*/|\d+[a-z]\.xml', '', x))
        data['session'] = (data.filename
                           .apply(lambda x: re.search(r'(\d+)[a-z]', x).group(1))
                           .pipe(pd.to_numeric))
        data['part'] = np.where(data.filename.str.endswith('a.xml'),
                                'a', 'b')
    return frames
