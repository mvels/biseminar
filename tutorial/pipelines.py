# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from items import CoursesItem
from items import PdfItem
import urllib
from DataModel import Course, Lecture, db
import peewee

class CoursePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CoursesItem):
            dirname = 'pdf' + ''.join(item['link'])
            course_code = ''.join(item['code'])
            try:
                course = Course.get(Course.code == course_code)
            except Course.DoesNotExist:
                print "course record not found, creating"
                try:
                    with db.transaction():
                        Course.create(
                            code = course_code,
                            name = ''.join(item['title']),
                            url = ''.join(item['link']),
                            path = dirname
                        )
                except peewee.OperationalError as e:
                    print 'Could not create a record for {0}'.format(course_code)

                if not os.path.exists(dirname):
                    try:
                        os.makedirs(dirname)
                    except OSError as e:
                        print "Could not create directory: " + dirname

        return item

class PdfPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, PdfItem):
            url = ''.join(item['link'])
            dirname = 'pdf' + ''.join(item['path']) + '/'
            course_code = ''.join(item['course_code'])

            try:
                course = Course.get(Course.code == course_code)
            except Course.DoesNotExist:
                course = None
                print "Non-existing course: {0}".format(course_code)

            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except OSError as e:
                    print "Could not create directory: " + dirname

            filename = os.path.basename(url)
            path = dirname + filename
            print "Saving {0} => {1}".format(url, path)
            try:
                urllib.urlretrieve(url, path)
                try:
                    lecture = Lecture.get(Lecture.course == course, Lecture.url == url)
                except Lecture.DoesNotExist as e:
                    print "Lecture record not found, creating ..."
                    try:
                        with db.transaction():
                            Lecture.create(
                                course = course,
                                url = url,
                                path = path,
                                content = ''
                            )
                    except peewee.OperationalError as e:
                        print "Could not create a record for course {0} lecture {1}".format(course_code, url)

            except IOError as e:
                print "Could not save file: {1} into {2}".format(url, path)
        return item
