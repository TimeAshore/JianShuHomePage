# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JianshuItem(scrapy.Item):
    auther = scrapy.Field()
    article_name = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()

