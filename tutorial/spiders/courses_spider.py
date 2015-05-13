# -*- coding: utf-8 -*-

import scrapy
from tutorial.items import CoursesItem
from tutorial.items import CoursePageItem
from tutorial.items import DataItem


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
            # only follow links in navbar that are inside allowed domain
            if t_link.find(self.start_urls[0]) > -1:
                item = CoursePageItem()
                item["title"] = sel.xpath("a/text()").extract()
                item["link"] = sel.xpath("a/@href").extract()
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
            if (t_link.find(".pdf") > -1 or t_link.find(".pptx") > -1) and \
                t_link.find("action=upload") == -1:
                item = DataItem()
                item['title'] = sel.xpath("text()").extract()
                item['link'] = sel.xpath("@href").extract()
                item['path'] = '/' + ''.join(response.url).replace(self.start_urls[0], '')
                course = response.meta['course']
                item['course_code'] = course['code']
                item['content'] = ''
                yield item
