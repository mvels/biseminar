from nltk.stem import PorterStemmer
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from tutorial.DataModel import db, Course, Lecture

class TopicModel(object):
    def getLectureRecord(self):
        try:
            data = Lecture.select().where(Lecture.id == 260).get()
            return data.content
        except Exception as e:
            return ''

    def dostuff(self):
        text = self.getLectureRecord()
        stemmer = PorterStemmer()
        lemmatizer = WordNetLemmatizer()
        try:
            tokens = word_tokenize(text)
        except UnicodeEncodeError as e:
            pass

        for token in tokens:
            if not token.isalpha():
                continue

            try:
                token = token.encode('utf8')
                stemword = stemmer.stem(token)
                # if len(stemword) > 2:
                #     # print "{0}: {1}".format(token, stemword)
                #     print "{0}".format(stemword)
                lemword = lemmatizer.lemmatize(token)
                if len(lemword) > 2:
                    print "{0}: {1}".format(token, lemword)
                    # print "{0}".format(lemword)
            except Exception as e:
                pass

if __name__ == '__main__':
    tm = TopicModel()
    tm.dostuff()

