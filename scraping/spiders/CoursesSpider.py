# -*- coding: utf-8 -*-

import scrapy
from scraping.items import CoursesItem
from scraping.items import CoursePageItem
from scraping.items import DataItem


class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["courses.cs.ut.ee"]
    start_urls = [
        "https://courses.cs.ut.ee/courses/old"
    ]

    filter_url = "https://courses.cs.ut.ee"
    allowed_semesters = [("2015", "spring"), ("2014", "fall"), ("2014", "spring"), ("2013", "fall")]

    def parse(self, response):
        for sel in response.xpath("//table[@class=\"table previous-years\"]/tr"):
            for it in sel.xpath(".//a"):
                link = it.xpath("@href").extract()[0]

                # Choose only wanted semesters
                if any([x in link and y in link for x, y in self.allowed_semesters]):
                    request = scrapy.Request(self.filter_url + ''.join(link), callback=self.parse_courses)
                    yield request

    def parse_courses(self, response):
        for sel in response.xpath("//ul[@class=\"course-list\"]").xpath(".//li"):
            item = CoursesItem()
            item["title"] = sel.xpath("a/text()").extract()
            item["link"] = sel.xpath("a/@href").extract()
            item["code"] = sel.xpath(".//span/text()").extract()
            yield item
            request = scrapy.Request(self.filter_url + ''.join(item['link']), callback=self.parse_navbar)
            request.meta['course'] = item
            yield request

    def parse_navbar(self, response):
        for sel in response.xpath("//nav[@class=\"sidebar\"]").xpath(".//a"):
            t_link = ''.join(sel.xpath("@href").extract())
            # only follow links in navbar that are inside allowed domain
            if t_link.find(self.filter_url) > -1:
                item = CoursePageItem()
                item["title"] = sel.xpath("text()").extract()
                item["link"] = sel.xpath("@href").extract()
                # yield item
                request = scrapy.Request(''.join(item['link']), callback=self.parse_article)
                request.meta['course'] = response.meta['course']
                yield request

    def parse_article(self, response):
        try:
            for sel in response.xpath("//article[@class=\"content\"]"):
                item = DataItem()
                item['link'] = response.url
                item['path'] = ''
                item['content'] = sel.extract()
                course = response.meta['course']
                item['course_code'] = course['code']
                yield item
        except AttributeError as e:
            pass

        for sel in response.xpath("//a"):
            t_link = ''.join(sel.xpath("@href").extract())
            if self.is_valid_url(t_link):
                item = DataItem()
                item['title'] = sel.xpath("text()").extract()
                item['link'] = sel.xpath("@href").extract()
                item['path'] = '/' + ''.join(response.url).replace(self.filter_url, '')
                course = response.meta['course']
                item['course_code'] = course['code']
                item['content'] = ''
                yield item

    def is_valid_url(self, url):
        return (url.find(".pdf") > -1 or url.find(".pptx") > -1) and \
               url.find("action=upload") == -1
