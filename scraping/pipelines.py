# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from items import CoursesItem
from items import DataItem
import urllib
from db.DataModel import Course, Lecture, db
import peewee


class CoursePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CoursesItem):
            course_code = ''.join(item['code'])
            try:
                course = Course.get(Course.code == course_code)
            except Course.DoesNotExist:
                print "course record not found, creating"
                try:
                    course_time = item['link'][0].split("/")
                    with db.transaction():
                        Course.create(
                            code=course_code,
                            name=''.join(item['title']),
                            year=course_time[1],
                            semester=''.join(course_time[-1]),
                            url=''.join(item['link']),
                            path='raw_data' + ''.join(item['link'])
                        )
                except peewee.OperationalError as e:
                    print 'Could not create a record for {0}'.format(course_code)

        return item


class DataPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, DataItem):
            url = ''.join(item['link'])
            dirname = 'raw_data' + ''.join(item['path']) + '/'
            course_code = ''.join(item['course_code'])
            content = ''.join(item['content'])
            path = ''
            year = ''.join(item['year'])
            semester = ''.join(item['semester'])

            try:
                course = Course.get(Course.code == course_code)

                #Currenly we gather one semester worth of data for each course.
                #(e.g if we gather data over the span of two years and a course is given
                #every semester, we only take one semester worth of material for that course)
                if course.year != year or course.semester != semester:
                    return item
            except Course.DoesNotExist:
                course = None
                print "Non-existing course: {0}".format(course_code)

            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except OSError as e:
                    print "Could not create directory: " + dirname

            try:
                lecture = Lecture.get(Lecture.course == course, Lecture.url == url)
            except Lecture.DoesNotExist as e:
                lecture = None

            # if no lecture record and no content, then download data (pdf, pptx, etc. according to url
            if lecture is None and len(content) == 0:
                filename = os.path.basename(url)
                path = dirname + filename
                print "Saving {0} => {1}".format(url, path)
                try:
                    urllib.urlretrieve(url, path)
                except IOError as e:
                    print "Could not save file: {1} into {2}".format(url, path)

            if lecture is None:
                print "Lecture record not found, creating ..."
                try:
                    title = path.split("/")[-1]
                    with db.transaction():
                        Lecture.create(
                            course=course,
                            url=url,
                            path=path,
                            name=title,
                            content=content
                        )
                except peewee.OperationalError as e:
                    print "Could not create a record for course {0} lecture {1}".format(course_code, url)
            else:
                if len(content) > 0:
                    try:
                        with db.transaction():
                            lecture.content = content
                            lecture.save()
                    except peewee.OperationalError as e:
                        print e
        return item
