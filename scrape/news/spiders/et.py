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
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)