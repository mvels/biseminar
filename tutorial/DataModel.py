import peewee

dbname = 'courses.sqlite'
db = peewee.SqliteDatabase(dbname)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Course(BaseModel):
    name = peewee.CharField()
    code = peewee.CharField()
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

db.create_tables([Course, Lecture, CourseWord, LectureWord, CorpusWord], safe=True)
