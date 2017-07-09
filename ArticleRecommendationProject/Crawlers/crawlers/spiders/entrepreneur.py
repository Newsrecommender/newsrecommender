# -*- coding: utf-8 -*-
import os
import string

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
	  	"Industries": [],
		"Growth" : ["https://www.entrepreneur.com/topic/growth-strategies",
					],
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
		"Markets": ["https://www.entrepreneur.com/topic/finance",
					"https://www.entrepreneur.com/topic/marketing",],
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
		"Management": ["https://www.entrepreneur.com/",
					"https://www.entrepreneur.com/topic/starting-a-business",
					"https://www.entrepreneur.com/topic/entrepreneurs",],
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

## uncategorized
# "https://www.entrepreneur.com/latest",
# "https://www.entrepreneur.com/popular",
# "https://www.entrepreneur.com/howto",
# "https://www.entrepreneur.com/lists",


class EntrepreneurSpider(CommonBaseSpider):
	name = "entrepreneur"
	base_dir = "crawl"
	allowed_domains = ["entrepreneur.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'https\:\/\/www\.entrepreneur\.com\/article\/\d{6}',)),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(EntrepreneurSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:

			title = tree.xpath(".//h1[contains(@class,\'headline\')]//text()")
			details = tree.xpath('.//div[contains(@class,\'bodycopy\')]//p//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ det.strip().encode('ascii','ignore') for det in details ])

				img_urls = tree.xpath('.//div[contains(@class,\'hero topimage\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				blurb = tree.xpath('.//div[contains(@class,\'bodycopy\')]/p/text()')
				news_item['blurb'] =  " ".join([ short_blurb.strip().encode('ascii','ignore') for short_blurb in blurb[0:1]])

				published_date = tree.xpath('.//time[contains(@itemprop,\'datePublished\')]//text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[0].strip(), '%B %d, %Y')

				tags = tree.xpath('.//div[contains(@class,\'article-tags\')]/a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)
				author = tree.xpath('.//div[contains(@itemprop,\'name\')]/text()')
				if author:
					news_item['author'] = get_stripped_list(author)

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


