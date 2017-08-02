from itertools import chain, repeat

import pandas as pd
import numpy as np

def topn_with_ties(series, n):
    try:
        cutoff = series.nlargest(n)[-1]
    except IndexError:
        return None
    return series[series >= cutoff]

def top_20_by_speaker_session_split(df, n):
    label_len = len(n)+1 if type(n) is list else n
    d = (df
         .assign(period=pd.cut(df.session, n))
         [df.speaker.isin(['MOT', 'CHI'])]
         .groupby('corpus period speaker'.split())
         .apply(lambda x: topn_with_ties(x.ngram.value_counts(), 20)))
    d = d.reset_index()
    return d.rename(columns={'level_3': 'ngram',
                             'ngram': 'count'})

def top_20_by_speaker_file_split(df):
    d = (df
         [df.speaker.isin(['MOT', 'CHI'])]
         .groupby('filename speaker'.split())
         .apply(lambda x: topn_with_ties(x.ngram.value_counts(), 20)))
    d = d.reset_index()
    return d.rename(columns={'level_2': 'ngram',
                             'ngram': 'count'})[d['ngram'] > 1]

def shared_vocab(unigrams):
    counts = (u[u.speaker.isin(['MOT', 'CHI'])]
              .groupby(['session', 'speaker', 'ngram'])
              .count().gt(0)
              .astype(int)
              .sum(level=[0, 2]))
    return counts[counts.eq(2)].dropna()

def analyze(target, other, topn=10, metadata=None):
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
    df['total_bigram_tokens'] = len(target)
    df['percent_top_ten'] = percent_top_ten

    if metadata:
        for key in metadata:
            print(key, metadata[key])
            df[key] = metadata[key]
    return df

def bidirectional_analysis(d1, d2, metadata=None):
    child = analyze(d1, d2, metadata={'target': 'CHI'})
    adult = analyze(d2, d1, metadata={'target': 'MOT'})
    df = pd.concat([child, adult])
    if metadata:
        for key in metadata:
            df[key] = metadata[key]
    return df

def aggregate_analysis(data):
    return bidirectional_analysis(data[data.speaker == 'CHI'], data[data.speaker == 'MOT'])

def within_group_analysis(data):
    return (bidirectional_analysis(data[((data.corpus == corpus) &
                                         (data.session == session) &
                                         (data.speaker == 'CHI'))],
                                   data[((data.corpus == corpus) &
                                         (data.session == session) &
                                         (data.speaker == 'MOT'))],
                                   {'corpus': corpus, 'session': session})
            for corpus in data.corpus.unique()
            for session in data.session.unique())

def across_corpus_analysis(data):
    return pd.concat(bidirectional_analysis(data[((data.session == session) &
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

# aggregate_bigram_analysis = bidirectional_analysis(bigrams[bigrams.speaker == 'CHI'],
#                                                    bigrams[bigrams.speaker == 'MOT'])
# aggregate_bigram_analysis = bidirectional_analysis(trigrams[trigrams.speaker == 'CHI'],
#                                                    trigrams[trigrams.speaker == 'MOT'])

# across_corpus_bigrams = across_corpus_analysis(bigrams)
# across_corpus_bigrams = across_corpus_analysis(trigrams)
