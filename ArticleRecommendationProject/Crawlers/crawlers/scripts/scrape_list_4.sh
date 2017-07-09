#!/bin/sh
_now=$(date +"%m_%d_%Y_%H_%M_%S")

PATH=$PATH:/usr/local/bin
export PATH

cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/nextbigwhat.py -o feeds/nextbigwhat-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/ndtv.py -o feeds/ndtv-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/reuters.py -o feeds/reuters-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/rediffbusiness.py -o feeds/rediffbusiness-$_now.json