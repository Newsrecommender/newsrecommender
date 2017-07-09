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
		"Small Business": ["http://www.ndtv.com/topic/sme",
		"http://www.ndtv.com/topic/sme/news"]
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


class NdtvSpider(CommonBaseSpider):
	name = "ndtv"
	base_dir = "crawl"
	allowed_domains = ["ndtv.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/profit\.ndtv\.com\/news\/.+\/.+',
			r'http:\/\/www\.ndtv\.com\/topic\/sme\/news\/page\-\d+')),
			callback='parse_item',
			follow=False	),
	)

	def parse_item(self, response):
		super(NdtvSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			# title = tree.xpath('.//div[contains(@class, "storytitle")]/h1/text()')
			title = tree.xpath('.//h1[@itemprop="headline"]//text()')
			details = tree.xpath('.//div[contains(@class, "pdl200")]//text()[not(ancestor::script)]')
			# details = tree.xpath('.//span[@itemprop="articleBody"]//text')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] ='\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])

				# img_urls = tree.xpath('.//div[contains(@class,"storypicbig")]/img/@src')
				img_urls = tree.xpath('.//div[contains(@class,"whosaid_top_mainimg_cont")]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				# cover_image = tree.xpath('.//table[contains(@class,"MR15")]//div/img/@src')
				# if cover_image:
				news_item['cover_image'] = get_stripped_list(img_urls)[0]

				published_date = tree.xpath('.//div[contains(@class, "dateline")]/text()')
				date_str = published_date[0].replace("(IST)","").strip().split(":",1)[1]

				if published_date:
					pub_date = published_date[0].strip()
					news_item['published_date'] = parse(date_str)
					# pub_date.strip('| Last Updated:(IST)').strip().encode('ascii','ignore') if '| Last Updated:(IST)' in pub_date else pub_date

				tags=tree.xpath('.//p[contains(@class, "alltags")]/a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

				author = tree.xpath('.//div[contains(@class, "dateline")]/a/text()')
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



