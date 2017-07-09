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
from common import CommonBaseSpider, get_stripped_list

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem

categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
		"Industries": ["http://www.smeweb.com/export",],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.smeweb.com/sme",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Deals": [],
		"Stocks": [],
		"Economics": [],
		"Markets": ["http://www.smeweb.com/business-events",
		"http://www.smeweb.com/mid-market",],
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
		"Technology": ["http://www.smeweb.com/innovation",],
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

class SmeWebSpider(CommonBaseSpider):
	name = "smeweb"
	base_dir = "crawl"
	allowed_domains = ["smeweb.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/www\.smeweb\.com\/.+')),
			callback='parse_item',
			follow=False),
	)

	def parse_item(self, response):
		super(SmeWebSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@itemprop,\"name\")]/text()")
			details = tree.xpath('.//div[@class="article__body"]/p//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([x.strip().encode('ascii','ignore')for x in details]).strip()
				
				news_item['source_url'] = response.url.split('?')[0]

				img_urls = tree.xpath('.//a[contains(@class,\"article__figure__link\")]/img/@src')

				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				published_date = tree.xpath('.//span[contains(@class,\"article__meta__info\")]/time/text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[0].strip().encode('ascii','ignore'), '%B %d %Y %I:%M %p')

				author = tree.xpath('.//span[contains(@class,\"article__meta__value\")]/text()')
				if author:
					author = author[0].strip()
					news_item['author'] = author.split('\n')[1].strip() if '\n' in author else author

				tags = tree.xpath('.//div[contains(@class,\"article__tags-container\")]/a/span/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

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



