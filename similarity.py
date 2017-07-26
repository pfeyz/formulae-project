import pandas as pd
import numpy as np

source = pd.read_pickle('trigrams.pkl')
source = source[source.session == '01']

adult = get_proportions(source, 'MOT')
child = get_proportions(source, 'CHI')

def overlap(a, b, randomize=False):
    if randomize:
        b.index = np.random.permutation(b.index)
    a, b = a.align(b, fill_value=0)
    numer = np.dot(a, b)
    denom = np.square(a).sum() + np.square(b).sum()
    return 2 * numer / denom

x = pd.Series([0.2, 0.3, 0.5])
y = pd.Series([0.1, 0.6, 0.3])

for x in (overlap(adult, child, True) for _ in range(1000)): print(x)
