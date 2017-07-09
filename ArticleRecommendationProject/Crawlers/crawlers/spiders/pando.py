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
from common import CommonBaseSpider

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


class PandoSpider(CommonBaseSpider):
	name = "pando"
	base_dir = "crawl"
	allowed_domains = ["pando.com"]
	start_urls = (
					"https://pando.com/",
					"https://pando.com/archives/",
					"https://pando.com/events/",
					"https://pando.com/subscribe/",


	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'https\:\/\/pando\.com\/.+', r'https\:\/\/pando\.com\/archives\/.+', r'https\:\/\/pando\.com\/\d{4}\/',r'https\:\/\/pando\.com\/\d{4}\/\d{2}',r'https\:\/\/pando\.com\/\d{4}\/\d{2}\/.+')),
			callback='parse_item',
					follow=False),
	)

	def parse_item(self, response):
		super(PandoSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath(".//div[contains(@class,\'shim\')]/h1//text()")
			details = tree.xpath('.//div[contains(@class,\'contains-copy excerpt\')]//p//text()')

			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([ det.strip().encode('ascii','ignore') for det in details ])

				img_urls = tree.xpath('.//p[contains(@id,\'featured-image\')]/img/@src')
				if img_urls:
					news_item['img_urls'] = img_urls


				blurb = tree.xpath('.//div[contains(@class,\'contains-copy excerpt\')]/p/text()')
				if blurb:
					news_item['blurb'] = " ".join([ blurb.strip().encode('ascii','ignore') for blurb in blurb ])

				cover_image = tree.xpath('.//p[contains(@id,\'featured-image\')]/img/@src')
				if cover_image:
					news_item['cover_image'] = cover_image

				published_date = tree.xpath('//*[@id="byline"]/span/text()')
				if published_date:
					news_item['published_date'] = datetime.strptime(published_date[1].split('\n')[1].strip(), '%B %d, %Y')
												

				author = tree.xpath('.//p[contains(@id,\'byline\')]/span//a/text()')
				if author: 
					news_item['author'] = author[1].split('By')[1].strip()
				return news_item

		except:
			pass
		return None


