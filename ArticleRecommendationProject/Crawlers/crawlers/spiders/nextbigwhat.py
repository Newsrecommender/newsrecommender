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
from common import CommonBaseSpider

# Import item that will be used to generate JSON feed
from crawlers.items import NewsItem


class NextBigWhatSpider(CommonBaseSpider):
	name = "nextbigwhat"
	base_dir = "crawl"
	allowed_domains = ["nextbigwhat.com"]
	start_urls = (
		"http://www.nextbigwhat.com/",
		"http://www.nextbigwhat.com/c/news"
		"http://www.nextbigwhat.com/c/productgeeks",
		"http://news.nextbigwhat.com/",
		"http://www.nextbigwhat.com/peppertap-shuts-down-297/"
		"http://www.nextbigwhat.com/three-co-founders-housing-quit-297/"
		"http://www.nextbigwhat.com/time-names-sachin-binny-100most-influential-people-297/"
		"http://www.nextbigwhat.com/vcommission-invests-undisclosed-amount-letreach-spinsvilla-297/"
		"http://www.nextbigwhat.com/cleartax-raises-1-3-million-funding-led-silicon-valley-angels-297/"
		"http://www.nextbigwhat.com/meat-delivery-startup-licious-raises-3-million-series-funding-297/"
		"http://www.nextbigwhat.com/digital-payments-company-transerv-raises-15-million-series-c-funding-297/"
		"http://www.nextbigwhat.com/craft-beer-brand-witlinger-secures-funding-support-expansion-plans-297/"
	)
	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/www\.nextbigwhat\.com\/.+',r'http\:\/\/news\.nextbigwhat\.com\/.+'),
			deny = (r'http\:\/\/unpluggd\.nextbigwhat\.com', r'http\:\/\/www\.nextbigwhat\.com\/(job|jobs)\/.+', r'http\:\/\/www\.nextbigwhat\.com\/(opinion-analysis|todoed-297|unpluggd-2016-summer-edition|nanolocal-technologies-bangalore-5046-product-manager|unpluggd-2016-edition-297|startups|tech|digitalindia|terms-and-conditions|introducing-anirudh-narayan-growth-hacking-maverick-unpluggd-297|unpluggd-2016-297|tos|contact|about-nextbigwhat|events|jobs|productgeeks|post-a-job|unpluggd-2016-speaker-form-297|xprize-foundation-mumbai-5046-project-manager|xprize-foundation-mumbai-5046-technical-director-womens-safety|statsbot-google-analytics-mixpanel-bot-slack-297|voonik-sujayath-unpluggd-297|we-are-hiring|page|pr)\/')),
			callback='parse_item',
					follow=False),
	)

	def parse_item(self, response):
		super(NextBigWhatSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()

		try:
			title = tree.xpath(".//header[contains(@class, 'entry-header')]/h1/text()")
			details = tree.xpath('.//div[contains(@class, "herald-entry-content")]/p/text()')
			
			if title and details:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]

				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = "\t".join([item.strip().encode('ascii','ignore') for item in details if item.strip()])

				img_urls = tree.xpath('.//div[contains(@class, "herald-post-thumbnail herald-post-thumbnail-single")]/span/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				meta_result = self.get_meta(tree)

				if 'description' in meta_result:
					news_item['blurb'] = meta_result['description']

				return news_item

		except:
			pass
		return None
