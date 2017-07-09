import os
from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from scrapy.selector import Selector
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from common import CommonBaseSpider, get_stripped_list
from crawlers.items import NewsItem


categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
		"Industries": ["http://www.huffingtonpost.in/news/business",
		],
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
		"Technology": ["http://www.huffingtonpost.in/news/tech", ],
		"Deadpool": [],
		"Misc": ["http://www.huffingtonpost.in/news/politics",],
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

class HuffingtonPostSpider(CommonBaseSpider):
	name = "huffingtonpost"
	base_dir = "crawl"
	allowed_domains = ["huffingtonpost.in"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/www.huffingtonpost.in\/.+'),),
			callback='parse_item',follow=False),
	)

	def parse_item(self, response):
		super(HuffingtonPostSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@class,\"title\")]//text()")
			details =  tree.xpath('.//div[contains(@class,\"content\")]//p//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])

				img_urls = tree.xpath('.//div[contains(@class,\"top-media--image image\")]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				cover_image = tree.xpath('.//span[contains(@class,\"img-caption\")]//img/@src')
				if cover_image:
					news_item['cover_image'] = get_stripped_list(cover_image)[0]

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				published_date = tree.xpath('.//div[contains(@class,\"timestamp\")]/span/text()')
				if published_date:
					pub_date = published_date[0].strip()
					news_item['published_date'] = datetime.strptime(pub_date.split('IST')[0].strip() if 'IST' in pub_date else pub_date, '%d/%m/%Y %I:%M %p')

				author = tree.xpath('.//a[contains(@class,\"author-card__details__name\")]/text()')
				if author:
					news_item['author'] = author[0].strip().encode('ascii','ignore')

				tags = tree.xpath('.//div[contains(@class,\"tag-cloud\")]/a/text()')
				if tags:
					news_item['tags'] = [x.strip().encode('ascii','ignore')for x in tags]

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

