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
from common import CommonBaseSpider,get_stripped_list

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
		"Small Business": ["https://gigaom.com/archives/small-business.html",]
	  }
	},
	{
	  "category": "Fund Raising",
	  "subcategory": {
		"Deals": [],
		"Stocks": [],
		"Economics": ["https://gigaom.com/archives/economics.html",
		"https://gigaom.com/archives/economy.html",
		"https://gigaom.com/archives/money.html",
		"https://gigaom.com/archives/non-profit.html",
		"https://gigaom.com/archives/revenue.html",
		"https://gigaom.com/archives/b2b.html",
		"https://gigaom.com/archives/bank-of-america.html",
		"https://gigaom.com/archives/enterprise.html",
		"https://gigaom.com/archives/world-bank.html",],
		"Markets": ["https://gigaom.com/archives/accel-partners.html",
		"https://gigaom.com/archives/andreessen-horowitz.html",
		"https://gigaom.com/archives/austin-ventures.html",
		"https://gigaom.com/archives/balderton-capital.html",
		"https://gigaom.com/archives/benchmark-capital.html",
		"https://gigaom.com/archives/bessemer-venture-partners.html",
		"https://gigaom.com/archives/canaan-partners.html",
		"https://gigaom.com/archives/charles-river-ventures.html",
		"https://gigaom.com/archives/digital-sky-technologies.html",
		"https://gigaom.com/archives/draper-fisher-jurvetson.html",
		"https://gigaom.com/archives/first-round-capital.html",
		"https://gigaom.com/archives/foundation-capital.html",
		"https://gigaom.com/archives/founders-fund.html",
		"https://gigaom.com/archives/foundry-group.html",
		"https://gigaom.com/archives/general-catalyst-partners.html",
		"https://gigaom.com/archives/goldman-sachs.html",
		"https://gigaom.com/archives/greycroft-partners.html",
		"https://gigaom.com/archives/greylock-partners.html",
		"https://gigaom.com/archives/harbinger-capital.html",
		"https://gigaom.com/archives/hutchison-whampoa.html",
		"https://gigaom.com/archives/index-ventures.html",
		"https://gigaom.com/archives/intel-capital.html",
		"https://gigaom.com/archives/intellectual-ventures.html",
		"https://gigaom.com/archives/jana-partners.html",
		"https://gigaom.com/archives/khosla-ventures.html",
		"https://gigaom.com/archives/kleiner-perkins-caufield-byers.html",
		"https://gigaom.com/archives/lightspeed-venture-partners.html",
		"https://gigaom.com/archives/ma-venture-capital.html",
		"https://gigaom.com/archives/matrix-partners.html",
		"https://gigaom.com/archives/mayfield-fund.html",
		"https://gigaom.com/archives/menlo-ventures.html",
		"https://gigaom.com/archives/mohr-davidow-ventures.html",
		"https://gigaom.com/archives/morgan-stanley.html",
		"https://gigaom.com/archives/new-enterprise-associates.html",
		"https://gigaom.com/archives/north-bridge-venture-partners.html",
		"https://gigaom.com/archives/norwest-venture-partners.html",
		"https://gigaom.com/archives/polaris-venture-partners.html",
		"https://gigaom.com/archives/pricewaterhousecoopers.html",
		"https://gigaom.com/archives/redpoint-ventures.html",
		"https://gigaom.com/archives/sequoia-capital.html",
		"https://gigaom.com/archives/shasta-ventures.html",
		"https://gigaom.com/archives/spark-capital.html",
		"https://gigaom.com/archives/true-ventures.html",
		"https://gigaom.com/archives/union-square-ventures.html",
		"https://gigaom.com/archives/vantagepoint-venture-partners.html",
		"https://gigaom.com/archives/venrock.html",
		"https://gigaom.com/archives/business.html",
		"https://gigaom.com/archives/classifieds-business.html",
		"https://gigaom.com/archives/business-intelligence.html",
		"https://gigaom.com/archives/ceo.html",
		"https://gigaom.com/archives/corporate.html",],
		"Product Launch" : [],
		"Investment" : ["https://gigaom.com/archives/bankruptcy.html",
		"https://gigaom.com/archives/businessfinance.html",
		"https://gigaom.com/archives/dow-jones.html",
		"https://gigaom.com/archives/earnings.html",
		"https://gigaom.com/archives/finance.html",
		"https://gigaom.com/archives/financial-services.html",
		"https://gigaom.com/archives/funding.html",
		"https://gigaom.com/archives/fundraising.html",
		"https://gigaom.com/archives/industry-moves.html",
		"https://gigaom.com/archives/investment.html",
		"https://gigaom.com/archives/ipo.html",
		"https://gigaom.com/archives/market-share.html",
		"https://gigaom.com/archives/mergers-acquisitions.html",
		"https://gigaom.com/archives/nvca.html",
		"https://gigaom.com/archives/nasdaq.html",
		"https://gigaom.com/archives/stocks.html",
		"https://gigaom.com/archives/venture-capital.html",],
		"Startups": [
		"https://gigaom.com/archives/arm.html",
		"https://gigaom.com/archives/betaworks.html",
		"https://gigaom.com/archives/see-founders-run.html",
		"https://gigaom.com/archives/startup-funding.html",
		"https://gigaom.com/archives/startup-profile.html",
		"https://gigaom.com/archives/startups.html",
		"https://gigaom.com/archives/techstars.html",
		"https://gigaom.com/archives/xoom.html",
		"https://gigaom.com/archives/y-combinator.html",
		"https://gigaom.com/archives/yell.html",]
	  }
	},
	{
	  "category": "Dedicated Coverage",
	  "subcategory": {
		"Opinion" : [],
		"Cover Story": ["https://gigaom.com/archives/success.html",],
		"Management Changes": [],
		"Sales & Marketing": [],
		"Management": ["https://gigaom.com/archives/entrepreneurs.html",
		"https://gigaom.com/archives/leadership.html",
		"https://gigaom.com/archives/management.html",
		],
		"Technology": [ ],
		"Deadpool": [],
		"Misc": [],
		"Ecommerce": ["https://gigaom.com/archives/e-commerce.html",]
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

class GigaomSpider(CommonBaseSpider):
	name = "gigaom"
	base_dir = "crawl"
	allowed_domains = ["gigaom.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls

	rules = (
		Rule(LinkExtractor(
			allow=(r'https\:\/\/gigaom\.com\/.+',)),
			callback='parse_item',
			follow=False),
	)

	def parse_item(self, response):
		super(GigaomSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//h1[contains(@class,\'entry-title single-title\')]//text()")
			detail = tree.xpath('.//section[contains(@class,\'entry-content wrap cf\')]//p//text()')

			if title and detail:
				news_item['source'] = self.name
				news_item['source_url'] = response.url.split('?')[0]
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ det.strip().encode('ascii','ignore') for det in detail ])

				img_urls = tree.xpath('.//div[contains(@class,\'featured-image\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				cover_image = tree.xpath('.//h1[contains(@class,\'entry-title single-title\')]/img/@src')
				if cover_image:
					news_item['cover_image'] = get_stripped_list(cover_image)[0]

				author = tree.xpath('.//span[contains(@class,\'entry-author author\')]/a/text()')
				if author:
					news_item['author'] = get_stripped_list(author)

				published_date = tree.xpath('.//time[contains(@class,\'updated entry-time\')]/text()')
				date_str = published_date[0].replace("-","").replace("CST","").strip()
				if published_date:
					news_item['published_date'] = datetime.strptime( date_str, '%b %d, %Y  %I:%M %p')
					# news_item['published_date'] = datetime.strptime( published_date[0].strip('PDT'), '%b %d, %Y - %I:%M %p ')

				tags = tree.xpath('.//span[contains(@itemprop,\'keywords\')]//text()')
				if tags:
					news_item['tags'] = [ det.strip().encode('ascii','ignore') for det in [var for var in tags if var != ' '] ]

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


