from urllib import response
import scrapy
import calendar

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
        # Select the <div class="artText"> from the page
        art_text = response.xpath('//div[@class="artText"]//text()').getall()
        if art_text:
            # Join and clean the text similar to get_text(separator='\n', strip=True)
            clean_text = '\n'.join([line.strip() for line in art_text if line.strip()])
            self.logger.info(f"Extracted content from {response.url}")
        
            # Or yield it as an item
            yield {
                'url': response.url,
                'text': clean_text
            }