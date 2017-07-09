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

class Rediffbusiness(CommonBaseSpider):
	name = "rediffbusiness"
	base_dir = "crawl"
	allowed_domains = ["rediff.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	start_urls = (
		"http://www.rediff.com",
		"http://www.rediff.com/business/",
		"http://www.rediff.com/business/headlines/",
		"http://www.rediff.com/business/report/auto-pix-review-skoda-superb-diesels-ride-quality-is-phenomenal/20160707.htm",
		"http://www.rediff.com/business/report/auto-pix-review-skoda-superb-diesels-ride-quality-is-phenomenal/20160707.htm",
	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/www\.rediff\.com\/business\/(report|interview)\/.+',)),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		filedir = self.pre_write_check()
		filename = os.path.join(filedir, md5(response.url).hexdigest())
		with open(filename, "wb") as html:
			html.write(response.body)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath('.//h1[contains(@class,"arti_heading")]/text()')
			details = tree.xpath('.//div[@id=\'arti_content_n\']//p/text()')
			if title and details:
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				details = [x.strip().encode('ascii','ignore') for x in details if x.strip()]
				details = "\t".join(details).strip()
				news_item['details'] = details
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url

				img_urls = tree.xpath('.//div[@id=\'arti_content_n\']/p/strong/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				tags = tree.xpath('.//div[contains(@id, "tags_div")]//a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

				author = tree.xpath('.//span[contains(@class, "grey1")]/a/text()')
				authorname = tree.xpath('.//span[contains(@class, "grey1")]/text()')
				if author:
					author = [x.strip().encode('ascii','ignore')for x in author]
					author = " ".join(author).strip()
					news_item['author'] = get_stripped_list(author)

				if authorname:
					authorname = [x.strip().encode('ascii','ignore')for x in authorname]
					authorname = " ".join(authorname).strip()
					news_item['author'] = get_stripped_list(authorname)

				published_date = tree.xpath('.//div[contains(@class, "sm1 grey1")]/text()')
				if published_date:
					pub_date = published_date[0]
					news_item['published_date'] = datetime.strptime(pub_date.split('IST')[0].strip().encode('ascii','ignore') if 'IST' in pub_date else pub_date, '%B %d, %Y %H:%M')

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
