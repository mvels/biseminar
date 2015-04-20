# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DmozItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

class AppspotItems(scrapy.Item):
    topic = scrapy.Field()
    author = scrapy.Field()
    id = scrapy.Field()
    last_post = scrapy.Field()

class CoursesItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    code = scrapy.Field()

class CoursePageItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

class PdfItem(scrapy.Item):
    course_code = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    path = scrapy.Field()

