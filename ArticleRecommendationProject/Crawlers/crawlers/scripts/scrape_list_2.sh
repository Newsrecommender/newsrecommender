#!/bin/sh
_now=$(date +"%m_%d_%Y_%H_%M_%S")

PATH=$PATH:/usr/local/bin
export PATH

cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/dealcurry.py -o feeds/dealcurry-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/entrepreneur.py -o feeds/entrepreneur-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/forbesindia.py -o feeds/forbesindia-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/gigaom.py -o feeds/gigaom-$_now.json
