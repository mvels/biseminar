from tutorial.DataModel import Lecture, db
import peewee
from bs4 import BeautifulSoup

class Html2Txt(object):
    def __init__(self):
        pass

def main():
    lectures = Lecture.select().where(Lecture.content <> '', Lecture.path == "").limit(1000)
    for lecture in lectures:
        soup = BeautifulSoup(lecture.content)
        print lecture.url
        lecture.content = soup.get_text()
        lecture.path = 'html2txt'
        try:
            with db.transaction():
                lecture.save()
        except peewee.OperationalError as e:
            print e

if __name__ == '__main__':
    main()
