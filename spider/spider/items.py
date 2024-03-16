# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags
import re

def clean_price(text):
    # Use regular expression to extract only digits
    cleaned_text = re.sub(r'\D', '', text)
    return cleaned_text

class SpiderItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst(),
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price), 
        output_processor=TakeFirst(),
    )
    zip = scrapy.Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst(),
    )
    km = scrapy.Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst(),
    )
    first_registration = scrapy.Field(
        input_processor=MapCompose(remove_tags), 
        output_processor=TakeFirst(),
    )
    pass
