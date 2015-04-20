# -*- coding: utf-8 -*-

import scrapy
from tutorial.items import CoursesItem
from tutorial.items import CoursePageItem
from tutorial.items import PdfItem


class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["courses.cs.ut.ee"]
    start_urls = [
        "https://courses.cs.ut.ee/"
    ]

    def parse(self, response):
        for sel in response.xpath("//ul[@class=\"course-list\"]").xpath(".//li"):
            item = CoursesItem()
            item["title"] = sel.xpath("a/text()").extract()
            item["link"] = sel.xpath("a/@href").extract()
            item["code"] = sel.xpath(".//span/text()").extract()
            yield item
            request = scrapy.Request("https://courses.cs.ut.ee" + ''.join(item['link']), callback=self.parse_navbar)
            request.meta['course'] = item
            yield request

        # filename = response.url.split("/")[-2]
        # with open(filename + ".html", "wb") as f:
        #     f.write(response.body)

    def parse_navbar(self, response):
        for sel in response.xpath("//nav[@class=\"sidebar\"]").xpath(".//li"):
            t_link = ''.join(sel.xpath("a/@href").extract())
            if t_link.find("Lecture") > -1 or t_link.find("Loeng") > -1:
                item = CoursePageItem()
                item["title"] = sel.xpath("a/text()").extract()
                item["link"] = sel.xpath("a/@href").extract()
                # yield item
                request = scrapy.Request(''.join(item['link']), callback=self.parse_lectures)
                request.meta['course'] = response.meta['course']
                yield request

    def parse_lectures(self, response):
        for sel in response.xpath("//a"):
            t_link = ''.join(sel.xpath("@href").extract())
            if t_link.find(".pdf") > -1 and t_link.find("action=upload") == -1:
                item = PdfItem()
                item["title"] = sel.xpath("text()").extract()
                item["link"] = sel.xpath("@href").extract()
                item["path"] = '/' + ''.join(response.url).replace(self.start_urls[0], '')
                course = response.meta['course']
                item['course_code'] = course['code']
                yield item
