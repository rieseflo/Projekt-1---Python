# new terminal, cd spider
# scrapy crawl tutti -O file.jl

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SpiderItem
from scrapy.loader import ItemLoader
from urllib.parse import urljoin

class MarketplaceSpider(CrawlSpider):
    name = 'tutti'
    start_urls = []
    base_url = "https://www.tutti.ch/de/q/autos/Ak8CkY2Fyc5TAwMDA?sorting=newest&page="
    for page_num in range(1, 101):
        url = base_url + str(page_num)
        start_urls.append(url)

    rules = (
        Rule(LinkExtractor(allow=r'fahrzeuge/autos'), callback='parse_item', follow=True),  
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)    
        l.add_xpath("price", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Preis CHF")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("zip", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "PLZ")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("km", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Kilometerstand")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("first_registration", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Erstzulassung")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("aufbau", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Aufbau")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("marke", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Marke")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("modell", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Modell")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("türen", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Türen")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("farbe", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Farbe")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("treibstoff", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Treibstoff")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("getriebeart", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Getriebeart")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')
        l.add_xpath("leistung", '//dt[span[@class="MuiTypography-root MuiTypography-body2 ecqlgla2 mui-style-x1ihqf" and contains(text(), "Leistung")]]/following-sibling::dd/span[@class="MuiTypography-root MuiTypography-body1 ecqlgla1 mui-style-op0mwp"]')

        yield l.load_item()