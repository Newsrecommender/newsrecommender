import os
from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from common import CommonBaseSpider
from crawlers.items import NewsItem


class MashableSpider(CommonBaseSpider):
	name = "mashable"
	base_dir = "crawl"
	allowed_domains = ["mashable.com"]
	start_urls = (
					"http://mashable.com/",
					"http://mashable.com/videos/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/social-media/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/tech/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/business/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/entertainment/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/world/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/lifestyle/?utm_cid=mash-prod-nav-ch",
					"http://mashable.com/tech/",
					"http://mashable.com/social-media/",
					"http://mashable.com/business/",
					"http://mashable.com/entertainment/#",
					"http://mashable.com/world/",
					"http://mashable.com/lifestyle/",
					"http://mashable.com/watercooler/",
					"http://shop.mashable.com/?utm_source=mashable&utm_medium=nav",
		)

	rules = (
		Rule(LinkExtractor(
			allow=(r'http\:\/\/mashable.com\/\d{4}\/\d{2}\/\d{2}\/.+'),),
			callback='parse_item',  follow=False),
	)

	def parse_item(self, response):
		super(MashableSpider, self).parse_item(response)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:
			title = tree.xpath("//h1[contains(@class,\'title\')]//text()")
			details = tree.xpath('//div[contains(@class,"post-text")]/p//text()')
			detail = tree.xpath('//section[contains(@class,"article-content blueprint")]//p//text()')
			if title and details or detail:
				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				news_item['title'] = title[0].strip().encode('ascii','ignore')
				if details :
					news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in details])
				if detail :
					news_item['details'] = "\t".join([ele.strip().encode('ascii','ignore') for ele in detail])


				img_urls = tree.xpath('//div[contains(@id,"post-content")]//img/@src')

				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				cover_image = tree.xpath('//div[contains(@id,"post-content")]//img/@src')
				if cover_image:
					news_item['cover_image'] = cover_image

				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore')

				author = tree.xpath('//span[contains(@class,"author_name")]/a/text()')
				if author:
					news_item['author'] = author

				tags = tree.xpath('//footer[contains(@class,"article-topics")]/a/text()')
				if tags:
					news_item['tags'] = tags

				return news_item
		except:
			pass
		return None
