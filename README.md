# News recommendations system
* News services are constantly looking for ways to increase readership, and in turn improved contribution margin
* One way to improve readership is to recommend news articles specific to a tastes or preferences of users.
* Improved readership can be used to generate higher per unit rates for advertising

There are different folders in the project folder:

**1**. **CrawlerDiffWays** : This folder contains 2 files, which we have tried to scrape the content of an article from the news sites.

Wefound step 2, a better source of information for real time, reason being that many a times rss/xml feeds are older than a day, but it depends on different news sites.

**a**. **News\_streamer.py** –This file collects news\_feeds from various sites.

After collecting these feeds, each feed will be cleaned(removal of unnecessary text), tokenized and stemmed and stored in Elasticsearch, which is commented as of now(out of scope as of now)

self.news\_sources : all the URLs of different news websites, this can be stored in a file and then fetched. We can also setup a cron job to do the same..

server\_addr : ES server address - Will be localhost once elastic search is installed

All feeds are collected as RSS/XMLS&#39;s.

**b**. **Web crawler News.py –** This file contains article information from a specific news site, Business standard in our example. Every news site has a different site structure. Thus every site will have its own scraper which needs to be written.

**       **

**2**. **Crawlers** – Once we did the above test and wrote our own set of code. We were able to understand the scrapers that were written by the company. This folder has some sample code of how the scraper was actually written.

Also This folder has many subfolders explained below:

**a**. **Scripts** : It contains scripts which are called from a cronjob, which accumulates the data output(json) of all scrapers(in folder -&gt; spiders).
**b**. **Spiders** : It has all individual news site scraper.
**c**. **Et.json** : Example of how the json looks like.



**3**. **Exploratory analysis** – This folder has an excel file, which contains summary level charts, which gives EDA.

**a**. 20170518\_eda\_summary\_charts: This file has all the summary level charts that we have created by analyzing news articles from **data.json,** which is one day&#39;s worth of scraped articles data(Got it form the company)

**4**. **Data** – This folder contains, what we have extracted, from a **data.json(**this is not attached as it was a 2 GB file**)**file which we got from the company after 1 day&#39;s job was run for all news sites. In addition to that we also got the below set of files.

**a.** DataExtractJSON.py**: We were extracting the data from data.json and putting it to a data frame. So that sample files could be created with features which we want.
**b.** Title\_and\_article1000.csv**: This is a sample file given by the company to use, so that we could run our content and collaborative based algorithms on it.
**c.** TrainSet700\_User\_Ratings**: This is what we have created after giving ratings to each and every of 1000 sample articles. We further broke it down to 700 and 300 articles as train and testing samples respectively.
**d.** User\_Ratings\_Compile**: This file is a conglomeration of all ratings given by 5 users. This is used for Collaborative recommendation technique.

**5**. **Recommendation –** This folder contains code for Content based and Collab based recommendation techniques.

**a**. **Collab_Content_Based.py:** Code written for Collaborative recommendation technique. This takes **User\_Ratings\_**** Compile.csv** as an input and gives generates recommendations by finding similiar articles for each of the 1000 articles.
**b**. **Collab_User_Based.py:** Code written for Collaborative recommendation technique. This takes **User\_Ratings\_**** Compile.csv** as an input and generates articles recommendations by finding similiar users preferences.
**c**. **ContentTest.py:**  Code written for Content based recommendation technique. This takes **Title\_and\_article1000.csv**  as an input and gives out an output file, which has each article and 10 articles which are similar to it.

**6**. **OutputFolder\_Recommendations –** This contains all o/p data that we have got from the various recommendation code, present in Recommendation folder.

**a. ContentOutput:** This file is what we have got by running ContentTest.py code.
**b. CollabOutput:** This file is what we have got by running CollabTest.py code.

**7**. **Recommender\_Project\_Presentation.pptx –** This is the ppt that has been created explaining the project.
