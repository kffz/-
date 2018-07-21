# -*- coding: utf-8 -*-
import scrapy
from jdgoods.items import JdgoodsItem
import re
import urllib


class JdgoodSpider(scrapy.Spider):
    name = 'jdgood'
    allowed_domains = ['jd.com']
    key=['CPU']
    start_urls = ['https://search.jd.com/Search?keyword='+key[0]+'&enc=utf-8']
    
    def parse(self,response):
        
        for i in range(len(self.key)):
            for ipage in range(1):
                url='https://search.jd.com/Search?keyword='+self.key[i]+'&enc=utf-8'+'&page='+str(ipage)
                yield scrapy.Request(url,callback=self.searchpage)

    def searchpage(self, response):
        #goodid=[]
        #search_url = response.url
        #print(search_url)
        item_url = 'https://item.jd.com/'
        for each in response.xpath("//li[@class='gl-item']"):
            #print(each)
            try:
                idnum = each.xpath("./@data-sku").extract()[0]
                #print(id)
                yield scrapy.Request(item_url+idnum+'.html',self.page)
            except:
                continue
        #print(goodid)
    
    def page(self,response):
        item = JdgoodsItem()
        title = response.xpath("//div[@class='sku-name']/text()").extract()[0]
        page_url = response.url
        item['url'] = page_url
        item['title'] = title
        pattern_price = r'https://item.jd.com/(.*?).html'
        idnum = re.findall(pattern_price,page_url)[0]
        item['uid'] = idnum
        try:
            name = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li/a//text()').extract()[0]
        except:
            try:
                name = response.xpath('//div[@class="name"]/a//text()').extract()[0].strip()
            except:
                try:
                    name = response.xpath('//div[@class="shopName"]/strong/span/a//text()').extract()[0].strip()
                except:
                    try:
                        name = response.xpath('//div[@class="seller-infor"]/a//text()').extract()[0].strip()
                    except:
                        name = ''
        item['store'] = name
        commentcount_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds='+idnum
        comment_response = urllib.request.urlopen(commentcount_url)
        #print(comment_response.info())
        commentcount_content = comment_response.read().decode('gbk')
        try:
            pattern_comment = r'"CommentCountStr":"(.*?)"'
            commentcount = re.findall(pattern_comment,commentcount_content)[0]
        except:
            try:
                pattern_comment=r'"CommentCount":(.*?)'
                commentcount = re.findall(pattern_comment,commentcount_content)[0]
            except:
                commentcount = '0'
        item['commentcount'] = commentcount
        #print(title,price,name,commentcount)
        
    #print(page_url)
        try:
            price_url = 'https://p.3.cn/prices/mgets?skuIds=J_'+idnum
            price_response = urllib.request.urlopen(price_url)
            price_content = price_response.read().decode('gbk')
            #print(type(price_content))
            #print(price_content)
            #print(type(price_response.read()))
            pattern_2 = r'"p":"(.*?)"'
            price = re.findall(pattern_2,price_content)[0]
            item['price'] = price
        except Exception as e:
            item['price'] = 'none'
            phone_url = 'https://item.m.jd.com/product/'+idnum+'.html'
            phone_response = urllib.request.urlopen(phone_url)
            phone_content = phone_response.read().decode('utf-8','ignore')
            #print(phone_content)
            phone_pattern = r"skuPrice:'(.*?)'"
            price = re.findall(phone_pattern,phone_content)[0]
        item['price'] = price
        #print(price)
        yield item
            
            #print(phone_response.info())
            #print(e)
        
   
             