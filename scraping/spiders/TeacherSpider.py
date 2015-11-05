# -*- coding: utf-8 -*-
import scrapy
from scraping.items import TeacherItem


class TeacherSpider(scrapy.Spider):
    name = "teacher"
    allowed_domains = ["www.cs.ut.ee"]
    start_urls = [
        "http://www.cs.ut.ee/et/instituut/tootajad"
    ]

    def parse(self, response):
        for name in response.xpath("//table").xpath(".//tr").xpath("td[1]").xpath('text()').extract():
            item = TeacherItem()
            item['name'] = name.strip()
            yield item