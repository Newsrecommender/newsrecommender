import os
from hashlib import md5
from io import BytesIO
from lxml import etree
from datetime import datetime
from scrapy.selector import Selector
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from common import CommonBaseSpider
from crawlers.items import NewsItem


class Tech(CommonBaseSpider):
	name = "tech"
	base_dir = "crawl"
	allowed_domains = ["tech.co"]
	start_urls = (
					"http://tech.co/",
					"http://jobs.tech.co/",
					"http://tech.co/announcements"
					"http://tech.co/breaking-news-2",
					"http://tech.co/business/funding-business",
					"http://tech.co/startups-apps/3d-printing-startups-apps",
					"http://tech.co/startups-apps/ecommerce-startups-apps",
					"http://tech.co/entrepreneur/tips-how-to/marketing-tips-how-to",
					"http://tech.co/cloud-storage-2",
					"http://tech.co/business/ecosystems",
					"http://tech.co/startups-apps/mobile",
					"http://tech.co/startups-apps/sharing-economy-startups-apps",
					"http://tech.co/entrepreneur/development-design",
					"http://tech.co/technology",
					"http://tech.co/entrepreneur/tips-how-to/productivity-tips-how-to",
					"http://tech.co/wearables-2",
					"http://tech.co/city/atlanta",
					"http://tech.co/city/boston",
					"http://tech.co/city/dc",
					"http://tech.co/city/los-angeles",
					"http://tech.co/city/portland-me",
					"http://tech.co/celebrate-startup-competition",
					"http://tech.co/tech-calendar",
					"http://tech.co/events",
					"http://tech.co/sxsw-events-2016",
					"http://celebrate.tech.co/",
					"http://tech.co/startups-apps/accelerator-startups-apps",
					"http://tech.co/startups-apps/incubator-startups-apps",
					"http://tech.co/entrepreneur/coworking-spaces-entrepreneur",
					"http://tech.co/business/jobs-in-tech",
					"http://tech.co/startups-apps/hackathon",
					"http://tech.co/business/books",
					"http://tech.co/startups-apps/productivity",
		)
	rules = (
		Rule(LinkExtractor(
			allow=(r'http:\/\/tech.co\/.+'),),
			callback='parse_item', 
			follow=False),
	)

	def parse_item(self, response):
		filedir = self.pre_write_check()
		filename = os.path.join(filedir, md5(response.url).hexdigest())
		with open(filename, "wb") as html:
			html.write(response.body)
		htmlparser = etree.HTMLParser()
		tree = etree.parse(BytesIO(response.body), htmlparser)

		news_item = NewsItem()
		try:   
			title = tree.xpath(".//div[contains(@class,\"large-12 columns article-title\")]//h1//text()")																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																
			details = tree.xpath('//html/body/div/div/article/div//p//text()')
			if title and details:
				news_item['title'] = title[0].strip().encode('ascii','ignore')  
				details =  [ele.strip().encode('ascii','ignore') for ele in details]
				news_item['details'] = "\t".join(details)
						  
				img_urls = tree.xpath('.//img[contains(@class,\"article-hero-img\")]/@src')

				if img_urls:
					news_item['img_urls'] = get_stripped_list(img_urls)

				cover_image = tree.xpath('.//img[contains(@class,\"article-hero-img\")]//img/@src')
				if cover_image:
					news_item['cover_image'] = cover_image

				news_item['source'] = self.name
				news_item['crawled_date'] = datetime.now()
				news_item['source_url'] = response.url.split('?')[0]
				author = tree.xpath(".//div[contains(@class,\"author\")]/h4/a/text()")
				news_item['author'] = author
				published_date = tree.xpath(".//div[contains(@class,\"datetime\")]/h2/span/text()")
				news_item['published_date'] = published_date
				news_item['tags'] = tree.xpath(".//div[contains(@class,\"tags\")]//a/text()")
				meta_result = self.get_meta(tree)

				if 'og:image' in meta_result:
					news_item['cover_image'] = meta_result['og:image']

				if 'og:description' in meta_result:
					news_item['blurb'] = meta_result['og:description']
					news_item['blurb'] = news_item['blurb'].strip().encode('ascii','ignore') 
					
				return news_item
		except:
			pass
		return None
