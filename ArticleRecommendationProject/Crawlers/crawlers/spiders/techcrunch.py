# -*- coding: utf-8 -*-
import os

from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime

from scrapy.selector import Selector

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

# This is our Base class from which we're extending
from common import CommonBaseSpider

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


class TechCrunchSpider(CommonBaseSpider):
	name = "techcrunch"
	base_dir = "crawl"
	allowed_domains = ["techcrunch.com"]
	start_urls = (
					"http://techcrunch.com/",
					"http://techcrunch.com/startups/",
					"http://techcrunch.com/mobile/",
					"http://techcrunch.com/gadgets/",
					"http://techcrunch.com/enterprise/",
					"http://techcrunch.com/social/",
					"http://techcrunch.com/europe/",
					"http://techcrunch.com/asia/",
					"http://techcrunch.com/crunch-network/",
					"http://techcrunch.com/unicorn-leaderboard/",
					"http://techcrunch.com/video/apps/",
					"http://techcrunch.com/video/tctv-news/",
					"http://techcrunch.com/video/bullish/",
					"http://techcrunch.com/video/crunchreport/",
					"http://techcrunch.com/events/disrupt-ny-2016/video/",
					"http://techcrunch.com/video/gadgets/",
					"http://techcrunch.com/event-type/disrupt/",
					"http://techcrunch.com/startup-battlefield/",

	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'https\:\/\/techcrunch\.com\/.+',)),
			callback='parse_item',
			follow=False),
	)

	def parse_item(self, response):
		super(TechCrunchSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@class,\'alpha tweet-title\')]//text()")
			details = tree.xpath('.//div[contains(@class,\'article-entry text\')]//p//text()')
			if title and details:
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ det.strip().encode('ascii','ignore') for det in details])
				
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]

				img_urls = tree.xpath('.//div[contains(@class,\'article-entry text\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = img_urls


				cover_image = tree.xpath('.//div[contains(@class,\'article-entry text\')]/img/@src')
				if cover_image:
					news_item['cover_image'] = cover_image[0]

				author = tree.xpath('/html/body/div[4]/article/div/div[1]/div/header/div[2]/div[1]/a/text()')
				if author :
					news_item['author'] = author


				return news_item

		except:
			pass
		return None


