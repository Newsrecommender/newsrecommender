# -*- coding: utf-8 -*-
import os

from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from dateutil.parser import parse
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
		"Stocks": [
					"http://in.reuters.com/finance/currencies",
					"http://in.reuters.com/finance/commodities"],
		"Economics": ["http://in.reuters.com/",],
		"Markets": ["http://in.reuters.com/video/business",
					"http://in.reuters.com/finance/markets/companyOutlooksNews",
					"http://in.reuters.com/finance/markets",
					"http://in.reuters.com/finance/markets/indices",
					"http://in.reuters.com/finance/markets/india-stock-market",
					"http://in.reuters.com/finance/markets/us",
		],
		"Product Launch" : [],
		"Investment" : [],
		"Startups": [],
		"Finance": ["http://in.reuters.com/finance",
					"http://in.reuters.com/finance/economy",
					"http://in.reuters.com/finance/summits",
					"http://in.reuters.com/finance/deals",]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Opinion" : ["http://in.reuters.com/finance/stocks-quotes",],
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": ["http://in.reuters.com/subjects/autos", ],
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


class ReutersSpider(CommonBaseSpider):
	name = "reuters"
	base_dir = "crawl"
	allowed_domains = ["in.reuters.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/in\.reuters\.com\/.+',)),
			callback='parse_item',
					follow=False),
	)

	def parse_item(self, response):
		super(ReutersSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@class,\"article-headline\")]/text()")
			details = tree.xpath('//*[@id="article-text"]//text()')

			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ det.strip().encode('ascii','ignore') for det in details ])
				# " ".join([ det.strip().encode('ascii','ignore') for det in details ])

				img_urls = tree.xpath('.//div[contains(@class,\'related-photo-container\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				blurb = tree.xpath('.//div[contains(@class,\'related-photo-caption\')]/text()')
				if blurb:
					news_item['blurb'] = " ".join([ blurb.strip().encode('ascii','ignore') for blurb in blurb ])

				published_date = tree.xpath('.//span[contains(@class,\'timestamp\')]//text()')
				date_str = published_date[0].replace("|","").replace("IST","").strip()

				if published_date:
					pub_date = published_date[0].strip()
					d1 =[pub_date.split('IST')[0] if 'IST' in pub_date else pub_date]
					# news_item['published_date'] = datetime.strptime(d1[0].strip().encode('ascii','ignore'), '%d %b, %Y')
					# datetime.strptime(d1[0], '%a %b %d, %Y %I:%M%p ')
					news_item['published_date'] = parse(date_str)

				author = tree.xpath('.//span[contains(@class,\'byline\')]/text()')
				if author:
					news_item['author'] = author[0].split('By')[1].strip()

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



