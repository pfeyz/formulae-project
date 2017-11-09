import re

def parse_data(document):
    category = None
    tags = {}
    for line in document.split('\n'):
        word = line.strip().lower()
        if word.isspace():
            continue
        if word.endswith(':'):
            category = word[:-1]
        else:
            tags[word] = category.lower()
    return tags

class FunctionWordTagger():
    def __init__(self):
        self.word_to_tag = parse_data(open('function-words.txt').read())
        self.tag_to_words = {}
        for word, tag in self.word_to_tag.items():
            self.tag_to_words[tag] = self.tag_to_words.get(tag, [])
            self.tag_to_words[tag].append(word)

    def tag(self, word, include_content=False):
        if word in list('.?!'):
            return 'boundary'
        if word == ',':
            return 'pause'
        return self.word_to_tag.get(word.lower(),
                                    'content' if include_content else None)

    def categorize(self, word):
        return 'F' if self.word_to_tag.get(word) else 'C'

    def tag_sentence(self, sentence):
        return ' '.join(self.tag(word, True)
                        for word in sentence.split(' '))

    def filter_sentence(self, sentence, kind='F'):
        assert kind in ['F', 'C']
        sentence = re.sub(r'\s+', ' ', sentence)
        return ' '.join([word for word in sentence.split(' ')
                         if self.categorize(word) == kind])
