# -*- coding: utf-8 -*-
import os

from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

# This is our Base class from which we're extending
from common import CommonBaseSpider

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


class SmallBizTrendsSpider(CommonBaseSpider):
    name = "smallbiztrends"
    base_dir = "crawl"
    allowed_domains = ["smallbiztrends.com"]
    start_urls = (
                    "http://smallbiztrends.com/",
                    'http://smallbiztrends.com/category/social-media',
                    'http://smallbiztrends.com/category/retail-trends',
                    'http://smallbiztrends.com/category/small-business-sale',
                    'http://smallbiztrends.com/category/marketing-tips',
                    'http://smallbiztrends.com/category/local-search-2',
                    ##Management 
                    'http://smallbiztrends.com/category/management',
                    'http://smallbiztrends.com/category/employment-trends',
                    'http://smallbiztrends.com/category/business-book-reviews',
                    'http://smallbiztrends.com/category/top-books',
                    'http://smallbiztrends.com/category/humor',
                    'http://smallbiztrends.com/category/small-business-operations',
                    ##Technology 
                    'http://smallbiztrends.com/category/product-lists',
                    'http://smallbiztrends.com/category/technology-trends',
                    'http://smallbiztrends.com/category/product-reviews',
                    ## Finance 
                    'http://smallbiztrends.com/category/economic-trends',
                    'http://smallbiztrends.com/category/small-business-taxes',
                    'http://smallbiztrends.com/category/smb-venture-angel-capital',
                    'http://smallbiztrends.com/category/small-business-loan',
                    'http://smallbiztrends.com/category/financial-management-section',
                    ## Advice 
                    'http://smallbiztrends.com/category/startup-trends',
                    'http://smallbiztrends.com/category/franchise-trends',
                    'http://smallbiztrends.com/category/handmade-business',
                    'http://smallbiztrends.com/category/green-business',
                    'http://smallbiztrends.com/category/interviews-2',
                    'http://smallbiztrends.com/category/research',
                    'http://smallbiztrends.com/small-business-resource-center',
                    'http://smallbiztrends.com/#',
                    'http://smallbiztrends.com/#',
                    'http://smallbiztrends.com/category/templates-2',
                    'http://smallbiztrends.com/#',
                    'http://smallbiztrends.com/small-business-resource-center',
                    ## More 
                    'http://smallbiztrends.com/category/small-business-news',
                    'htp://smallbiztrends.com/category/small-business-news',
                    'http://smallbiztrends.com/events',
                    'http://smallbiztrends.com/category/small-business-events',
                    'http://sellingtosmallbusinesses.com/',
                    'http://smallbiztrends.com/category/press-release',
                    'http://smallbiztrends.tradepub.com/',
                    ##  –And More 
                    'http://smallbiztrends.com/category/daily-tips',
                    'http://smallbiztrends.com/business-cartoons',
                    'http://smallbiztrends.com/infographics',
                    'http://smallbiztrends.com/about',
                    'http://smallbiztrends.com/about',
                    'http://smallbiztrends.com/category/announcements',
                    'http://smallbiztrends.com/newsletter-archive',
                    'http://smallbiztrends.com/contact',
                    'http://smallbiztrends.com/advertise',
                    'http://smallbiztrends.com/advertise',
                    'http://smallbiztrends.com/small-business-spotlight',
                    )
    rules = (
        Rule(SgmlLinkExtractor(
            allow=(r'http\:\/\/smallbiztrends\.com\/\d{4}\/\d{2}\/(.+|)'),),
            callback='parse_item', follow=True),
    )
    def parse_item(self, response):
        super(SmallBizTrendsSpider, self).parse_item(response)
        htmlparser = etree.HTMLParser()
        tree = etree.parse(BytesIO(response.body), htmlparser)

        news_item = NewsItem()
        try:
            title = tree.xpath(".//div[@class='post-inner']/h1/text()")
            details = tree.xpath('.//div[@class=\"entry\"]/p/text()')
            if title and details:
                news_item['source'] = self.name
                news_item['crawled_date'] = datetime.now()
                news_item['source_url'] = response.url.split('?')[0]
                news_item['title'] = title[0].strip().decode('unicode_escape').encode('ascii','ignore')
                news_item['details'] = '\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])
                # ' '.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])

                if tree.xpath('.//span[@class=\'full-span-featured-image\']/span/img/@src'):
                    news_item['img_urls'] = tree.xpath('.//span[@class=\'full-span-featured-image\']/span/img/@src')
                elif tree.xpath('.//img[contains(@class,\'size-full\')]/@src'):
                    news_item['img_urls'] = tree.xpath('.//img[contains(@class,\'size-full\')]/@src')
                elif tree.xpath('.//img[contains(@class,\'aligncenter\')]/@src'):
                    news_item['img_urls'] = tree.xpath('.//img[contains(@class,\'aligncenter\')]/@src')

                meta_result = self.get_meta(tree)

                if 'description' in meta_result:
                    news_item['blurb'] = meta_result['description']

                published_date = tree.xpath('.//span[contains(@class,\'article-date\')]/text()')
                if published_date:
                    news_item['published_date'] = datetime.strptime(published_date[0], '%b %d, %Y')
                author = tree.xpath('.//span[contains(@itemprop,\'name\')]/a/text()')
                if author:
                    news_item['author'] = author
                return news_item

        except:
            pass
        return None
