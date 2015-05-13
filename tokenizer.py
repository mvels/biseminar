from nltk.stem import PorterStemmer
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
from tutorial.DataModel import db, Course, Lecture, LectureWord, CourseWord
import operator
import peewee

class Tokenizer(object):
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
            token = token.encode('utf8')
            token = token.lower()
            if not token.isalpha():
                continue
            try:
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

    def getLectures(self, course):
        lectures = Lecture.select().where(Lecture.course == course)
        return list(lectures)

    def extractCourseTokens(self, lectures):
        print "Lecture count: {0}".format(len(lectures))
        for lecture in lectures:
            print "Lecture: {0}".format(lecture.id)
            result = self.extractLectureTokens(lecture)

    def getCourses(self, courseId=0):
        if courseId:
            courses = Course.select().where(Course.id == courseId)
        else:
            courses = Course.select()
        return list(courses)

    def extractAllCourseTokens(self):
        for course in self.getCourses():
            print course.id, course.name
            self.extractCourseTokens(course)

    def getLectureWords(self, lecture):
        lectureWords = list(LectureWord.select().where(LectureWord.lecture == lecture))
        return lectureWords

    def createCourseTokens(self):
        for course in self.getCourses():
            print "{}: {}".format(course.id, course.name.encode('utf8'))
            token_dict = {}
            for lecture in self.getLectures(course):
                lectureWords = self.getLectureWords(lecture)
                for lectureWord in lectureWords:
                    if token_dict.has_key(lectureWord.word):
                        token_dict[lectureWord.word] += 1
                    else:
                        token_dict[lectureWord.word] = 1
            sorted_tokens = sorted(token_dict.items(), key=operator.itemgetter(1))
            for token in sorted_tokens:
                try:
                    with db.transaction() as txn:
                        CourseWord.create(
                            course = course,
                            word = token[0],
                            count = token[1],
                            active = True
                        )
                        txn.commit()
                except peewee.OperationalError as e:
                    print "Could not create a record for course {0}, word {1}, {2}".format(course.id, token[0], e)


if __name__ == '__main__':
    tok = Tokenizer()
    # tok.debug = True
    # tok.extractAllCourseTokens()
    tok.createCourseTokens()


