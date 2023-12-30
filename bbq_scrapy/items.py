# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


def serialize_category_list(value):
    value = list(set(value))
    return value

class BbqMenuItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    price = scrapy.Field()
    category_list = scrapy.Field(serializer = serialize_category_list)
    origin_dict = scrapy.Field()
    nutritions_dict = scrapy.Field()
    allergy = scrapy.Field()


class BbqEventItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    event_duration = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    event_active = scrapy.Field()
    content_img = scrapy.Field()


class BbqSideItem(scrapy.Item):
    side_title = scrapy.Field()
    side_contents = scrapy.Field()


class EachSideItem(scrapy.Item):
    menu_title = scrapy.Field()
    menu_side_options = scrapy.Field()