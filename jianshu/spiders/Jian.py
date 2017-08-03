# -*- coding: utf-8 -*-
import scrapy
import re
import MySQLdb
import json
import codecs
from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor as sle
from scrapy.http import Request,FormRequest
from jianshu.items import JianshuItem
import sys
import random
import time
import string
import logging
import requests
import os

reload(sys)
sys.setdefaultencoding('utf-8')


class JianSpider(scrapy.Spider):
    name = "Jian"
    allowed_domains = ["jianshu.com"]
    start_urls = ['http://www.jianshu.com']
    ids = []
    ans = 2
    header = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Cookie": "_session_id=ako3cU1zUlZXR1EyWGlVbUlBSXFwanZLaUgvMnZMOTBhemp2bktDbHZjVTNxbVR5ZTBRTmgvbWZqaWNCdVg5bER5bUIzWjNMbTJDSndVTzRTbWdLRjhoOUQ4ZDhzdFFzMTF1czBvdUtuSnRqR215ZGp0elRTMitCTEtqcTdPaDFvVE9HUmtsRG1LRFRmN1NiYVU3QU1FVjZxc3JwU0poRGltODNHa2ZicVVPMTBNMFdHQUFyNVhOU3p5VFVZRWlwWDVtMmg4a0lVVnp6bllNMXpqQjdTdGhkaHFkM3JKVHR4VlZYOGhrNkQrbVg5OXRJNE1rdGZzZ0VqNnlLTUZlVmJxQThha0J4RDFaNkVId0ZDY0xPeWNzYVdGbXFTZHY0dEk0MUxSVXlkUDUrRmRLS3dqSzBDOGcvbllsZEJ2ckh4SlJ6R1lRL2IrVFp0bTEyN25VY2ZVa2tqZ3hxejcrWFdvNG9ZMTh0THpaTCs4NVZad01MNmJpRzJnaCt5OFlFK3FIcmJNM3ZYNFRFQnliZTBNenhXTThDajMweTd6QUFDU1Rma0tTR2ZFVT0tLVoyTzhkMlBvVG80Mmh1V3hPRDZHNHc9PQ%3D%3D--e5f346d782d2bdc52270c1c7229857a03dc1a747",
        "Host": "www.jianshu.com",
        "Referer": "http://www.jianshu.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "X-CSRF-Token": "wVHm0G4esacdPLWER5AIQCDCDNAD9LLMkfB9Zd7ZrTQcNri0U+mdKPLzVAZPtPM97oc6Jq74z3FG5tup3qpZPQ==",
        "X-INFINITESCROLL": "true",
        "X-Requested-With": "XMLHttpRequest"
    }


    def parse(self, response):
        sel = Selector(response)
        lis = sel.xpath('/html/body/div[1]/div/div[2]/div[3]/ul/li')
        for x in lis:
            data_id = x.xpath('@data-note-id').extract()[0]
            self.ids.append(data_id)
            p_id = x.xpath('div/a').xpath('@href').extract()[0]
            yield Request('http://www.jianshu.com'+p_id,meta={"p_id":p_id},callback=self.parse_item)

        sum1 = '&seen_snote_ids[]='.join(self.ids)
        url = 'http://www.jianshu.com/?seen_snote_ids[]='+sum1+'&page='+str(2)
        # print url
        yield Request(url,meta={'url':url},headers=self.header,callback=self.page_two)



    def page_two(self,response):
        last_url = response.meta['url']
        new_url = re.sub('&page=\d',"",last_url)
        self.ans += 1

        sel = Selector(response)
        lis = sel.xpath('//li')
        id = []
        for x in lis:
            data_id = x.xpath('@data-note-id').extract()[0]
            # print data_id
            new_url = new_url + '&seen_snote_ids[]=' + str(data_id)
            p_id = x.xpath('div/a').xpath('@href').extract()[0]
            yield Request('http://www.jianshu.com' + p_id, meta={"p_id": p_id}, callback=self.parse_item)
        new_url = new_url + '&page=' + str(self.ans)
        print 'new_urll:', new_url
        yield Request(new_url, meta={'url': new_url}, headers=self.header, callback=self.page_two)
        if self.ans >= 15:
            sys.exit()


    #爬每篇文章内容
    def parse_item(self,response):
        sele = Selector(response)
        item = JianshuItem()
        try:
            item['auther'] = sele.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/div/span[2]/a/text()').extract()[0]
        except:
            item['auther'] = ""
        try:
            item['article_name'] = sele.xpath('/html/body/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        except:
            item['article_name'] = ""
        content = sele.xpath('/html/body/div[1]/div[1]/div[1]/div[2]').extract()[0]
        content = re.sub('</\w*>', '\n', content)
        content = re.sub('<[^>]+>','',content)
        content.replace("图片发自简书App","")
        content.replace("\n","")
        item['content'] = content
        item['link'] = 'http://www.jianshu.com'+ response.meta['p_id']
        return  item



