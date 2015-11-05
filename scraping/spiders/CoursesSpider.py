# -*- coding: utf-8 -*-

import scrapy
from scraping.items import CoursesItem
from scraping.items import CoursePageItem
from scraping.items import DataItem


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

    def parse_navbar(self, response):
        for sel in response.xpath("//nav[@class=\"sidebar\"]").xpath(".//a"):
            t_link = ''.join(sel.xpath("@href").extract())
            # only follow links in navbar that are inside allowed domain
            if t_link.find(self.start_urls[0]) > -1:
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
                item['path'] = '/' + ''.join(response.url).replace(self.start_urls[0], '')
                course = response.meta['course']
                item['course_code'] = course['code']
                item['content'] = ''
                yield item

    def is_valid_url(self, url):
        return (url.find(".pdf") > -1 or url.find(".pptx") > -1) and \
               url.find("action=upload") == -1
