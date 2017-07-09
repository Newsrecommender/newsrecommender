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
	  	"Industries": ["http://www.businessinsider.in/exclusives",
	  	"http://www.businessinsider.in/retail"],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.businessinsider.in/smallbusiness"]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
	  	"Deals": [],
		"Stocks": [],
		"Economics": ["http://www.businessinsider.in/yourmoney",
		"http://www.businessinsider.in/wealthadvisor"],
		"Markets": ["http://www.businessinsider.in/clusterstock",
				"http://www.businessinsider.in/moneygame",
				],
		"Product Launch" : [],
        "Investment" : [],
        "Startups": ["http://www.businessinsider.in/startups",]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
	  	"Opinion" : [],
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": ["http://www.businessinsider.in/careers",
					"http://www.businessinsider.in/education/articlelist/27536464.cms",
					"http://www.businessinsider.in/thelife"],
		"Technology": ["http://www.businessinsider.in/sai",
					"http://www.businessinsider.in/science" ],
		"Deadpool": [],
		"Misc": ["http://www.businessinsider.in/warroom"],
		"Ecommerce": ["http://www.businessinsider.in/ecommerce"],
		"Enterprise": ["http://www.businessinsider.in/enterprise"]
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
	  	"Policy": [],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :["http://www.businessinsider.in/law"]
		}
	}
]


class BusinessInsiderSpider(CommonBaseSpider):
	name = "businessinsider"
	base_dir = "crawl"
	allowed_domains = ["businessinsider.in"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/www\.businessinsider\.in\/.+\.cms',)),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(BusinessInsiderSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:

			# title = tree.xpath('//*[@id="Content"]/div[3]/div[3]/div[1]/div/div[1]/div/article/div[1]/h1/text()')
			title = tree.xpath('//*[@id="Content"]/div[3]/div[3]/div[1]/div/div[1]/div/article/div[1]/h1//text()')
			# details = tree.xpath('.//div[contains(@class,\'section1\')]//p//text()')
			details = tree.xpath('.//div[contains(@class,"hide_show_handler main_content")]//p//text()')
			
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([item.strip().encode('ascii','ignore') for item in details])

				img_urls = tree.xpath('.//div[contains(@class,\'MeetingImg blk\')]/img/@src')
				img_url_list = []
				if img_urls:
					for img_url in img_urls:
						img_url_list.append("http://www.businessinsider.in"+img_url)
					news_item['img_urls'] = get_stripped_list(img_url_list)

				published_date = tree.xpath('.//div[contains(@class,\'ByLine\')]//span[contains(@class,\'Date\')]//text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(get_stripped_list(published_date)[0], '%b %d, %Y, %I.%M %p')

				author = tree.xpath('.//a[contains(@class,\'Name\')]/text()')
				if author:
					news_item['author'] = get_stripped_list(author)

				tags = tree.xpath('.//span[contains(@class,\'anchorLink\')]/text()')
				more_tags = tree.xpath('.//div[contains(@id,\'commentHash\')]//a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)
				if more_tags:
					news_item['tags'] = get_stripped_list(more_tags)

				cover_image = tree.xpath('.//div[contains(@class,\'MeetingImg blk\')]/img/@src')
				if cover_image:
					news_item['cover_image'] = img_url_list[0]
					# get_stripped_list(cover_image)

				referer = response.request.headers['Referer']
				for item in categories:
					if referer in sum(item['subcategory'].values(), []):
						news_item['category'] = item['category']
						key = (key for key,value in item['subcategory'].items() if referer in value).next()
						news_item['sub_categories'] = [key]
				return news_item

		except:
			self.log('==Exception=================>>>>>>>>! %r' % e)
		return None


