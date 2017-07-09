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
		"Industries": ["http://www.smechannels.com/category/press-releases/",],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ["http://www.smechannels.com/",
							"http://www.smechannels.com/category/news/",
							"http://www.smechannels.com/events/",]
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
		"Startups": ["http://www.smechannels.com/category/start-up/"]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Opinion" : ["http://www.smechannels.com/category/analyst-view/",],
		"Cover Story": [],
		"Management Changes": ["http://www.smechannels.com/category/executives-movement/",],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": ["http://www.smechannels.com/category/hardware-news/",
					"http://www.smechannels.com/category/power-solution/",
					"http://www.smechannels.com/category/server/",
					"http://www.smechannels.com/category/surveillance/",
					"http://www.smechannels.com/category/security/",
					"http://www.smechannels.com/category/software-news/",
					"http://www.smechannels.com/category/networking/",
					"http://www.smechannels.com/category/imaging-solutions/",
					"http://www.smechannels.com/category/warranty-and-services/",
					"http://www.smechannels.com/category/unified-communications/",
					"http://www.smechannels.com/category/hardware-news/accessories/",
					"http://www.smechannels.com/category/hardware-news/component/",
					"http://www.smechannels.com/category/hardware-news/peripherals/",
					"http://www.smechannels.com/category/hardware-news/pc-and-notebooks/",
					"http://www.smechannels.com/category/hardware-news/storage/" ],
		"Deadpool": [],
		"Misc": [],
		"Ecommerce": []
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
		"Policy": ["http://www.smechannels.com/category/govt-policy/",],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]


class SMEChannels(CommonBaseSpider):
	name = "smechannel"
	base_dir = "crawl"
	allowed_domains = ["smechannels.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/www\.smechannels\.com\/.+'),),
			callback='parse_item',
					follow=False	),
	)

	def parse_item(self, response):
		filedir = self.pre_write_check()
		filename = os.path.join(filedir, md5(response.url).hexdigest())
		if not os.path.exists(filename):
			with open(filename, "wb") as html:
				html.write(response.body)
		else:
			print "skipped file {0}".format(filename)
			return None

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@class,\"post-tile entry-title\")]/text()")
			details = tree.xpath('//div[contains(@class,"entry-content")]/p//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])
				# " ".join([ele.strip().encode('ascii','ignore') for ele in details])

				img_urls = tree.xpath('.//div[contains(@class,\'feature-img\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				blurb = tree.xpath('.//div[@class=\'entry-content\']/p/em/text()')
				if blurb:
					news_item['blurb'] = blurb[0].strip().encode('ascii','ignore')

				## TODO
				## Author, Tags
				tags = tree.xpath('.//div[contains(@class,\'mom-post-meta single-post-meta\')]/span[3]/a//text()')
				if tags:
					news_item['tags'] = tags

				published_date = tree.xpath('.//span//time[contains(@class,\'updated\')]//text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(" ".join([item.strip().encode('ascii','ignore') for item in published_date]), '%B %d, %Y')


				author = tree.xpath('.//span[contains(@class,\'fn\')]/a/text()')
				if author:
					news_item['author'] = author

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

# http://www.smechannels.com/category/news/
# scrapy runspider demo_crawler.py -o top-stackoverflow-questions.json