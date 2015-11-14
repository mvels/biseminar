import peewee, os

DB_DIR = os.path.dirname(os.path.dirname(__file__)) + "/db/"
dbname = DB_DIR + 'courses.sqlite'
db = peewee.SqliteDatabase(dbname)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Course(BaseModel):
    name = peewee.CharField()
    code = peewee.CharField()
    year = peewee.CharField()
    semester = peewee.CharField()
    url = peewee.CharField()
    path = peewee.CharField()


class Lecture(BaseModel):
    course = peewee.ForeignKeyField(Course)
    url = peewee.CharField()
    path = peewee.CharField()
    content = peewee.TextField()


class LectureWord(BaseModel):
    lecture = peewee.ForeignKeyField(Lecture)
    word = peewee.CharField()
    count = peewee.IntegerField()
    active = peewee.BooleanField()
    weight = peewee.DoubleField()


class CourseWord(BaseModel):
    course = peewee.ForeignKeyField(Course)
    word = peewee.CharField()
    count = peewee.IntegerField()
    active = peewee.BooleanField()
    lectures = peewee.IntegerField()


class CorpusWord(BaseModel):
    word = peewee.CharField()
    count = peewee.IntegerField()
    active = peewee.BooleanField()


class TopicWord(BaseModel):
    topic = peewee.IntegerField()
    word = peewee.CharField()
    weight = peewee.DoubleField()


class CourseTopic(BaseModel):
    course = peewee.ForeignKeyField(Course)
    topic = peewee.IntegerField()
    weight = peewee.DoubleField()


class LDALogLikelihood(BaseModel):
    iteration = peewee.IntegerField()
    loglikelihood = peewee.DoubleField()


class LectureTopic(BaseModel):
    lecture = peewee.ForeignKeyField(Lecture)
    topic = peewee.IntegerField()
    weight = peewee.DoubleField()


class LectureTopicWord(BaseModel):
    topic = peewee.IntegerField()
    word = peewee.CharField()
    weight = peewee.DoubleField()


if __name__ == '__main__':
    db.create_tables([Course, Lecture, CourseWord, LectureWord, CorpusWord, TopicWord, CourseTopic, LDALogLikelihood,
                      LectureTopic, LectureTopicWord], safe=True)
