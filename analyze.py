import re
from glob import glob
from itertools import chain, repeat

from main import generate_chunks
import pandas as pd

from talkbank_parser import MorParser

def read_files(filenames, n=2):
    parser = MorParser()
    for fn in filenames:
        print(fn)
        for uid, speaker, ngram in generate_chunks(parser.parse(fn), n):
            yield fn, uid, speaker, ngram


def read_data(filenames, n):
    data = pd.DataFrame(read_files(filenames, n))
    data.columns = 'filename uid speaker ngram'.split()

    data['group'] = data.filename.apply(lambda x: re.sub(r'^.*/|\d+[a-z]\.xml', '', x))
    data['session'] = data.filename.apply(lambda x: re.search(r'(\d+)[a-z]', x).group(1))
    return data


filenames = sorted(glob("/home/paul/Downloads/Manchester/**/*.xml"))
bigrams = read_data(filenames, 2)
trigrams = read_data(filenames, 3)

def analyze(target, other, topn=10):
    tops = target.ngram.value_counts()
    try:
        cutoff = tops.head(topn)[-1]
    except IndexError:
        return {}
    tops = tops[tops >= cutoff]

    other = other.ngram.value_counts()

    df = pd.DataFrame({ 'bigram': tops.index,
                        'frequency': tops,
                        'partner frequency': other.ix[tops.index].fillna(0).astype(int)
    }).sort_values(by=['frequency', 'bigram'],
                   ascending=False)
    del df['bigram']
    percent_top_ten = (len(target[target.ngram.isin(tops.index)])
                       / len(target))
    percent_top_ten = round(percent_top_ten, 2)
    df['ratio'] = df['frequency'].div(df['partner frequency']).round(2)
    return {'df': df,
            'total_bigram_tokens': len(target),
            'percent_top_ten': percent_top_ten}

def bidirectional_analysis(d1, d2, metadata=None):
    child = analyze(d1, d2)
    adult = analyze(d2, d1)
    if metadata:
        for key in metadata:
            child[key] = adult[key] = metadata[key]
    return {'child': child, 'adult': adult}

def aggregate_analysis(data):
    return bidirectional_analysis(data[data.speaker == 'CHI'], data[data.speaker == 'MOT'])

def within_group_analysis(data):
    return (bidirectional_analysis(data[((data.group == group) &
                                         (data.session == session) &
                                         (data.speaker == 'CHI'))],
                                   data[((data.group == group) &
                                         (data.session == session) &
                                         (data.speaker == 'MOT'))],
                                   {'group': group, 'session': session})
            for group in data.group.unique()
            for session in data.session.unique())

def across_group_analysis(data):
    return (bidirectional_analysis(data[((data.session == session) &
                                         (data.speaker == 'CHI'))],
                                   data[((data.session == session) &
                                         (data.speaker == 'MOT'))],
                                   {'session': session})
            for session in data.session.unique())

def extend(seq, length, pad=''):
    return chain(seq, repeat(pad, length - len(seq)))

def analysis_dict_to_csv(data):
    child = data['child']
    adult = data['adult']
    child_text = child['df'].to_csv().split('\n')[1:]
    adult_text = child['df'].to_csv().split('\n')[1:]
    length = max(len(child_text), len(adult_text))
    text = '\n'.join([',,'.join([x, y])
            for x, y in zip(extend(child_text, length),
                            extend(adult_text, length))])


aggregate_bigram_analysis = analyze(bigrams[bigrams.speaker == 'CHI'],
                                    bigrams[bigrams.speaker == 'MOT'],
                                    topn=20)
aggregate_trigram_analysis = analyze(trigrams[trigrams.speaker == 'CHI'],
                                     trigrams[trigrams.speaker == 'MOT'],
                                     topn=20)
across_group_bigrams = across_group_analysis(bigrams)
across_group_bigrams = across_group_analysis(trigrams)
