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
from scrapy.http import Request


categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
	  	"Industries": ["http://www.financialexpress.com/industry/sme/",
	  					"http://www.financialexpress.com/industry/companies/",
						"http://www.financialexpress.com/industry/automobiles/",
						"http://www.financialexpress.com/industry/banking-finance/",
						"http://www.financialexpress.com/industry/insurance/",
						"http://www.financialexpress.com/industry/jobs/"],
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
		"Stocks": ["http://www.financialexpress.com/stock-market/"],
		"Economics": ["http://www.financialexpress.com/economy/"],
		"Markets": ["http://www.financialexpress.com/currency/",
					"http://www.financialexpress.com/markets/",
					"http://www.financialexpress.com/markets/world-markets/",
					"http://www.financialexpress.com/markets/commodities/",],
		"Product Launch" : [],
        "Investment" : ["http://www.financialexpress.com/personal-finance/"],
        "Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": [],
		"Technology": ["http://www.financialexpress.com/industry/tech/"],
		"Deadpool": [],
		"Misc": [],
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


### Uncovered links
## "http://www.financialexpress.com/lifestyle/",
## "http://www.financialexpress.com/lifestyle/health/",
## "http://www.financialexpress.com/lifestyle/science/",
## "http://www.financialexpress.com/lifestyle/showbiz/",
## "http://www.financialexpress.com/lifestyle/travel-tourism/",
## "http://www.financialexpress.com/print/editors-picks/",
## "http://www.financialexpress.com/print/international/",
## "http://www.financialexpress.com/print/edits-columns/",
## "http://www.financialexpress.com/fe-columnist/",
## "http://www.financialexpress.com/print/fe-360/",
## "http://www.financialexpress.com/print/politics/",
## "http://www.financialexpress.com/print/economy-print/",
## "http://www.financialexpress.com/print/personal-finance-print/",
## "http://www.financialexpress.com/print/front-page/",
## "http://www.financialexpress.com/print/fe-insight/",
## "http://www.financialexpress.com/print/fecampus/",
## "http://www.financialexpress.com/print/brand-wagon/",

class FinancialExpressSpider(CommonBaseSpider):
	name = "financialexpress"
	base_dir = "crawl"
	allowed_domains = ["financialexpress.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/www.financialexpress.com\/.+'),),
			callback='parse_item', follow=True),
	)

	def parse_item(self, response):
		super(FinancialExpressSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)
		self.log('==RESPONSE=================>>>>>>>>! %s' % response.request.headers['Referer'])
		referer = response.request.headers['Referer']

		news_item = NewsItem()
		try:
			title = tree.xpath(".//meta[@itemprop='headline']/@content")
			details = tree.xpath(".//div[@itemprop='articleBody']//p//text()")
			# self.log('==Title=================>>>>>>>>! %s' % title[0])

			if title and details:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])

				img_urls = tree.xpath(".//div[@itemprop='articleBody']//img[contains(@class,'size-full')]/@src")

				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				if 'og:updated_time' in meta_result:
					news_item['published_date'] =  datetime.strptime(meta_result['og:updated_time'].split("+")[0], '%Y-%m-%dT%H:%M:%S')


				authors = tree.xpath(".//meta[@itemprop='author']/@content")
				if authors:
					news_item['author'] = get_stripped_list(authors)

				for item in categories:
					if referer in sum(item['subcategory'].values(), []):
						news_item['category'] = item['category']
						key = (key for key,value in item['subcategory'].items() if referer in value).next()
						news_item['sub_categories'] = [key]
				return news_item

		except Exception, e:
			self.log('==Exception=================>>>>>>>>! %r' % e)
		return None
