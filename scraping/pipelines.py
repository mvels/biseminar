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
            course_time = item['link'][0].split("/")
            year = course_time[1]
            semester = ''.join(course_time[-1])

            #Check if entry already exists
            course = Course.select().where(Course.code == course_code, Course.year == year, Course.semester == semester)

            if not course.exists():
                print "course record not found, creating"
                try:
                    with db.transaction():
                        Course.create(
                            code=course_code,
                            name=''.join(item['title']),
                            year=year,
                            semester=semester,
                            url=''.join(item['link']),
                            path='raw_data'.join(item['link'])
                        )
                except peewee.OperationalError as e:
                    print "Could not create a record for {} due to {}".format(course_code, e)

        return item


class DataPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, DataItem):
            url = ''.join(item['link'])
            dir_name = 'raw_data' + ''.join(item['path']) + '/'
            course_code = ''.join(item['course_code'])
            content = ''.join(item['content'])
            path = ''
            year = ''.join(item['year'])
            semester = ''.join(item['semester'])

            course = Course.select().where(Course.code == course_code, Course.year == year, Course.semester == semester)
            if not course.exists():
                course = None
                print "Non-existing course: {}".format(course_code)

            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name)
                except OSError as e:
                    print "Could not create directory: {} due to {}".format(dir_name, e)

            lecture = Lecture.select().where(Lecture.course == course, Lecture.url == url)
            # if no lecture record and no content, then download data (pdf, pptx, etc.) according to url
            if not lecture.exists() and len(content) == 0:
                filename = os.path.basename(url)
                path = dir_name + filename
                print "Saving {} => {}".format(url, path)
                try:
                    urllib.urlretrieve(url, path)
                except IOError as e:
                    print "Could not save file: {} into {}. Cause {}".format(url, path, e)

            if not lecture.exists():
                print "Lecture record not found, creating ..."
                try:
                    title = self.__get_title(url)
                    with db.transaction():
                        Lecture.create(
                            course=course,
                            url=url,
                            path=path,
                            name=title,
                            content=content
                        )
                except peewee.OperationalError as e:
                    print "Could not create a record for course {} lecture {} due to {}".format(course_code, url, e)
            else:
                if len(content) > 0:
                    try:
                        with db.transaction():
                            lecture.content = content
                            lecture.save()
                    except peewee.OperationalError as e:
                        print e
        return item

    @staticmethod
    def __get_title(url):
        title = url.split("/")
        if url.find(".pdf") > -1 or url.find(".pptx") > -1:
            return title[-1]
        else:
            return "Web content - " + str(title[-1])