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


class DealCurrySpider(CommonBaseSpider):
	name = "dealcurry"
	base_dir = "crawl"
	allowed_domains = ["dealcurry.com"]
	start_urls = (
					"http://www.dealcurry.com/",
					"http://www.dealcurry.com/MergersAcquisitions.htm",
					"http://www.dealcurry.com/PrivateEquity.htm/",
					"http://www.dealcurry.com/VentureCapital.htm/",
					"http://www.dealcurry.com/IPO-Offerings.htm/",
					"http://www.dealcurry.com/20160621-Twitter-acquires-machine-learning-startup-Magic-Pony-to-boost-image-content.htm",
					"http://www.dealcurry.com/20150817-Goldman-Sachs-Invests-In-Piramal-Realty.htm",
					"http://www.dealcurry.com/20160125-Big-Data-Firm-Qubole-Raises-Funds.htm",
					'http://www.dealcurry.com/2014094-Monarch-Apparels-Files-DRHP-On-BSE-SME.htm'
	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/www\.dealcurry\.com\/\d+-(.*)',r'http\:\/\/www.dealcurry.com\/(MergersAcquisitions|PrivateEquity|VentureCapital|IPO-Offerings).htm')),
			callback='parse_item', follow=False),
	)

	def parse_item(self, response):
		super(DealCurrySpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()

		try:
			title = tree.xpath(".//h1/text()")
			details = tree.xpath('.//div[contains(@class, "articleSpacer")]/p//text()')
			if title and details:
				news_item['source_url'] = response.url.split('?')[0]
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([x.strip().encode('ascii','ignore')for x in details]).strip()
				# "\t".join([item.strip().encode('ascii','ignore') for item in details if item.strip()])

				tags = tree.xpath('.//div[contains(@style, "padding-bottom:10px")]/span[contains(@style, "color:#346f9a; float:left; text-align:left")]/a/text()')
				news_item['tags'] = tags[0].strip().encode('ascii','ignore')

				published_date = tree.xpath(".//span[contains(@style, 'color:#6b6b6b;float:left; text-align:left; margin-left:5px')]/text()")
				news_item['published_date'] = datetime.strptime(published_date[0].encode('ascii','ignore'), '%d %B %Y') 
				author = tree.xpath('.//div[contains(@style, "")]/span[contains(@style, "color:#6b6b6b; float:left; text-align:left;")]/text()')
				news_item['author'] = author[0].split('by')[1].strip().encode('ascii','ignore')

				img_urls = tree.xpath('.//div[contains(@style, "padding-bottom:10px")]/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				meta_result = self.get_meta(tree)

				if 'description' in meta_result:
					news_item['blurb'] = meta_result['description']

				return news_item

		except:
			pass
		return None
