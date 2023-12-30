import scrapy
from bbq_scrapy.items import BbqEventItem
from datetime import datetime

class BbqEventSpider(scrapy.Spider):
    name = "bbq_event"
    allowed_domains = ["bbq.co.kr"]
    start_urls = ["https://bbq.co.kr/events"]
    date = datetime.now().strftime("%Y%m%d")

    custom_settings = {
        'ITEM_PIPELINES': {'bbq_scrapy.pipelines.BbqEventPipeline': 300},
        'FEEDS': {
            f'./data/{date}_event.json': {'format': 'json', 'overwrite': True},
        },
    }


    def parse(self, response):
        active_flag = 'finished' not in response.url

        urls = response.css('div.Flex__Wrapper-sc-1q3w46z-0.dDnPwI a')
        for url in urls:
            detail_url = response.urljoin(url.css('::attr(href)').get())
            yield response.follow(detail_url, callback=self.parse_detail_event, cb_kwargs={'active_flag': active_flag})

        if 'finished' not in response.url:
            next_url = self.start_urls[0] + '/finished'
            yield response.follow(next_url, callback=self.parse)


    def parse_detail_event(self, response, active_flag):
        event_item = BbqEventItem()

        event_item['url'] = response.url
        event_item['title'] = response.css("span.Text__Wrapper-sc-14360qc-0.bYHZlv::text").get()
        event_item['event_duration'] = response.css('span.Text__Wrapper-sc-14360qc-0.boCMbS::text')[-1].get()
        event_item['event_active'] = active_flag
        event_item['content_img'] = response.css('div.EventPageTemplate__Article-sc-q1i1ix-2.kdXtS img::attr(src)').get()
        
        yield event_item