import os
from datetime import datetime
from hashlib import md5
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

def get_stripped_list(data):
	if data:
		return [d.strip() for d in data if d.strip()]
	return []

class CommonBaseSpider(CrawlSpider):
	base_dir = "crawl"
	allowed_meta_properties = ["og:description", "og:image", "description","og:updated_time"]


	def get_meta(self, tree):
		"""
		This method iterates over meta tags and extracts images
		and other details
		"""
		result = {}

		for meta in tree.findall(".//meta"):
			for attribute in meta.attrib:
				if attribute == "property" and meta.attrib[attribute] in self.allowed_meta_properties:
					result[meta.attrib[attribute]] = meta.attrib['content']
		return result

	def pre_write_check(self):
		"""
		This method is used to check if necessary directories exists before
		writing html files
		"""
		if not os.path.exists(self.base_dir):
			os.mkdir(self.base_dir)

		source = os.path.join(self.base_dir, self.name)
		if not os.path.exists(source):
			os.mkdir(source)
		return source

	def parse_item(self, response):
		filedir = self.pre_write_check()
		if response.url:
			filename = os.path.join(filedir, md5(response.url.split('?')[0]).hexdigest())
		else:
			return None

		## if HTML file is already saved then skip storing it.
		if not os.path.exists(filename):
			with open(filename, "wb") as html:
				html.write(response.body)
				print (10*"="),"Saved file {0}".format(filename)
		else:
			print (10*"="),"Skipped file {0}".format(filename)

