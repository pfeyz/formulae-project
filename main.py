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

def generate_chunks(utterances, gramsize):
    """Returns a generator of ngram strings of size `gramsize`, from list of
    utterance, filtered by speaker.

    """
    for uid, speaker, tokens in utterances:
        words = [x.word for x in tokens]
        if not utterance_filter(words):
            continue
        for ngram in ngrams(sanitize_words(words), gramsize):
            yield uid, speaker, ' '.join(ngram)

def ngrams_from_files(filenames, gramsize, speakers=None):
    if gramsize < 1:
        raise Exception('Invalid gramsize for allgrams: {}'.format(gramsize))
    parser = MorParser()
    utterances = (utterance
                  for fn in filenames
                  for utterance in parser.parse(fn))
    for _, speaker, gram in generate_chunks(utterances, gramsize):
        if speakers is None or speaker in speakers:
            yield gram

def allgrams(filenames, gramsize, speakers=None):
    """ Prints out all ngrams of size `gramsize` to stdout, filtered by speakers """
    for ngram in ngrams_from_files(filenames, gramsize, speakers):
        print(ngram)

def topngrams_from_file(filename, gramsize, freq_cutoff=1, speakers=None):
    counts = Counter(ngrams_from_files([filename], gramsize, speakers))
    top_10 = counts.most_common(10)
    if len(top_10) == 0:
        raise Exception('No utterances found')
    cutoff = top_10[-1][1]
    top_10 = [(item, count)
              for item, count in counts.items()
              if count >= cutoff and count > freq_cutoff]
    return sorted(top_10, key=lambda x: x[1], reverse=True)

def topngrams(filenames, gramsize, speakers=None, freq_cutoff=1):
    for filename in sorted(filenames):
        for gram, count in topngrams_from_file(filename, gramsize, speakers=speakers, freq_cutoff=freq_cutoff):
            print('{}, {}, {}'.format(filename, count, gram))
        print()

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

    top10_parser = subparsers.add_parser('top10',
                                         help='prints the number of utterances per speaker')
    top10_parser.add_argument('-s', '--speakers', default=None, help='Limit analysis to specific group of speakers, "CHI" or "CHI,MOT"')
    top10_parser.add_argument('-n', type=int, default=2, help='the size of the ngrams to use')
    top10_parser.add_argument('-f', '--freq-cutoff', type=int, default=1,
                              help='Number of times an ngram must occur to appear in output')
    top10_parser.add_argument('filenames', nargs='+')
    top10_parser.set_defaults(command='top10')

    args = parser.parse_args()

    speakers = None
    if 'speakers' in args:
        speakers = args.speakers
        if speakers is not None:
            speakers = speakers.split(',')

    if 'command' not in args:
        parser.print_help()
    elif args.command == 'speakerstats':
        speakerstats(args.filenames)
    elif args.command == 'top10':
        topngrams(args.filenames, args.n, speakers=speakers, freq_cutoff=args.freq_cutoff)
    elif args.command == 'allgrams':
        allgrams(args.filenames, args.n, speakers=speakers)
main()
