import peewee
from DataModel import db, Course, Lecture

# try:
#     with db.transaction():
#         Course.create(
#             code = 'testcode',
#             name = 'testname',
#             url = 'http://',
#             path = './asdad/'
#         )
# except peewee.OperationalError as e:
#     print e

# courseQuery = Course.select()
# for course in courseQuery:
#     print course.code, course.name

# try:
#     course = Course.get(Course.code == 'testcode')
#     print 'course exists'
# except Course.DoesNotExist:
#     print 'no such course'


