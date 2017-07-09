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
		"Investment" : [],
		"Startups": ["http://startoholics.in/",
					"http://startoholics.in/category/startup-stories/",
					"http://startoholics.in/category/startup-stories/page/2/",
					"http://startoholics.in/category/startup-stories/page/3/",
					"http://startoholics.in/category/startup-stories/page/4/",
					"http://startoholics.in/category/startup-stories/page/5/",
					"http://startoholics.in/category/startup-stories/page/6/",
					"http://startoholics.in/category/startup-stories/page/7/",
					"http://startoholics.in/category/startup-stories/page/8/",
					"http://startoholics.in/category/startup-stories/page/9/",
					"http://startoholics.in/category/startup-stories/page/10/",
					"http://startoholics.in/category/startup-stories/page/11/",
					"http://startoholics.in/category/startup-stories/page/12/",
					"http://startoholics.in/category/startup-stories/page/13/",
					"http://startoholics.in/category/startup-stories/page/14/",
					"http://startoholics.in/category/startup-stories/page/15/",]
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

class StartOHolicsSpider(CommonBaseSpider):
	name = "startoholics"
	base_dir = "crawl"
	allowed_domains = ["startoholics.in"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(SgmlLinkExtractor(
			allow=(r'http\:\/.startoholics\.in\/\d{4}\/\d{2}\/.+'),
			deny = (r'http\:/\/startoholics\.in\/(we-are-hiring|category/featured|author/vaishali3092|category/confession-by-an-entrepreneur-startoholic|category/our-take|category/startup-mantra|category/news|category/interviews|category/startup-stories|submit-your-startup|sponsor-us|team|contact)/')),
			callback='parse_item',
			follow=True),
	)
	def parse_item(self, response):
		super(StartOHolicsSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()

		try:
			title = tree.xpath(".//h1/text()")
			details = tree.xpath('.//span[contains(@style,\'font-size:\')]/text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = '\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])
				

				img_urls = tree.xpath('.//img[contains(@class,\'wp-image\')]/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				meta_result = self.get_meta(tree)

				if 'description' in meta_result:
					news_item['blurb'] = meta_result['description']

				author = tree.xpath('.//li[contains(@class, "entry-author")]/a/text()')
				if author:
					news_item['author'] = get_stripped_list(author)

				published_date = tree.xpath('.//li[contains(@class, "date")]/text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[0].strip().encode('ascii','ignore'), '%d %b, %Y')

				tags = tree.xpath('.//p[contains(@class, "entry-tags")]/a/text()')
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
