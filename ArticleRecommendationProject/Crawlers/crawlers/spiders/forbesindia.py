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
		"Industries": ["http://forbesindia.com/features/enterprise/",
		"http://forbesindia.com/upfront/",],
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


class ForbesIndiaSpider(CommonBaseSpider):
	name = "forbesindia"
	base_dir = "crawl"
	allowed_domains = ["forbesindia.com"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
	   Rule(LinkExtractor(
		   allow=(r'http:\/\/forbesindia\.com\/article\/.+'),),
		   callback='parse_item',
		   follow=False),
	)

	def parse_item(self, response):
		super(ForbesIndiaSpider, self).parse_item(response)

		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			# title = tree.xpath(".//div[contains(@class,\"PT10 PB20\")]/div/h1/text()")
			title = tree.xpath(".//div[contains(@class,'col-lg-9 col-md-8 col-sm-7')]/h1//text()")
			# details = tree.xpath('//*[@id="article"]/div[7]/p//text()')
			details = tree.xpath('.//div[contains(@class,"storydiv")]//text()')
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])
				details_start_char = tree.xpath('.//span[contains(@class,\'g-60-b\')]/text()')
				if details_start_char:
					news_item['details'] = details_start_char[0] + news_item['details']

				# img_urls = tree.xpath('.//table[contains(@class,\'PB20\')]//img/@src')
				img_urls = tree.xpath('.//div[contains(@class,"artical-main-sec MT20 spacediv")]//img/@src')
				if not img_urls:
					img_urls = tree.xpath('.//*[@id="article"]//table[1]//tr[1]//img/@src')
				img_urls_p = tree.xpath('.//p[contains(@class,\'padding-bottom:2px;\')]//img/@src')

				if img_urls:
				   news_item['img_urls'] = get_stripped_list(img_urls)
				elif img_urls_p:
				   news_item['img_urls'] = get_stripped_list(img_urls_p)

				# cover_image = tree.xpath('.//table[contains(@class,\'PB20\')]//img/@src')
				cover_image = tree.xpath('.//div[contains(@class,"artical-main-sec MT20 spacediv")]//img/@src')
				if cover_image:
				   news_item['cover_image'] = get_stripped_list(cover_image)[0]

				blurb = tree.xpath('.//div[@class=\'caption1 PT5 PB10\']//text()')
				if blurb:
					news_item['blurb'] = blurb[0].strip().encode('ascii','ignore')

				# published_date_first = tree.xpath('.//div[contains(@class,\'articlehd\')]/span/text()')
				# published_date_second = tree.xpath('.//div[contains(@class,\'date PB5\')]/text()')

				published_date_first = tree.xpath('.//div[contains(@class,"update-date text-uppercase")]//text()')
				if published_date_first:
					news_item['published_date'] = datetime.strptime(published_date_first[1].encode('ascii','ignore'), ' %b %d, %Y ')
					# datetime.strptime(published_date_first[0].split('|')[1].strip('').encode('ascii','ignore'), ' %b %d, %Y ')

				# author =tree.xpath('.//div[contains(@class,\'author_name\')]/a/text()')
				author =tree.xpath('.//div[contains(@class,"author-name text-uppercase")]//text()')
				author_name = tree.xpath('.//div[contains(@class,\'byline1 PT5\')]/a/text()')
				if author:
					news_item['author'] = get_stripped_list(author)
				if author_name:
					news_item['author'] = get_stripped_list(author_name)

				tags = tree.xpath('.//div[contains(@class,\'link PT10\')]/a/text()')
				if tags:
					news_item['tags'] = get_stripped_list(tags)

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


