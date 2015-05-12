from nltk.stem import PorterStemmer
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
from tutorial.DataModel import db, Course, Lecture, LectureWord
import operator
import peewee

class TopicModel(object):
    def __init__(self, lemmatize = True):
        self.debug = False
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.lemmatize = lemmatize
        self.stopwords = set(stopwords.words('english'))


    def lemstem(self, token):
        if self.lemmatize:
            return self.lemmatizer.lemmatize(token)
        else:
            return self.stemmer.stem(token)


    def extractTokens(self, text):
        try:
            tokens = word_tokenize(text)
        except UnicodeEncodeError as e:
            tokens = []

        token_dict = {}
        for token in tokens:
            token = token.lower()
            if not token.isalpha():
                continue
            try:
                token = token.encode('utf8')
                lemstem_word = self.lemstem(token)
                if len(lemstem_word) > 2 and not lemstem_word in self.stopwords:
                    if self.debug:
                        print "{0}: {1}".format(token, lemstem_word)
                    if token_dict.has_key(lemstem_word):
                        token_dict[lemstem_word] += 1
                    else:
                        token_dict[lemstem_word] = 1
            except Exception as e:
                pass
        return token_dict

    def getLectureRecord(self, lectureId):
        try:
            data = Lecture.select().where(Lecture.id == lectureId).get()
            return data
        except Exception as e:
            return None

    def extractLectureTokens(self, lecture):
        if lecture == None:
            return False

        text = lecture.content
        tokens = self.extractTokens(text)
        sorted_tokens = sorted(tokens.items(), key=operator.itemgetter(1))

        for token in sorted_tokens:
            if self.debug:
                print token
            try:
                with db.transaction() as txn:
                    LectureWord.create(
                        lecture = lecture,
                        word = token[0],
                        count = token[1],
                        active = True
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for lecture {0}, word {1}, {2}".format(lecture.id, token[0], e)

        return True


    def getCourseRecord(self, courseId):
        try:
            data = Course.select().where(Course.id == courseId).get()
            return data
        except Exception as e:
            return None

    def extractCourseTokens(self, course):
        lectures = list(Lecture.select().where(Lecture.course == course))

        print "Lecture count: {0}".format(len(lectures))
        for lecture in lectures:
            print "Lecture: {0}".format(lecture.id)
            result = self.extractLectureTokens(lecture)

    def extractAllCourseTokens(self):
        courses = Course.select()#.where(Course.id == 2)
        for course in list(courses):
            print course.id, course.name
            self.extractCourseTokens(course)


if __name__ == '__main__':
    tm = TopicModel()
    tm.extractAllCourseTokens()

