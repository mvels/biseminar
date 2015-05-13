# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CoursesItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    code = scrapy.Field()

class CoursePageItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

class DataItem(scrapy.Item):
    type = scrapy.Field()
    course_code = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    path = scrapy.Field()
    content = scrapy.Field()

