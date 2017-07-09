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
from common import CommonBaseSpider, get_stripped_list

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
		"Industries": ["http://www.moneycontrol.com/news/business/",],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": [ "http://www.moneycontrol.com/sme/",
		"http://www.moneycontrol.com/news/sme-301.html",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Deals": [],
		"Stocks": [],
		"Economics": [],
		"Markets": ["http://www.moneycontrol.com/stocksmarketsindia/"],
		"Product Launch" : [],
		"Investment" : [],
		"Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Opinion" : [],
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": [ ],
		"Deadpool": [],
		"Misc": [],
		"Ecommerce": []
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
		"Policy": [],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]

class MoneycontrolSpider(CommonBaseSpider):
	name = "moneycontrol"
	base_dir = "crawl"
	allowed_domains = ["moneycontrol.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(SgmlLinkExtractor(
			allow=(r'http\:\/\/www\.moneycontrol\.com\/news\/(business|economy|sme|technology|current-affairs|world-news|)\/(.*)',)),
			callback='parse_item',
			follow=True	),
	)

	def parse_item(self, response):
		super(MoneycontrolSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath('.//h1[contains(@class, "arti_title")]/text()')
			details = tree.xpath('.//div[contains(@class, "MT20")]//p//text()[not(ancestor::script)]')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] ='\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])

				img_urls = tree.xpath('.//table[contains(@class,"MR15")]//div/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				tags = tree.xpath('.//div[contains(@class, "tag_wrap MT20")]/a//text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

				published_date = tree.xpath('.//p[contains(@class, "arttidate MT15")]//text()')

				if published_date:
					if '|' in published_date[0]:
						news_item['published_date'] = datetime.strptime(published_date[0].split('|')[0].strip().encode('ascii','ignore'), '%b %d, %Y, %I.%M %p')
					else:
						news_item['published_date'] = datetime.strptime(published_date[0].strip().encode('ascii','ignore'), '%b %d, %Y, %I.%M %p')

				referer = response.request.headers['Referer']
				for item in categories:
					if referer in sum(item['subcategory'].values(), []):
						news_item['category'] = item['category']
						key = (key for key,value in item['subcategory'].items() if referer in value).next()
						news_item['sub_categories'] = [key]
				return news_item

		except Exception, e:
			self.log('==Exception=================>>>>>>>>! %r' % e)
		return None


