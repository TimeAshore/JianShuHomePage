# -*- coding: utf-8 -*-
import MySQLdb
from scrapy import log
from twisted.enterprise import adbapi
from scrapy.http import Request
from scrapy.exceptions import DropItem
import time
import MySQLdb.cursors
import socket
import select
import sys
import os
import errno
import codecs
import json
from scrapy.exceptions import DropItem
#去重
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item


class MySQLStorePipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            db='JianShu',
                                            user='root',
                                            passwd='123456',
                                            cursorclass=MySQLdb.cursors.DictCursor,
                                            charset='utf8',
                                            use_unicode=True
                                            )
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self, tx, item):
        try:
            tx.execute('insert into Home_articles values(%s,%s,%s,%s)',(
                item['article_name'],item['auther'],item['content'],item['link']
                     ))
            print u"写入成功"
        except:
            print u"写入失败"

#写入json文件
class JsonPipeline(object):

    def __init__(self):
        self.file = codecs.open('clo.json', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        try:
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.file.write(line)
            print 'success'
            return item
        except:
            print 'failed'
            pass

    def spider_closed(self, spider):
        self.file.close()
