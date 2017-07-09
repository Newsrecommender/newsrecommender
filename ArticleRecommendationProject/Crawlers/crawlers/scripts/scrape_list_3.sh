#!/bin/sh
_now=$(date +"%m_%d_%Y_%H_%M_%S")

PATH=$PATH:/usr/local/bin
export PATH


cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/huffingtonpost.py -o feeds/huffingtonpost-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/iamwire.py -o feeds/iamwire-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/vccircle.py -o feeds/vccircle-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/moneycontrol.py -o feeds/moneycontrol-$_now.json