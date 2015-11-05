import json
from Teacher import Teacher


class StopWord(object):
    def __init__(self):
        self.words = self.assemble()

    def assemble(self):
        teacher = Teacher()
        words = set(self.load_stopwords('en'))
        words = words.union(set(self.load_stopwords('et')))
        words = words.union(set(teacher.names))
        words = sorted(list(words))
        return words

    def load_stopwords(self, language):
        fname = 'stopwords_' + language + '.json'
        words = json.loads(open(fname).read())
        return words


if __name__ == '__main__':
    sw = StopWord()
    print sw.words