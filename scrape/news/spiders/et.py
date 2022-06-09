from urllib import response
import scrapy
import calendar
import re
from scrapy import Selector

class ETSpider(scrapy.Spider):
    name = "et"
    
    def start_requests(self):
        uri_month = "https://economictimes.indiatimes.com/archive/"
        uri_day = "https://economictimes.indiatimes.com/archivelist/"
        years = ["2022"]
        months = ["1", "2", "3", "4", "5"]
        start = 44562
        
        month_urls = []
        day_urls = []
        for year in years:
            for month in months:
                month_urls.append(uri_month + "year-%s,month-%s.cms" % (year, month))
                max_days = calendar.monthrange(int(year), int(month))[1]
                for i in range(1, max_days+1):
                    day_urls.append(uri_day + "year-%s,month-%s,starttime-%s.cms" % (year, month, start))
                    start = start + 1
                    
        for url in day_urls:
            yield scrapy.Request(url=url, callback=self.parse_url)


    def parse_url(self, response):
        # Select <ul class="content"> and extract hrefs
        links = response.xpath('//ul[@class="content"]//a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_item)
    
    
    def parse_item(self, response):
        # Process the individual news item
       
        # Step 1: Get the raw HTML of the <div class="artText">
        art_div_html = response.xpath('//div[@class="artText"]').get()

        if art_div_html:
            # Step 2: Remove <style>...</style> using regex
            # This removes entire <style> tags and their content (non-greedy match)
            cleaned_html = re.sub(r'<style.*?>.*?</style>', '', art_div_html, flags=re.DOTALL | re.IGNORECASE)

            # Step 3: Create a new selector from the cleaned HTML
            selector = Selector(text=cleaned_html)

            # Step 4: Extract and clean all text
            text_parts = selector.xpath('//text()').getall()
            clean_text = '\n'.join([t.strip() for t in text_parts if t.strip()])

            yield {
                'url': response.url,
                'text': clean_text
            }

            self.logger.info(f"Cleaned and extracted text from {response.url}")
