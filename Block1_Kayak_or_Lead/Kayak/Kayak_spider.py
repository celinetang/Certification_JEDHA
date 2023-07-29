import os 
import logging
import scrapy
from scrapy.crawler import CrawlerProcess

class BookingSpider(scrapy.Spider):
    # Name of your spider
    name = "booking"

    # Starting URL
    start_urls = ['https://www.booking.com/']

    # Parse function for input of destination and dates
    
    def parse(self, response):
        # FormRequest used to login
        return scrapy.FormRequest.from_response(
            response,
            formdata={'search': 'Marseille', 'dates': '31/05/2023'},
            callback=self.scrape_results
        )
    
    def scrape_results(self, response):
        yield {"hotel_name":response.xpath("/html/body/div[3]/div/div[4]/div[1]/div[1]/div[4]/div[2]/div[2]/div/div/div[3]/div[4]/div[1]/div[2]/div/div[1]/div/div[1]/div/div[1]/div/h3/a/div[1]/text()").get()}

            
# Name of the file where the results will be saved
filename = "Paris.json"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('src/'):
        os.remove('src/' + filename)

# Declare a new CrawlerProcess with some settings
## USER_AGENT => Simulates a browser on an OS
## LOG_LEVEL => Minimal Level of Log 
## FEEDS => Where the file will be stored 
## More info on built-in settings => https://docs.scrapy.org/en/latest/topics/settings.html?highlight=settings#settings
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename: {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(BookingSpider)
process.start()