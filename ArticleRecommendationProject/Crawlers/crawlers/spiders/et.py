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
from common import CommonBaseSpider,get_stripped_list

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


categories = [
	 {
	  "category": "Industry",
	  "subcategory": {
	  	"Industries": ['http://economictimes.indiatimes.com/industry/energy',
					'http://economictimes.indiatimes.com/industry/services',
					'http://economictimes.indiatimes.com/news/company',],
		"Growth" : [],
		"Mergers and Acquisitions" : [],
		"Partnership" : [],
		"Pivot/Rebranding": [],
		"Small Business": ['http://economictimes.indiatimes.com/small-biz/startups',
						'http://economictimes.indiatimes.com/small-biz/sme-sector',
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-2.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-3.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-4.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-5.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-6.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-7.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-8.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-9.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-10.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-11.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-12.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-13.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-14.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-15.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-16.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-17.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-18.cms",
						"http://economictimes.indiatimes.com/small-biz/sme-sector/articlelist/msid-11993058,page-19.cms",
						'http://economictimes.indiatimes.com/small-biz/us-sme/newslist/46956986.cms',]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Stocks": [],
		"Economics": ['http://economictimes.indiatimes.com/small-biz/money/articlelist/47280660.cms'],
		"Markets": ['http://economictimes.indiatimes.com/markets/ipo',
					'http://economictimes.indiatimes.com/markets/forex',
					'http://economictimes.indiatimes.com/markets/bonds',
					'http://economictimes.indiatimes.com/markets/stocks',
					'http://economictimes.indiatimes.com/markets/commodities',
					'http://economictimes.indiatimes.com/markets/live-coverage',
					'http://economictimes.indiatimes.com/markets/technical-charts',],
		"Product Launch" : [],
        "Investment" : ['http://economictimes.indiatimes.com/nri/nri-investments',
					'http://economictimes.indiatimes.com/nri/nri-real-estate',],
        "Startups": []
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
	  	"Opinion" : [],
		"Cover Story": [],
		"Management Changes": [],
		"Sales & Marketing": ['http://economictimes.indiatimes.com/small-biz/marketing-branding'],
		"Management": ['http://economictimes.indiatimes.com/small-biz/entrepreneurship',
						'http://economictimes.indiatimes.com/small-biz/hr-leadership',],
		"Technology": ['http://economictimes.indiatimes.com/tech/software',
						'http://economictimes.indiatimes.com/tech/internet',
						'http://economictimes.indiatimes.com/tech/hardware',
						'http://economictimes.indiatimes.com/tech/ites',
						'http://economictimes.indiatimes.com/small-biz/security-tech'],
		"Deadpool": [],
		"Misc": ['http://economictimes.indiatimes.com/nri/nri-tax',
			'http://economictimes.indiatimes.com/nri/nris-in-news',
			'http://economictimes.indiatimes.com/nri/working-abroad',
			'http://economictimes.indiatimes.com/news/politics-nation',
			'http://economictimes.indiatimes.com/nri/returning-to-india',
			'http://economictimes.indiatimes.com/nri/visa-and-immigration',
			'http://economictimes.indiatimes.com/nri/forex-and-remittance',],
	  }
	},
	{
	  "category": "Policy",
	  "subcategory": {
	  	"Policy": ['http://economictimes.indiatimes.com/small-biz/policy-trends/articlelist/11993039.cms',],
		"RBI" : [],
		"Regulations" : [],
		"Taxation" : [],
		"Law & Order" :['http://economictimes.indiatimes.com/small-biz/legal/articlelist/47280656.cms',]
		}
	}
]



class ETSpider(CommonBaseSpider):
	name = "et"
	base_dir = "crawl"
	allowed_domains = ["economictimes.indiatimes.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(LinkExtractor(
			allow=(
				r'http\:\/\/economictimes\.indiatimes\.com\/(defence|industry|mutual-funds)',
				r'http\:\/\/economictimes\.indiatimes\.com\/mf\/(mf-news|analysis)\/.+\.cms',
				r'http\:\/\/economictimes\.indiatimes\.com\/personal-finance\/(mutual-funds|)\/.+\.cms',
				r'http\:\/\/economictimes\.indiatimes\.com\/tech\/(hardware|software|internet|ites)\/.+\.cms'
				r'http\:\/\/economictimes\.indiatimes\.com\/industry\/(cons-products|energy|indl-goods|healthcare|services|)\/.+\.cms',
				r'http\:\/\/economictimes\.indiatimes\.com\/markets\/(stocks|ipo|live-coverage|technical-charts|commodities|forex|bonds|)\/.+\.cms',
				r'http\:\/\/economictimes\.indiatimes\.com\/news\/(company|ipo|live-coverage|technical-charts|commodities|forex|bonds|politics-nation)\/.+\.cms'
				r'http\:\/\/economictimes\.indiatimes\.com\/nri\/(nris-in-news|nri-real-estate|nri-investments|nri-tax|forex-and-remittance|visa-and-immigration|working-abroad|returning-to-india)\/.+\.cms',
				r'http\:\/\/economictimes\.indiatimes\.com\/small-biz\/(legal|money|startups|entrepreneurship|sme-sector|policy-trends|marketing-branding|hr-leadership|security-tech|us-sme|startups)\/.+\.cms',
				)),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(ETSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)
		news_item = NewsItem()

		try:
			title = tree.xpath('.//h1[contains(@class, "title")]/text()[1]')
			details = tree.xpath('.//div[@class=\'Normal\']//text()')
			if title and details :
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().decode('unicode_escape').encode('ascii','ignore')
				news_item['details'] = "\t".join([item.strip().encode('ascii','ignore') for item in details if item.strip()])
				news_item['cover_image'] = ''
				news_item['blurb'] = ''
				news_item['img_urls'] = []

				img_urls = tree.xpath('.//figure/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']

				news_item['blurb'] =  news_item['blurb'].decode('unicode_escape').encode('ascii','ignore')

				published_date = tree.xpath('.//div[contains(@class,\'byline\')]/text()')
				self.log('==Pub date=================>>>>>>>>! %r' % published_date)
				print "pb------------------->",published_date
				if published_date:
					# published_date = " ".join(published_date)
					# news_item['published_date'] = datetime.strptime(published_date.split('|')[1].strip('IST').strip(), '%b %d, %Y, %I.%M %p')
					news_item['author'] = published_date[0].split('|')[0].strip()
					date_str = (published_date[0].split(":")[1:])[0].replace("IST","").strip()
					news_item['published_date'] = datetime.strptime(date_str, '%b %d, %Y, %I.%M %p')

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




