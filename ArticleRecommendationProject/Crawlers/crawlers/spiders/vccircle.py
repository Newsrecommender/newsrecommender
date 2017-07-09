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
from common import CommonBaseSpider,  get_stripped_list

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
	  	"Industries": ["http://www.vccircle.com/healthcare",
					"http://www.vccircle.com/healthcare-pharmaceuticals",
					"http://www.vccircle.com/healthcare-services",
					"http://www.vccircle.com/healthcare-medicaldevices",
					"http://www.vccircle.com/manufacturing",
					"http://www.vccircle.com/manufacturing-engineering",
					"http://www.vccircle.com/manufacturing-commodities",
					"http://www.vccircle.com/manufacturing-textiles",
					"http://www.vccircle.com/infrastructure",
					"http://www.vccircle.com/infra-power",
					"http://www.vccircle.com/infra-transportation",
					"http://www.vccircle.com/infra-construction",
					"http://www.vccircle.com/infra-urbaninfra",
					"http://www.vccircle.com/infra-cleantech",
					"http://www.vccircle.com/infra-realestate",],
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
	  	"Deals": ["http://www.vccircle.com/deals-mna",
				"http://www.vccircle.com/deals-pe",
				"http://www.vccircle.com/deals-venture-capital",
				"http://www.vccircle.com/deals-public-equity",],
		"Stocks": [],
		"Economics": [],
		"Markets": [],
		"Product Launch" : [],
        "Investment" : ["http://venturebeat.com/category/deals/",
			        "http://www.vccircle.com/consumer",],
        "Startups": [],
        "Finance": ["http://www.vccircle.com/finance",
					"http://www.vccircle.com/finance-banking",
					"http://www.vccircle.com/finance-microfinance",
					"http://www.vccircle.com/finance-alternativeinvestment",
					"http://www.vccircle.com/finance-economy",]
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
		"Technology": ["http://www.vccircle.com/tmt",
					"http://www.vccircle.com/tmt-telecom",
					"http://www.vccircle.com/tmt-media",
					"http://www.vccircle.com/tmt-technology", ],
		"Deadpool": [],
		"Misc": [],
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
	  	"Policy": [
		"http://www.vccircle.com/fmcg",
		"http://www.vccircle.com/consumer-education",
		"http://www.vccircle.com/consumer-retail",
		"http://www.vccircle.com/consumer-foodnagri",],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]

## not included
## "http://www.vccircle.com/vcc-tv",


class VccircleSpider(CommonBaseSpider):
	name = "vccircle"
	base_dir = "crawl"
	allowed_domains = ["vccircle.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
			Rule(LinkExtractor(
					allow=(r'http:\/\/www\.vccircle\.com\/news\/.+\/\d{4}\/\d{2}\/\d{2}\/.+',
						r'http:\/\/www\.vccircle\.com\/.+\?page=\d+')),
					callback='parse_item',
					follow=False	),
	)

	def parse_item(self, response):
		super(VccircleSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath('//*[@id="block-system-main"]/div/div[2]/div[2]/h2/text()')
			# details = tree.xpath('.//div[@class=\'cont-text\']/div//text()')
			details = tree.xpath('.//div[@class=\'vcc-snippet-body\']/p[@class=\'selectionShareable\']//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([x.strip().encode('ascii','ignore')for x in details]).strip()

				
				img_urls = tree.xpath('.//div[contains(@class,"field-item even")]/img/@src')
				if img_urls:
						news_item['img_urls'] = get_stripped_list(img_urls)
						news_item['cover_image'] = img_urls[0]

				cover_image = tree.xpath('.//table[contains(@class,"MR15")]//div/img/@src')
				if cover_image:
						news_item['cover_image'] = cover_image[0]

				tags = tree.xpath('.//div[contains(@class, "content-tags")]//a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

				author = tree.xpath('.//span[contains(@class, "byline_person")]/text()')
				if author:
					news_item['author'] = author[0].split('by')[1].strip() if 'by' in author[0] else author[0].strip()

				published_date = tree.xpath('.//span[contains(@class, "date-display-single")]/text()')
				if published_date:
					news_item['published_date'] = datetime.strptime("".join(get_stripped_list(published_date)[0]), '%A, %B %d, %Y -  %I:%M')

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


