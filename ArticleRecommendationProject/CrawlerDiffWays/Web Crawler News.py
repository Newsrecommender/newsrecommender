# -*- coding: utf-8 -*-
"""
Created on Sat May 06 12:46:44 2017

@author: Niranjan/Shwetank
"""
#import the library used to query a website
import urllib2
import requests
import os
import shutil
import json
#import the Beautiful soup functions to parse the data returned from the website

from bs4 import BeautifulSoup

#function to get articles, it accepts url as the input
def get_article_url(url):
	yelp_r = requests.get(url)
	yelp_soup = BeautifulSoup(yelp_r.text, 'html.parser')
	articles_s = yelp_soup.find_all('div',{'class':'article'})
	articles=[]
	for article_s in articles_s:
		inter = article_s.findAll('a')
		for a in inter:
			articles.append(url+a['href']) 
	return articles
			
#function to get article content, it accepts articles as the input, which is a lit of url's
def get_articles(articles):
	article_contents={}
	for article_c_soup in  articles:
		article_1 = requests.get(article_c_soup)
		article_1_soup = BeautifulSoup(article_1.text, 'html.parser')
		article_contents[article_c_soup]=article_1_soup.find_all('p',{'itemscope':'articleBody'})
	return 	article_contents
#getting serialize issue while trying to write data onto json file, still need to debug	
def jdefault(o):
    return o.__dict__

#function to write data in a folder
def wite_to_file(folderName,article_contents):
	try:
		current_path = os.getcwd()
		file_name = os.path.basename("Business_Standard")
		new_path = os.path.join(current_path, folderName, file_name)
		#create the directory if not present
		#if not os.path.exists(os.path.join(current_path, folderName)):
        #	os.makedirs(os.path.join(current_path, folderName))
		with open(new_path, "wb") as output_file:
			print json.dumps(article_contents, default=jdefault)
	except:
		pass



#Steps to get the article contents onto json file, writing the file is currently not working and i am eating up the exception as of now.
articles = get_article_url("http://www.business-standard.com")
article_contents = get_articles(articles)
wite_to_file("news",article_contents)



