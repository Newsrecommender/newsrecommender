"""
This file collects news_feeds from various sites
After collecting these feeds, each feed will be cleaned(removal of unnecessary text), tokenized and stemmed and stored in ES, which is commented as of now
self.news_sources : all the URLs of different news websites, this can be stored in a file and then fetched. We can also setup a cron job to do the same..
server_addr : ES server address - Will be localhost once elastic search is installed
All feeds are collected as RSS/XMLS's
"""


import feedparser as fp
from nltk import RegexpTokenizer
#from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import re
#from elasticsearch import Elasticsearch, helpers
#We should ideally copy the data to Elastic search, so that data can be fetched and worked upon.. COmmented it as of now.
#es = Elasticsearch(server_addr, timeout=300)

#Cretion of class, which will house related functions for news words by news links...
class NewsArticles(object):

	def __init__(self):	
		self.tokenizer = RegexpTokenizer(r'[a-zA-Z_]+')
		#self.p_stem = PorterStemmer()
		self.p_stem = SnowballStemmer("english")
		self.news_sources ={"News": ["http://timesofindia.indiatimes.com/rssfeeds/5880659.cms", "http://www.economist.com/sections/science-technology/rss.xml"]}
	
	def nlp_clean(self, document):
		new_doc = re.sub(r"<.*?>", "", document)
		tokens = self.tokenizer.tokenize(new_doc)
		new_tokens = [self.p_stem.stem(tok.lower()) for tok in tokens if tok not in stopwords.words('english')]
		return new_tokens

	def collect_news(self):
		news_articles = {}
		for domain in self.news_sources.keys():
			news_id = 0
			for url in self.news_sources[domain]:
				d = fp.parse(url)
				#print(d)
				for post in d.entries:
					#Below steps will produce set of words, which will later be concatenated as value for news_article dictionary
					title = self.nlp_clean(post["title"])
					print(post["summary"])
					summary = self.nlp_clean(post["summary"])
					link = post["link"]
					news_articles[(domain, url, link, news_id)] = title + summary 
					news_id += 1
		#print(news_articles)
		actions = []
		for news in news_articles.keys():
			action = {
				"_op_type" : "create",
				"_index" : "news_collection",
				"_type" : "feeds",
				"_source" : {
					"news_dom" : news[0],
					"news_rss" :news[1],
					"news_link" : news[2],
					"news_id" : news[3],
					"news_text" : news_articles[news]
				}
			}
			actions.append(action)
			#print(actions)

		#print helpers.bulk(es, actions)
#Creation of object news, which will call __init__ 		
news=NewsArticles()
'''
Call collect_news function, which will collect the news and creates a dictionary
which has type of news, rss link, actual news link, dummy id and content of news, which is broken down into words of importance.
'''
news.collect_news()
