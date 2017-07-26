import pandas as pd

def get_dataset(cached=True):
    if cached:
        unigrams = pd.read_pickle('unigrams.pkl')
        bigrams = pd.read_pickle('bigrams.pkl')
        trigrams = pd.read_pickle('trigrams.pkl')
    else:
        filenames = sorted(glob("/home/paul/Downloads/Manchester/**/*.xml"))
        unigrams = read_data(filenames, 1)
        bigrams = read_data(filenames, 2)
        trigrams = read_data(filenames, 3)

        unigrams.to_pickle(open('unigrams.pkl', 'wb'))
        bigrams.to_pickle(open('bigrams.pkl', 'wb'))
        trigrams.to_pickle(open('trigrams.pkl', 'wb'))
    return unigrams, bigrams, trigrams
