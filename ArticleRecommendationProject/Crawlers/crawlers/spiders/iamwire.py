# -*- coding: utf-8 -*-
import os

from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from dateutil.parser import parse
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
		"Industries": [],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": []
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Deals": [],
		"Stocks": [],
		"Economics": [],
		"Markets": [],
		"Product Launch" : [],
		"Investment" : ["http://www.iamwire.com/category/business/business-investments",],
		"Startups": ["http://www.iamwire.com/",
					"http://www.iamwire.com/category/business/business-startups",]
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
		"Technology": [
					"http://www.iamwire.com/category/technology/technology-internet",
					"http://www.iamwire.com/category/technology/technology-mobile",
					"http://www.iamwire.com/category/technology/technology-gadgets" ],
		"Deadpool": [],
		"Misc": [],
		"Ecommerce": [
					"http://www.iamwire.com/category/business/business-ecommerce",]
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

class IAmWirepiderSpider(CommonBaseSpider):
	name = "iamwire"
	base_dir = "crawl"
	allowed_domains = ["iamwire.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(SgmlLinkExtractor(
			allow=(r'http\:\/\/www\.iamwire\.com\/\d{4}\/\d{2}\/.+\/\d{1,6}',)),
			callback='parse_item', follow=True),
	)

	def parse_item(self, response):
		super(IAmWirepiderSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()

		try :

			# title = tree.xpath('.//div[@class="entry-header"]/h1/text()')
			title = tree.xpath('.//h1[@class="entry-title  margin-bottom-30"]//text()')
			details = tree.xpath('.//div[@class="entry-content"]/p//text()')
			
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore').decode('unicode_escape')
				news_item['details'] =  '\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])

				img_urls = tree.xpath('.//img[contains(@class,\'wp\')]/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				# published_date = tree.xpath('.//time[contains(@class, "entry-date")]/text()')
				published_date = tree.xpath('.//time[contains(@class, "entry-date published")]//text()')
				if published_date:
					news_item['published_date'] = parse(get_stripped_list(published_date)[0])
					# datetime.strptime(get_stripped_list(published_date)[0], '%B %d, %Y')

				author = tree.xpath('.//a[contains(@class, "url fn n")]/text()')
				if author:
					news_item['author'] = get_stripped_list(author)

				tags = tree.xpath('.//ul[contains(@class, "tag-list")]/li/a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)


				meta_result = self.get_meta(tree)

				if 'description' in meta_result:
					news_item['blurb'] = meta_result['description']

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

