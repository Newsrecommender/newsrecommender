import os
from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from common import CommonBaseSpider, get_stripped_list
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
		"Small Business": ["http://venturebeat.com/category/small-biz/",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Stocks": [],
		"Economics": [],
		"Markets": [],
		"Product Launch" : [],
        "Investment" : ["http://venturebeat.com/category/deals/"],
        "Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": ["http://venturebeat.com/category/marketing/",],
		"Management": ["http://venturebeat.com/category/entrepreneur/",],
		"Technology": [ "http://venturebeat.com/category/mobile/",
						"http://venturebeat.com/category/cloud/",
						"http://venturebeat.com/category/dev/",
						"http://venturebeat.com/category/media/"
			],
		"Deadpool": [],
		"Misc": ["http://venturebeat.com/category/social/",],
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :[]
		}
	}
]


## Uncategorized
## "http://venturebeat.com/",
## "http://events.venturebeat.com/",
## "http://insight.venturebeat.com/",
## "http://events.venturebeat.com/#upcoming_events",
## "http://insight.venturebeat.com/reports/marketing-technology",
## "http://insight.venturebeat.com/reports/mobile",
## "http://insight.venturebeat.com/reports/gaming",
## "http://insight.venturebeat.com/reports/miscellaneous",
## "http://insight.venturebeat.com/content/marketing-technology-subscription",


class VentureBeatSpider(CommonBaseSpider):
	name = "venturebeat"
	base_dir = "crawl"
	allowed_domains = ["venturebeat.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/venturebeat.com\/\d{4}\/\d{2}\/\d{2}\/.+'),),
			callback='parse_item',
					follow=False	),
	)


	def parse_item(self, response):
		super(VentureBeatSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath("//h1[contains(@class,\'article-title\')]//text()")
			details = tree.xpath('//div[contains(@class,"article-content")]/p//text()')

			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])
				

				img_urls = tree.xpath('//div[contains(@class,"article-content")]//img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				published_date = tree.xpath('.//time[contains(@class,\"the-time\")]/text()')
				if published_date :
					news_item['published_date'] = datetime.strptime(published_date[0], '%B %d, %Y %I:%M %p')

				author = tree.xpath('.//a[contains(@class,\"author url fn\")]/text()')
				if author :
					news_item['author'] = get_stripped_list(author)

				tags = tree.xpath('.//div[contains(@class,\"article-tags\")]/a/text()')
				if tags :
					news_item['tags'] = get_stripped_list(tags)

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
