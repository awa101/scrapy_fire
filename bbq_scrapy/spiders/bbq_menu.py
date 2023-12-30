import scrapy
from bbq_scrapy.items import BbqMenuItem, BbqSideItem, EachSideItem
from scrapy.http import Request
from scrapy.selector import Selector



class BbqMenuSpider(scrapy.Spider):
    name = "bbq_menu"
    allowed_domains = ["bbq.co.kr"]
    all_options = []

    custom_settings = {
        'ITEM_PIPELINES': {'bbq_scrapy.pipelines.BbqMenuPipeline': 300},
    }


    def start_requests(self):
        url = 'https://bbq.co.kr/categories/1'
        yield Request(url, callback=self.parse) 

    def parse(self, response):
        urls = response.css('a.ProductCard__Wrapper-sc-1jkf5kq-0')
        for url in urls:
            detail_url = 'https://bbq.co.kr/' + url.css('::attr(href)').get()

            yield response.follow(detail_url, callback=self.parse_detail_menu)

        # category for pagenation
        current_category = int(response.url.split('/')[-1])
        next_category = current_category + 1


        # if next_category <= 14:
        if next_category <= 14:
            next_category_url = f'https://bbq.co.kr/categories/{next_category}'
            yield response.follow(next_category_url, callback=self.parse)



    def parse_detail_menu(self, response):

        menu_item = BbqMenuItem()
        modal_html = response.css('div.Flex__Wrapper-sc-1q3w46z-0.gtfiHP').get()
        modal_selector = Selector(text=modal_html)
        origin_dict, nutritions_dict, allergy = self.parse_detail_modal(modal_selector)
        menu_title = response.css("span.Text__Wrapper-sc-14360qc-0.xllYV::text").get()
        
        menu_item['url'] = response.url
        menu_item['title'] = menu_title
        menu_item['content'] = response.css("span.Text__Wrapper-sc-14360qc-0.kDWWaz::text").get()
        menu_item['price'] = response.css("span.Text__Wrapper-sc-14360qc-0.lcdMRs::text").get()
        menu_item['category_list'] = response.css("div.Box__Wrapper-sc-19le4xr-0.bgDkHx span.Text__Wrapper-sc-14360qc-0.hhayAA::text").getall()
        menu_item['origin_dict'] = origin_dict
        menu_item['nutritions_dict'] = nutritions_dict
        menu_item['allergy'] : allergy

        yield menu_item


        side_item = BbqSideItem()
        each_side_list = []
        each_menus_option = {}
        side_lists = response.css('div.Flex__Wrapper-sc-1q3w46z-0.jKkTgb')
        half_length = len(side_lists) // 2 
        for side_list in side_lists[:half_length]: 
            side_list_name = side_list.css('span.Text__Wrapper-sc-14360qc-0.ebQsIh::text').get()
            
            if side_list_name:
                print(side_list_name)
                each_side_list.append(side_list_name)

                if side_list_name not in self.all_options:
                    self.all_options.append(side_list_name)
                    side_contents = side_list.css('span.Text__Wrapper-sc-14360qc-0.kFmnIk::text').getall()
                    side_options = [content for content in side_contents if not content.startswith('최대')]
                    each_menus_option[side_list_name] = side_options

        for side_title, side_contents in each_menus_option.items():
            side_item = BbqSideItem()
            side_item['side_title'] = side_title
            side_item['side_contents'] = side_contents

            yield side_item

        # EachSideItem에 각 메뉴별 옵션 저장
        each_side_item = EachSideItem()
        each_side_item['menu_title'] = menu_title
        each_side_item['menu_side_options'] = each_side_list

        yield each_side_item




    def parse_detail_modal(self, modal_selector):
        # 원산지
        origin_dict = {}
        origin_titles = modal_selector.css('span.Text__Wrapper-sc-14360qc-0.kFmnIk::text').getall()
        origin_contents = modal_selector.css('span.Text__Wrapper-sc-14360qc-0.hhayAA::text').getall()

        if len(origin_titles) == len(origin_contents):
            for i in range(len(origin_titles)):
                origin_key = origin_titles[i].split()[-1] if origin_titles[i] else None
                origin_value = origin_contents[i] if origin_contents[i] else None
                if origin_key and origin_value:
                    origin_dict[origin_key] = origin_value

        # 영양 정보
        nutritions_dict = {}
        nutrition_facts = modal_selector.css("div.Box__Wrapper-sc-19le4xr-0.fzZzcY")
        for nutrition in nutrition_facts:
            title = nutrition.css("span.Text__Wrapper-sc-14360qc-0.cpMrXG::text").get()
            amount = nutrition.css("span.Text__Wrapper-sc-14360qc-0.kvZCDa::text").get()
            if title and amount:
                nutritions_dict[title] = amount

        # 알레르기 정보
        allergy = modal_selector.css('span.Text__Wrapper-sc-14360qc-0.kDWWaz::text').get()

        return origin_dict, nutritions_dict, allergy
    
