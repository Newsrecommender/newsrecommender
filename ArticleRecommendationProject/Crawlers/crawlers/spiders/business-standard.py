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
	  	"Industries": ["http://www.business-standard.com/companies",
	  		"http://www.business-standard.com/category/specials-power-10927.htm"],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.business-standard.com/sme"]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
	  	"Deals": [],
		"Stocks": ["http://www.business-standard.com/markets-stocks",
			"http://www.business-standard.com/markets-commodities",
			"http://www.business-standard.com/markets-ipos",
			"http://www.business-standard.com/markets-mutual-funds",],
		"Economics": ["http://www.business-standard.com/economy-policy"],
		"Markets": ["http://www.business-standard.com/finance",
			"http://www.business-standard.com/markets-news"],
		"Product Launch" : [],
        "Investment" : [],	
        "Startups": ["http://www.business-standard.com/category/companies-start-ups-10113.htm"]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
	  	"Opinion" : [	],
		"Cover Story": ["http://www.business-standard.com/category/specials-data-stories-10908.htm",
				"http://www.business-standard.com/opinion"],
		"Management Changes": ["http://www.business-standard.com/management"],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": ["http://www.business-standard.com/technology"],
		"Deadpool": [],
		"Misc": [],
		"Ecommerce": [],
		"Enterprise": []
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


class BusinessStandardSpider(CommonBaseSpider):
	name = "business-standard"
	base_dir = "crawl"
	allowed_domains = ["business-standard.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/\www\.business\-standard\.com\/article\/sme\/.+',)),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(BusinessStandardSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:

			title = tree.xpath(".//h1[contains(@class,\'headline\')]//text()")
			details = tree.xpath('.//span[contains(@class,\'p-content\')]/div//text()[not(ancestor::script)]')
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([item.strip().encode('ascii','ignore') for item in details])

				img_urls = tree.xpath('.//img[contains(@class,\'imgCont\')]/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)


				published_date = tree.xpath('.//p[contains(@class,\'fL\')]//span//text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[3].split("\t")[0], '%B %d, %Y')

				related = tree.xpath('.//div[contains(@class,\'readmore_tagBG\')]//h2//a/text()')
				if related:
					news_item['tags'] = [item.strip() for item in related if item.strip()]

				cover_image = tree.xpath('.//img[contains(@class,\'imgCont\')]/@src')
				if cover_image:
					news_item['cover_image'] = cover_image
				return news_item

		except:
			pass
		return None


