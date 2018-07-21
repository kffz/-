# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
import psycopg2.extras
import time

class JdgoodsPipeline(object):
    def __init__(self):
        self.conn=psycopg2.connect(host="localhost",user="postgres",port=5432,password="676794",database="jd")
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        drop_table = "drop table if exists jd_cpu_20180505"
        cursor.execute(drop_table)
        create_table = """create table jd_cpu_20180505
        (uid varchar(100) not null,
        title varchar(1000) not null,
        price varchar(1000) not null,
        url varchar(1000) not null,
        store varchar(1000),
        commentcount varchar(100),
        date varchar(1000),
        primary key(uid));"""
        cursor.execute(create_table)
    
    def process_item(self, item, spider):
        
        try:
            title = str(item['title'])
            price = str(item['price'])
            url=item['url']
            store = item['store']
            commentcount = item['commentcount']
            uid = item['uid']
            date = time.strftime("%Y-%m-%d",time.localtime())
            #print(url)
            #print(title)
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            insert_exe = "insert into jd_cpu_20180505(uid,title,price,url,store,commentcount,date) values('%s','%s','%s','%s','%s','%s','%s');"%(uid,title,price,url,store,commentcount,date)
            cursor.execute(insert_exe)
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            #print(err)
    
    def close_spider(self,spider):
        self.conn.close()
