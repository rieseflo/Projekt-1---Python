# new terminal, cd spider
# scrapy crawl tutti -o file.json

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SpiderItem
from scrapy.loader import ItemLoader

class MarketplaceSpider(CrawlSpider):
    name = 'tutti'
    allowed_domains = ['tutti.ch']
    start_urls = ["https://www.tutti.ch/de/q/motorraeder/Ak8CrbW90b3JjeWNsZXOUwMDAwA?sorting=newest&page=1"]

    rules = (
        Rule(LinkExtractor(allow=r'fahrzeuge/motorraeder'), callback='parse_item', follow=True),  
        Rule(LinkExtractor(allow=r'page=\d+'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)    
        l.add_css("title", "h1.MuiTypography-root.MuiTypography-h5.mui-style-18teqp8")
        l.add_xpath("description", '//div[contains(@class, "MuiBox-root") and contains(@class, "mui-style-znb5ut")]/span[contains(@class, "MuiTypography-root") and contains(@class, "MuiTypography-body1") and contains(@class, "ecqlgla1") and contains(@class, "mui-style-nthajo")]')
        l.add_xpath("price", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Preis CHF")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("zip", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "PLZ")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("km", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Kilometerstand")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
        l.add_xpath("first_registration", '//dt[contains(span/@class, "ecqlgla2") and contains(span/text(), "Erstzulassung")]/following-sibling::dd/span[contains(@class, "ecqlgla1")]')
                
        yield l.load_item()
