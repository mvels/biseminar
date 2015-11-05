from nltk.stem import PorterStemmer
from nltk import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
from db.DataModel import db, Course, Lecture, LectureWord, CourseWord, CorpusWord
import operator
import peewee
from StopWord import StopWord


class Tokenizer(object):
    def __init__(self, lemmatize=True):
        self.debug = False
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.lemmatize = lemmatize
        self.stopwords = self.get_stopwords()

    def get_stopwords(self):
        sw = StopWord()
        return set(sw.words)
        # return set(stopwords.words('english'))

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
            # token = token.encode('utf8')
            token = token.lower()

            #check if string consists of alphabetic characters only
            if not token.isalpha():
                continue

            try:
                lemstem_word = self.lemstem(token)
            except Exception as e:
                lemstem_word = token
                # print 'Could not lemmatize: {}'.format(token.encode('utf8'))

            if len(lemstem_word) > 2 and not lemstem_word in self.stopwords:
                if self.debug:
                    print "{0}: {1}".format(token.encode('utf8'), lemstem_word.encode('utf8'))
                if token_dict.has_key(lemstem_word):
                    token_dict[lemstem_word] += 1
                else:
                    token_dict[lemstem_word] = 1

        return token_dict

    def getLectureRecord(self, lectureId):
        try:
            data = Lecture.select().where(Lecture.id == lectureId).get()
            return data
        except Exception as e:
            return None

    def extractLectureTokens(self, lecture):
        if lecture is None:
            return False

        text = lecture.content
        tokens = self.extractTokens(text)
        sorted_tokens = sorted(tokens.items(), key=operator.itemgetter(1))

        for token in sorted_tokens:
            try:
                with db.transaction() as txn:
                    LectureWord.create(
                        lecture=lecture,
                        word=token[0],
                        count=token[1],
                        active=True,
                        weight=0
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for lecture {0}, word {1}, {2}".format(lecture.id, token[0], e)

            if self.debug:
                print token

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
            lectures = self.getLectures(course)
            self.extractCourseTokens(lectures)

    def getLectureWords(self, lecture):
        lectureWords = list(LectureWord.select().where(LectureWord.lecture == lecture))
        return lectureWords

    def createCourseTokens(self):
        for course in self.getCourses():
            print "{}: {}".format(course.id, course.name.encode('utf8'))
            token_dict = {}
            lecture_token = {}

            for lecture in self.getLectures(course):
                lectureWords = self.getLectureWords(lecture)
                for lectureWord in lectureWords:
                    if not token_dict.has_key(lectureWord.word):
                        token_dict[lectureWord.word] = 0
                        lecture_token[lectureWord.word] = 0

                    token_dict[lectureWord.word] += lectureWord.count
                    lecture_token[lectureWord.word] += 1
            sorted_tokens = sorted(token_dict.items(), key=operator.itemgetter(1))
            for token in sorted_tokens:
                try:
                    with db.transaction() as txn:
                        CourseWord.create(
                            course=course,
                            word=token[0],
                            count=token[1],
                            active=True,
                            lectures=lecture_token[token[0]]
                        )
                        txn.commit()
                except peewee.OperationalError as e:
                    print "Could not create a record for course {0}, word {1}, {2}".format(course.name.encode('utf8'),
                                                                                           token[0].encode('utf8'), e)

    def getCourseWords(self, courseId=0):
        if courseId == 0:
            courseWords = CourseWord.select()
        else:
            courseWords = CourseWord.select().where(CourseWord.course == courseId)
        return list(courseWords)

    def createCorpusTokens(self):
        token_dict = {}
        for courseWord in self.getCourseWords():
            if token_dict.has_key(courseWord.word):
                token_dict[courseWord.word] += courseWord.count
            else:
                token_dict[courseWord.word] = courseWord.count
                # print courseWord.word, courseWord.count

        sorted_tokens = sorted(token_dict.items(), key=operator.itemgetter(1))
        for token in sorted_tokens:
            print token
            try:
                with db.transaction() as txn:
                    CorpusWord.create(
                        word=token[0],
                        count=token[1],
                        active=True
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for word {}, {}".format(token[0], e)

    def calc_tf(self):
        for course in self.getCourses(55):
            print course.name
            for lecture in self.getLectures(course):
                maxCount = 0
                for lectureWord in self.getLectureWords(lecture):
                    maxCount = max(maxCount, lectureWord.count)

                for lectureWord in self.getLectureWords(lecture):
                    try:
                        with db.transaction():
                            lectureWord.weight = 0.5 + (0.5 * lectureWord.count) / maxCount
                            lectureWord.save()
                    except peewee.OperationalError as e:
                        print e

from nltk import download
if __name__ == '__main__':
    tok = Tokenizer()
    # tok.debug = True

    #Download first time
    #from nltk import download
    #download('punkt')

    print "Extracting all tokens"
    tok.extractAllCourseTokens()

    print "Creating course tokens"
    tok.createCourseTokens()

    # print "Calculating tf weights"
    # tok.calc_tf()

    tok.createCorpusTokens()
