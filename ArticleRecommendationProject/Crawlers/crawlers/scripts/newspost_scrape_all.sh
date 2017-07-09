#!/bin/sh
_now=$(date +"%m_%d_%Y_%H_%M_%S")

PATH=$PATH:/usr/local/bin
export PATH

cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/et.py -o feeds/et-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/bloomberg.py -o feeds/bloomberg-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/businessinsider.py -o feeds/businessinsider-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/business-standard.py -o feeds/business-standard-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/dealcurry.py -o feeds/dealcurry-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/entrepreneur.py -o feeds/entrepreneur-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/forbesindia.py -o feeds/forbesindia-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/gigaom.py -o feeds/gigaom-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/huffingtonpost.py -o feeds/huffingtonpost-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/iamwire.py -o feeds/iamwire-$_now.json
wait
# cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/mashable.py -o feeds/mashable-$_now.json
# wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/moneycontrol.py -o feeds/moneycontrol-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/nextbigwhat.py -o feeds/nextbigwhat-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/ndtv.py -o feeds/ndtv-$_now.json
wait
# cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/pando.py -o feeds/pando-$_now.json
# wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/reuters.py -o feeds/reuters-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/rediffbusiness.py -o feeds/rediffbusiness-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smallbiztrends.py -o feeds/smallbiztrends-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smechannels.py -o feeds/smechannels-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smesector.py -o feeds/smesector-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smetimes.py -o feeds/smetimes-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/smeweb.py -o feeds/smeweb-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/startoholics.py -o feeds/startoholics-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/startuptimes.py -o feeds/startuptimes-$_now.json
wait
# cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/techcrunch.py -o feeds/techcrunch-$_now.json
# wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/thehindu.py -o feeds/thehindu-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/vccircle.py -o feeds/vccircle-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/venturebeat.py -o feeds/venturebeat-$_now.json
wait
cd $HOME/Code/newspost/crawlers/crawlers && $HOME/Installs/envs/newspost/bin/scrapy runspider spiders/yourstory.py -o feeds/yourstory-$_now.json
wait
echo "Scrapnig done successfully on $_now"