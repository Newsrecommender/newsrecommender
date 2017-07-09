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


## Categories
categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
	  	"Industries": ["http://www.thehindu.com/business/Industry/",
	  					"http://www.thehindubusinessline.com/companies/"],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.thehindu.com/business/agri-business/",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Stocks": ["http://www.thehindu.com/business/budget/",],
		"Economics": ["http://www.thehindu.com/business/Economy/",
					"http://www.thehindubusinessline.com/economy/agri-business/",
					"http://www.thehindubusinessline.com/economy/logistics/",
					"http://www.thehindubusinessline.com/economy/macro-economy/",
					],
		"Markets": ["http://www.thehindu.com/business/markets/",
					"http://www.thehindubusinessline.com/markets/",
					"http://www.thehindubusinessline.com/markets/stock-markets/",
					"http://www.thehindubusinessline.com/markets/forex/",
					"http://www.thehindubusinessline.com/markets/commodities/",
					"http://www.thehindubusinessline.com/markets/gold/",
					"http://www.thehindubusinessline.com/markets/todays-pick/",

					],
		"Product Launch" : [],
        "Investment" : [],
        "Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
	  	"Opinion": ["http://www.thehindubusinessline.com/opinion/editorial/",
					"http://www.thehindubusinessline.com/opinion/columns/",
					"http://www.thehindubusinessline.com/opinion/letters/",
					"http://www.thehindubusinessline.com/opinion/books/",],
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": [ "http://www.thehindubusinessline.com/info-tech/",
						"http://www.thehindubusinessline.com/info-tech/social-media/",
						"http://www.thehindubusinessline.com/info-tech/computers-and-laptops/",
						"http://www.thehindubusinessline.com/info-tech/mobiles-tablets/",
						"http://www.thehindubusinessline.com/info-tech/other-gadgets/",],
		"Deadpool": [],
		"Misc": [],
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
	  	"Policy":["http://www.thehindubusinessline.com/economy/policy/"],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]


class Thehindubusiness(CommonBaseSpider):
	name = "thehindubusiness"
	base_dir = "crawl"
	allowed_domains = ["thehindu.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
			Rule(LinkExtractor(
					allow=(r'http:\/\/www\.thehindu\.com\/business\/.+\/?pageNo=\d+#anch',
						r'http:\/\/www\.(thehindu|thehindubusinessline)\.com\/(business|news|markets)\/(budget|Industry|markets|international|stock-markets)\/.+')),
					callback='parse_item',
					follow=False),
	)

	def parse_item(self, response):
		super(Thehindubusiness, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			# title = tree.xpath('.//h1[@class=\'detail-title\']/text()')
			title = tree.xpath('.//h1[@class=\'title\']/text()')
			# details = tree.xpath('.//p[@class=\'body\']/text()')
			details = tree.xpath('.//div[starts-with(@id,"content-body-14269002")]//p//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([x.strip().encode('ascii','ignore')for x in details]).strip()

				# img_urls = tree.xpath('.//div[contains(@class,"text-embed")]/img/@src')
				img_urls = tree.xpath('.//div[@class="img-container picture"]/img/@data-proxy-image')
				other_img_urls = tree.xpath('.//div[contains(@id,"hcenter")]/img/@src')

				if img_urls:
						news_item['img_urls'] = get_stripped_list(img_urls)
				if other_img_urls:
						news_item['img_urls'] = get_stripped_list(other_img_urls)


				cover_image = tree.xpath('.//div[@class="img-container picture"]/img/@data-proxy-image')
				if cover_image:
						news_item['cover_image'] = cover_image[0].strip()

				tags = tree.xpath('.//div[contains(@id, "articleKeywords")]/p//a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

				# published_date = tree.xpath('.//div[contains(@class, "artPubUpdate")]/text()')
				published_date = tree.xpath('.//div[@class="teaser-text update-time"]/span/none/text()')
				date_str = published_date[0].replace("IST","").strip()
				if published_date:
					news_item['published_date'] = parse(date_str)
					# datetime.strptime(published_date[0].split('Updated:')[1].split('IST')[0].strip().encode('ascii','ignore'), '%B %d, %Y %I:%M')

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


