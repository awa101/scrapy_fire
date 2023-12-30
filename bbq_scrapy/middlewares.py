from time import sleep
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class SeleniumMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        try:
            options = Options()
            options.add_argument("--headless")  
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Set the path to geckodriver
            geckodriver_path = '/mnt/c/bbq_scrapy/bbq_scrapy_fire/geckodriver'
            self.driver = webdriver.Firefox(executable_path=geckodriver_path, options=options)
        
        except Exception as e:
            spider.logger.error(f"Error initializing the driver: {e}")

    def spider_closed(self, spider):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def process_request(self, request, spider):
        self.driver.get(request.url)
        sleep(2) 

        if "products" in request.url:
            self.process_detail_page(spider)
        elif "event" in request.url:
            more_event_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'div.Button__Wrapper-sc-vj85hk-0')
            if len(more_event_buttons) > 0:
                self.process_event_page(spider)
        
        body = self.driver.page_source.encode('utf-8')
        return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)

    def process_detail_page(self, spider):
        try:
            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.Flex__Wrapper-sc-1q3w46z-0.jGqnJH")
            modal_element = modal_elements[1]
            modal_element.click()
            sleep(1)  # modal loading..
        except NoSuchElementException:
            spider.logger.error("Modal element not found for modal.")

    def process_event_page(self, spider):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        more_event = self.driver.find_element(By.CSS_SELECTOR, 'div.Button__Wrapper-sc-vj85hk-0')
        more_event.click()
        sleep(2)



# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class BbqScrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BbqScrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
