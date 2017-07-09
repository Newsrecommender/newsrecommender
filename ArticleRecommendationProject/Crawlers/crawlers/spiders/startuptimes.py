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
		"Industries": [],
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
		"Investment" : ["http://www.startuptimes.in/search/label/Funding"],
		"Startups": ["http://startuptimes.in/",]
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


class StartupTimesSpider(CommonBaseSpider):
	name = "startuptimes"
	base_dir = "crawl"
	allowed_domains = ["startuptimes.in"]
	urls = [filter(None,item['subcategory'].values()) for item in categories if filter(None,item['subcategory'].values())]
	urls = sum(sum(urls, []), []) ## i.e. similar to [item for sublist in urls for subsublist in sublist for item in subsublist]
	start_urls = urls
	rules = (
		Rule(SgmlLinkExtractor(
			allow=(r'http\:\/\/www\.startuptimes\.in\/\d{4}\/\d{2}\/.+'),
			deny = (r'http\:\/\/www\.startuptimes\.in\/search\/label\/interview\/.+',r'http\:\/\/www\.startuptimes\.in\/\d{4}\/\d{2}\/(post-startup-pitch.html|advertise-on-startuptimes.html|post-startup-jobs-for-free.html|startup-forums-live-india.html|advertise-your-startup-for-rs-100.html|active-polls-on-startuptimesin.html|active-polls-on-startuptimesin.html|freedom-251-buisness-model.html|press-release-startups-submit.html|ambani-son-before-after-pics-how-did-he.html|interns-wanted-for-media.html|startup-founders-request-for-interview.html)'),),
			callback='parse_item',
			follow=True),
	)
	def parse_item(self, response):

		deny_xpaths = ['http://4.bp.blogspot.com/-chhNLDME0Yo/VZw_4EpmQ1I/AAAAAAAANcE/8WKzyR2Dhh8/s640/startup%2Breport%2Bindia.png',
		'http://3.bp.blogspot.com/-0GSnIzmvK84/UhtWvbUmd7I/AAAAAAAAFco/8rFc-kLEt0c/s1600/martjack+logo+st.gif',
		'http://4.bp.blogspot.com/-OeT3NW9TP1U/VgxZe7EgYCI/AAAAAAAAPSs/-zPCdu_ayZg/s1600/peppertap.jpg',
		'http://3.bp.blogspot.com/-lVFGg8e2EyA/UhgPxpABqdI/AAAAAAAAFX0/BaOb_gHYLCI/s1600/bigbasket.com+logo.png',
		'http://4.bp.blogspot.com/-KTNZQPHscyE/VjPvqSZgK9I/AAAAAAAAP4U/mAqBIH6ljr0/s320/advertise%2Bwith%2Bstartuptimes.png',
		'http://2.bp.blogspot.com/-ZBwO4Q4XxZc/VkLhwiuEPfI/AAAAAAAAQHk/CJALT6xKiks/s1600/ecommerce%2Breport%2Bindia%2B2025.png',
		'https://1.bp.blogspot.com/-X0_bk4Fw4LM/Vw2L0J3gCTI/AAAAAAAAR88/qrczkABYY9wZFX0Pyqkf9ty-ltc270DhgCLcB/s640/ambani%2Bson%2Bbefore%2Bafter%2Bpics.png',
		'http://1.bp.blogspot.com/-3a0VWriQezs/Ued5D94B7yI/AAAAAAAAEjU/kouuhO17mVA/s320/Startups+Request+for+Interview.png']

		super(StartupTimesSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:

			title = tree.xpath(".//h3[@class=\"post-title entry-title\"]/a/text()")
			details = tree.xpath('.//div[@dir=\'ltr\']/text()[preceding-sibling::br and following-sibling::br]')
			if title and details:
				print self.name,"namee"
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				news_item['details'] = '\t'.join([item.strip().encode('ascii','ignore').decode('unicode_escape') for item in details if item.strip()])
				
				img_urls = tree.xpath('.//div[contains(@style,\'center\')]/a/img/@src')
				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)
					news_item['cover_image'] = img_urls[0]

				meta_result = self.get_meta(tree)

				if 'description' in meta_result:
					news_item['blurb'] = meta_result['description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				## TODO
				## author, tags, published_date

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

