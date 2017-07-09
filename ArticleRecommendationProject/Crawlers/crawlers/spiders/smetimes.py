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
		"Small Business": ["http://www.smetimes.in/",
					"http://www.smetimes.in/smetimes/news/industry/india-industry-main-page.html",
					"http://www.smetimes.in/smetimes/news/world/world_news.html",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Deals": [],
		"Stocks": [],
		"Economics": ["http://www.smetimes.in/smetimes/news/indian-economy-news/india_economy.html",],
		"Markets": ["http://www.smetimes.in/smetimes/news/global-business/global-business-page.html",],
		"Product Launch" : [],
		"Investment" : [],
		"Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Opinion" : ["http://www.smetimes.in/smetimes/editorial/index.html"],
		"Cover Story": ["http://www.smetimes.in/smetimes/in-depth/indepth.html",],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": [ "http://www.smetimes.in/smetimes/news/pr_newswire/index.html",],
		"Deadpool": [],
		"Misc": ["http://www.smetimes.in/smetimes/news/politics-nation.html",],
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

class SMETimesSpider(CommonBaseSpider):
	name = "smetimes"
	base_dir = "crawl"
	allowed_domains = ["smetimes.in"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(SgmlLinkExtractor(
			# allow=(r'http\:\/\/\www\.smetimes\.\in\/smetimes\/news\/pr_newswire\/2016\/May\/\d{2}\/.+'),),
			allow=(r'http\:\/\/\www\.smetimes\.in\/smetimes\/news\/.+'),),
			callback='parse_item',
			follow=True),
	)

	def parse_item(self, response):
		super(SMETimesSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//span[contains(@class,\"blue-heading\")]//text()")
			details = tree.xpath('//span[@class="text"]//text()')
			details = [ele.encode('ascii','ignore').replace("\n","") for ele in details]
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join(details)

				img_urls = tree.xpath('//span[contains(@class,"text")]//img/@src')

				if not img_urls[0].lower().find(self.name.lower()) == -1:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				published_date = tree.xpath('.//div[contains(@align,\'justify\')]/span/span//text()')
				if published_date:
					pub_date = published_date[0].split("|")[1]
					news_item['published_date'] = datetime.strptime(pub_date, ' %d %b, %Y')

				author = tree.xpath('.//div[contains(@align,\'justify\')]/span/span//text()')
				if author :
					news_item['author'] = author[0].split("|")[0].strip()

				referer = response.request.headers['Referer']
				for item in categories:
					if referer in sum(item['subcategory'].values(), []):
						news_item['category'] = item['category']
						key = (key for key,value in item['subcategory'].items() if referer in value).next()
						news_item['sub_categories'] = [key]
				self.log('==Exception=================>>>>>>>>! %r' % news_item)
				return news_item

		except Exception, e:
			self.log('==Exception=================>>>>>>>>! %r' % e)
		return None

