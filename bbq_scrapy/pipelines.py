import pymysql
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter


class BbqScrapyPipeline:
    def process_item(self, item, spider):
        return item

class BbqMenuPipeline:
    def open_spider(self, spider):
        # MySQL 데이터베이스 연결 설정
        self.connection = pymysql.connect(# host='scrapy_fire_db',
                                          user='root',
                                          host='127.0.0.1',
                                          port=3303,
                                          password='bbq_scrapy',
                                          database='bbq_scrapy',
                                          charset='utf8mb4')
        self.cursor = self.connection.cursor()

        # 아래는 .json으로 저장하는 코드
        date = datetime.now().strftime("%Y%m%d")
        self.file_map = {
            'BbqMenuItem': open(f'./data/{date}_bbq_menu.json', 'wb'),
            'BbqSideItem': open(f'./data/{date}_bbq_side.json', 'wb'),
            'EachSideItem': open(f'./data/{date}_each_menu_side.json', 'wb'),
        }
        self.exporter_map = {
            'BbqMenuItem': JsonItemExporter(self.file_map['BbqMenuItem'], encoding='utf-8', ensure_ascii=False),
            'BbqSideItem': JsonItemExporter(self.file_map['BbqSideItem'], encoding='utf-8', ensure_ascii=False),
            'EachSideItem': JsonItemExporter(self.file_map['EachSideItem'], encoding='utf-8', ensure_ascii=False)
        }
        for exporter in self.exporter_map.values():
            exporter.start_exporting()

    def close_spider(self, spider):
        self.connection.commit()
        self.connection.close()

        # 아래는 .json으로 저장하는 코드
        for exporter in self.exporter_map.values():
            exporter.finish_exporting()
        for file in self.file_map.values():
            file.close()

    def process_item(self, item, spider):
        item_class_name = item.__class__.__name__
        if item_class_name == 'BbqSideItem':
            item = self.process_bbq_side_item(item)
        if item_class_name in self.exporter_map:
            self.exporter_map[item_class_name].export_item(item)
        item['created_at'] = datetime.now()
        
        self.save_item_to_db(item)
        return item

    def process_bbq_side_item(self, side_item):
        contents = side_item['side_contents']
        side_dict = {}
        for i in range(0, len(contents), 2):
            if i+1 < len(contents):
                side_dict[contents[i]] = contents[i+1]
        side_item['side_contents'] = side_dict
        return side_item
    
    
    def save_item_to_db(self, item):
        # Menu 테이블에 데이터 저장
        menu_sql = """
            INSERT INTO Menu (url, title, description, price, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(menu_sql, (
            item['url'],
            item['title'],
            item['description'],
            item['price'],
            item['created_at']
        ))
        menu_id = self.cursor.lastrowid

        # Category, MenuCategory 테이블에 데이터 저장
        for category in item['category_list']:
            category_sql = "INSERT INTO Category (category) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)"
            self.cursor.execute(category_sql, (category,))
            category_id = self.cursor.lastrowid
            
            menu_category_sql = "INSERT INTO MenuCategory (menu_id, category_id) VALUES (%s, %s)"
            self.cursor.execute(menu_category_sql, (menu_id, category_id))

        # Nutrition 테이블에 데이터 저장
        nutrition_sql = """
            INSERT INTO Nutrition (menu_id, calories, sugars, protein, fat, sodium) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        nutrition = item['nutritions_dict']
        self.cursor.execute(nutrition_sql, (menu_id, nutrition.get('열량(kcal)'), nutrition.get('당류(g)'),
                                            nutrition.get('단백질(g)'), nutrition.get('포화지방(g)'), nutrition.get('나트륨(mg)')))

        # Origin 테이블에 데이터 저장
        for ingredient, origin in item['origin_dict'].items():
            origin_sql = "INSERT INTO Origin (menu_id, ingredient, origin) VALUES (%s, %s, %s)"
            self.cursor.execute(origin_sql, (menu_id, ingredient, origin))



class BbqEventPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == 'event_duration':
                value = adapter.get(field_name)
                dates = value.replace("이벤트 기간 :", "").strip().split('~')
                if len(dates) == 2:
                    adapter['start_date'] = dates[0].strip()
                    adapter['end_date'] = dates[1].strip()


        del adapter['event_duration']

        return item