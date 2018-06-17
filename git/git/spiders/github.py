# -*- coding: utf-8 -*-
import scrapy
import logging
from scrapy.http import Request,FormRequest,HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
import sys
import re

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(sys.stdout)])

class GithubSpider(CrawlSpider):
    name = 'github'
    allowed_domains = ['github.com']
    start_urls = ['http://github.com/issues']
    rules = (
        Rule(LinkExtractor(allow=('/issues/\d+',),
                           restrict_xpaths='//ul[starts-with(@class,"table-list")]/li/div[2]/a[2]'),
             callback='parse_page'),
        Rule(LinkExtractor(restrict_xpaths='//a[@class="next_page"]')),
    )
    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
        "Referer": "https://github.com/",
    }


    def start_requests(self):
        return [Request("https://github.com/login",meta={'cookiejar':1},callback =self.post_login)]



    def post_login(self,response):
        print('Login Prepared')
        authenticity_token = response.xpath('//input[@name="authenticity_token"]/@value').extract_first()
        logging.info('authenticity_token='+authenticity_token)
        return [FormRequest.from_response(response,url='https://github.com/session',\
                                                 meta={'cookiejar':response.meta['cookiejar']},\
                                                 headers = self.post_headers,
                                                 formdata={
                                                     'utf8':'✓',
                                                     'login':'***********',
                                                     'password':'***********',
                                                     'authenticity_token':authenticity_token
                                                 },
                                                 callback=self.after_login,
                                                 dont_filter=True)]
    def after_login(self,response):
        for url in self.start_urls:
            yield Request(url,meta={'cookiejar':response.meta['cookiejar']})
        print('Login Completed')

    def parse_page(self,response):
        logging.info('--------------------消息分割线----------------')
        logging.info(response.url)
        issue_title = response.xpath('//span[@class="js-issue-title"]/text()').extract_first()
        logging.info('issue_title:'+issue_title)

    def _requests_to_follow(self, response):
        if not isinstance(response,HtmlResponse):
            return
        seen = set()
        for n,rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links=rule.process_links(links)
            for link in links:
                seen.add(link)
                r = Request(url=link.url,callback=self._response_downloaded)
                r.meta.update(rule=n,link_text=link.text,cookiejar = response.meta['cookiejar'])
                yield rule.process_request(r)