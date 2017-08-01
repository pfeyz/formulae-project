"""

Output the parent's most frequent ngrams, excluding those ngrams that
contain words not present in the child's speech during that same session.

"""

from collections import Counter
from glob import glob
from os import path

from talkbank_parser import MorParser
from main import generate_chunks

MANCHESTER_ROOT = None # the path to the top-level manchester folder
TARGET_CHILD = None # the child to focus on

assert MANCHESTER_ROOT and TARGET_CHILD, "You must set the MANCHESTER_ROOT and TARGET_CHILD variables"

MANCHESTER_ROOT = path.expanduser(MANCHESTER_ROOT)

def read_files(filenames, gram_size=1):
    """Returns a list of ngrams, each ngram represented as a 4-tuple of filename,
    utterance id, speaker name, and list of words in the ngram

    """
    assert isinstance(filenames, list), "filenames argument must be a list"
    parser = MorParser()
    for fn in filenames:
        for uid, speaker, ngram in generate_chunks(parser.parse(fn), gram_size):
            yield fn, uid, speaker, ngram

def unique_ngrams(filenames, target_speaker, gram_size=1):
    """Returns a set of all unique ngrams observed in file `filename`"""
    vocab = list(read_files(filenames, gram_size=gram_size))
    child_vocab = set()
    for _, _, speaker, ngram in vocab:
        if speaker == target_speaker:
            child_vocab.add(ngram)
    return child_vocab

def speaker_vocab(filenames, target_speaker):
    """Returns a set of the unique words that were uttered by speaker in the files."""
    return unique_ngrams(filenames, target_speaker, gram_size=1)

def parent_shared_ngrams(filenames, gram_size):
    """Returns a set of all unique ngrams that are shared with the child"""
    all_ngrams = list(read_files(filenames, gram_size=gram_size))
    parent_vocab = set()
    child_vocab = speaker_vocab(filenames, 'CHI')
    for _, _, speaker, ngram in all_ngrams:
        if speaker == "MOT":
            for word in ngram.split():
                if word not in child_vocab:
                    break
            else:
                parent_vocab.add(ngram)
    return parent_vocab

def filtered_parent_freq_count(filenames, gram_size):
    """Returns a frequency count of the ngrams in the parent's speech, excluding
    those that contained any words that did not appear in the child's speech.

    """
    counts = Counter()
    vocab = list(read_files(filenames, gram_size=gram_size))
    parent_list = parent_shared_ngrams(filenames, gram_size=gram_size)
    for _, _, speaker, ngram in vocab:
        if speaker == "MOT" and ngram in parent_list:
            counts[ngram] += 1
    return counts.most_common(10)

def to_csv(output):
    for element in output:
        ngram, quant = element
        print(ngram, ",", quant)

def main():
    """Output the parent's most frequent ngrams, excluding those ngrams that
    contain words not present in the child's speech during that same session.

    """
    glob_pattern = "{root}/{child}/*.xml".format(root=MANCHESTER_ROOT, child=TARGET_CHILD)
    corpus_files = glob(glob_pattern)
    for filename in corpus_files:
        print(filename)
        to_csv(filtered_parent_freq_count([filename], 2))

if __name__ == "__main__":
    main()
