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

class YourStorySpider(CommonBaseSpider):
	name = "yourstory"
	base_dir = "crawl"
	allowed_domains = ["yourstory.com"]
	start_urls = (
					"http://yourstory.com/",
					"http://yourstory.com/ys-stories/"
					"http://yourstory.com/news/"
					"http://yourstory.com/resources/",
					"http://yourstory.com/ys-in-depth/ys-research/",
					"http://yourstory.com/asia/"
					"http://yourstory.com/africa/",
					"http://yourstory.com/worldwide/usa/"
					"http://yourstory.com/invest-karnataka/"
	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/(social\.)*yourstory\.com\/\d{4}\/\d{2}\/.+\/'),),
			callback='parse_item',
			follow=False),
	)

	def parse_item(self, response):
		super(YourStorySpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:

			title = tree.xpath(".//h3[contains(@class,\"title\")]/text()")
			details = tree.xpath('.//div[@class=\'ys_post_content text\']/p/text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([x.strip().encode('ascii','ignore')for x in details]).strip()
				
				img_urls = tree.xpath('.//img[contains(@class,\'size-full\')]/@src')

				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				author = tree.xpath('.//a[contains(@class, "postInfo color-ys")]/text()')
				if author:
					news_item['author'] = author[0].strip().encode('ascii','ignore')

				published_date = tree.xpath('.//p[contains(@class, "postInfo color-grey mt-5 fr")]/text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[0].split('\n')[1].strip(), '%d %B %Y')

				tags = tree.xpath('.//ul[contains(@class, "articleTags mt-5")]/li/a/text()')
				if tags:
					news_item['tags'] = [x.strip().encode('ascii','ignore')for x in tags]
				return news_item

		except:
			pass
		return None


