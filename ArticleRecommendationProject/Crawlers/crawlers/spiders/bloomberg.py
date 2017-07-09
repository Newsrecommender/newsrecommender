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
from common import CommonBaseSpider, get_stripped_list
from crawlers.items import NewsItem
from scrapy.http import Request

## Uncategorized
## http://www.bloomberg.com/businessweek
categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
		"Industries": ["http://www.bloomberg.com/news/industries"],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.bloomberg.com/small-business"]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Stocks": ["http://www.bloomberg.com/markets/stocks"],
		"Economics": ["http://www.bloomberg.com/markets/economics"],
		"Markets": ["http://www.bloomberg.com/markets",
					"http://www.bloomberg.com/markets/benchmark",
					"http://www.bloomberg.com/markets/rates-bonds",
					"http://www.bloomberg.com/markets/currencies",
					"http://www.bloomberg.com/markets/commodities"],
		"Product Launch" : [],
		"Investment" : [],
		"Startups": ["http://www.bloomberg.com/topics/startups"]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Cover Story": ["http://www.bloomberg.com/topics/cover-story"],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": [ "http://www.bloomberg.com/technology",
						"http://www.bloomberg.com/news/science-energy",
						"http://www.bloomberg.com/topics/global-tech",
						"http://www.bloomberg.com/topics/cybersecurity",
						"http://www.bloomberg.com/topics/silicon-valley"],
		"Deadpool": [],
		"Misc": [],
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]


class BloombergSpider(CommonBaseSpider):
	name = "bloomberg"
	base_dir = "crawl"
	allowed_domains = ["bloomberg.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/www.bloomberg.com\/news\/articles\/\d{4}-\d{2}-\d{2}\/.+'),),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(BloombergSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)
		self.log('==RESPONSE=================>>>>>>>>! %s' % response.request.headers['Referer'])
		news_item = NewsItem()
		try:
			# title = tree.xpath(".//span[contains(@class,\"lede-headline__highlighted\")]//text()")
			title = tree.xpath(".//span[contains(@class,\"lede-text-only__highlight\")]//text()")
			# details = tree.xpath('.//div[contains(@class,\"article-body__content\")]//p//text()')
			details = tree.xpath('.//div[contains(@class,\"body-copy\")]//p//text()')
			# self.log('==Title=================>>>>>>>>! %s' % title[0])
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])

				# img_urls = tree.xpath('.//div[contains(@class,\"inline-media__unlinked-image\")]//img/@src')
				img_urls = tree.xpath('.//div[contains(@class,"lazy-img")]/img//@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				# published_date = tree.xpath('.//time[contains(@class,\"published-at time-based\")]/text()')
				published_date = tree.xpath('//*[@itemprop="datePublished"]//text()')
				# published_date = tree.xpath('.//div[contains(@class,"lede-text-only__times")]//text()')[1]
				if published_date :
					date_str = published_date[1].split('GMT')[0].strip()
					news_item['published_date'] = parse(date_str)
					# datetime.strptime(published_date[0].split('EDT')[0].strip().encode('ascii','ignore'), '%B %d, %Y %I:%M %p')

				# authors = tree.xpath('.//div[contains(@class,\"author-byline\")]/a/text()')
				authors = tree.xpath('.//div[contains(@class,"author")]//text()')

				if authors:
					news_item['author'] = get_stripped_list(authors)[0]

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
