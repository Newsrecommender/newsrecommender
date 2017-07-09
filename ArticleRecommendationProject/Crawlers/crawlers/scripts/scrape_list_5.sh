#!/bin/sh
_now=$(date +"%m_%d_%Y_%H_%M_%S")

PATH=$PATH:/usr/local/bin
export PATH

cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smallbiztrends.py -o feeds/smallbiztrends-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smechannels.py -o feeds/smechannels-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smetimes.py -o feeds/smetimes-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/yourstory.py -o feeds/yourstory-$_now.json
