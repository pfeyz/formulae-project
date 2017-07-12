import argparse
from collections import Counter

from talkbank_parser import MorParser, MorToken

ILLEGAL_NGRAMS = {
    'one two',
    'two three',
    'a b',
    'b c',
    'c d',
    'd e',
    'e f',
    'f g',
    'uh oh',
    'oh oh',
    'um um',
    'um a',
    'beep beep',
    'tweet tweet',
    'night moon',
    'night night',
    'old MacDon',
    'MacDon had',
    'ring around',
    'around the',
    'the rosey',
    'J P',
    'New Investigator',
    'Tot Time',
    'one two three',
    'two three four',
    'three four five',
    'four five six',
    'five six seven',
    'six seven eight',
    'seven eight nine',
    'eight nine ten',
    'nine ten eleven',
    'old MacDon had',
    'MacDon had a',
    'ring around the',
    'around the rosey',
    'pop goes the',
    'a b c',
    'b c d',
    'c d e',
    'd e f',
    'e f g',
    'f g h',
    'h i j',
    'quack quack quack'}

def illegal_gram(gramstr):
    """ Returns false if ngram should be excluded from our analysis """
    if gramstr in ILLEGAL_NGRAMS:
        return True
    return False

def utterance_filter(words):
    """ Returns false if utterance should be excluded from our analysis """
    for i in range(2, 4):
        for j in range(0, len(words) - i + 1):
            if illegal_gram(' '.join(map(str, words[j:j+i]))):
                return False
    return True

def sanitize_words(words):
    """ Returns a cleaned up version of the utterance """
    edited = []
    for word in words:
        if word == '.':
            pass
        elif word == '?':
            pass
        elif word == '-':
            pass
        else:
            edited.append(word)
    return edited

def ngrams(words, n):
    """ Returns a list of ngrams of size `n` in list `words` """
    return [words[i:i+n]
            for i in range(len(words) - n + 1)]

def generate_chunks(utterances, gramsize, target_speakers=None):
    """Returns a generator of ngram strings of size `gramsize`, from list of
    utterance, filtered by speaker.

    """
    for _, speaker, tokens in utterances:
        if target_speakers is not None and speaker not in target_speakers:
            continue
        words = [x.word for x in tokens]
        include = utterance_filter(words)
        if include:
            yield from ngrams(sanitize_words(words), gramsize)

def allgrams(filenames, gramsize, speakers=None):
    """ Prints out all ngrams of size `gramsize` to stdout, filtered by speakers """
    if gramsize < 1:
        raise Exception('Invalid gramsize for allgrams: {}'.format(gramsize))
    parser = MorParser()
    utterances = (utterance
                  for fn in filenames
                  for utterance in parser.parse(fn))
    chunks = generate_chunks(utterances, gramsize, speakers)
    for chunk in chunks:
        print(' '.join(chunk))

def speakerstats(filenames):
    """ Prints out the number of utterances per speaker in `filenames` """
    parser = MorParser()
    utterances = (utterance
                  for fn in filenames
                  for utterance in parser.parse(fn))
    counts = Counter(speaker for _, speaker, _ in utterances)
    counts = sorted(counts.items(), key=lambda x: x[1])
    for speaker, count in counts:
        print(speaker, count)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    allgram_parser = subparsers.add_parser('allgrams',
                                           help='outputs all ngrams in input file')
    allgram_parser.add_argument('-n', type=int, default=2)
    allgram_parser.add_argument('-s', '--speakers', default=None)
    allgram_parser.add_argument('filenames', nargs='+')
    allgram_parser.set_defaults(command='allgrams')

    speakerstats_parser = subparsers.add_parser('speakerstats',
                                                help='prints the number of utterances per speaker')
    speakerstats_parser.add_argument('filenames', nargs='+')
    speakerstats_parser.set_defaults(command='speakerstats')

    args = parser.parse_args()
    if 'command' not in args:
        parser.print_help()
    elif args.command == 'speakerstats':
        speakerstats(args.filenames)
    elif args.command == 'allgrams':
        speakers = args.speakers
        if speakers is not None:
            speakers = speakers.split(',')
        allgrams(args.filenames, args.n, speakers=speakers)
main()
