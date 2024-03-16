# crawl gpx spider, limit to 10 and store output in json line format file
# new terminal, cd spider
# scrapy crawl tutti -o file.json -s CLOSESPIDER_PAGECOUNT=100

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SpiderItem
from scrapy.loader import ItemLoader
import re

class MarketplaceSpider(CrawlSpider):
    name = 'tutti'
    start_urls = ['https://www.tutti.ch/de/q/motorraeder/Ak8CrbW90b3JjeWNsZXOUwMDAwA?sorting=newest&page=1']

    rules = (
        Rule(LinkExtractor(allow=(r"page=",))),
        Rule(LinkExtractor(allow=(r"fahrzeuge/motorraeder",)), callback='parse_item'),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)    
        l.add_css("title", "h1.MuiTypography-root.MuiTypography-h5.mui-style-18teqp8")
        l.add_xpath("description", '//div[contains(@class, "MuiBox-root") and contains(@class, "mui-style-znb5ut")]/span[contains(@class, "MuiTypography-root") and contains(@class, "MuiTypography-body1") and contains(@class, "ecqlgla1") and contains(@class, "mui-style-nthajo")]')
        l.add_xpath("price", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Preis CHF")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("zip", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "PLZ")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("km", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Kilometerstand")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("first_registration", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Erstzulassung")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        
        return l.load_item()