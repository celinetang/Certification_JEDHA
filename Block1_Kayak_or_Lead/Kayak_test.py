

villes=["Mont Saint Michel",
"St Malo",
"Bayeux",
"Le Havre",
"Rouen",
"Paris",
"Amiens",
"Lille",
"Strasbourg",
"Chateau du Haut Koenigsbourg",
"Colmar",
"Eguisheim",
"Besancon",
"Dijon",
"Annecy",
"Grenoble",
"Lyon",
"Gorges du Verdon",
"Bormes les Mimosas",
"Cassis",
"Marseille",
"Aix en Provence",
"Avignon",
"Uzes",
"Nimes",
"Aigues Mortes",
"Saintes Maries de la mer",
"Collioure",
"Carcassonne",
"Ariege",
"Toulouse",
"Montauban",
"Biarritz",
"Bayonne",
"La Rochelle"]

import scrapy
import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
import pandas as pd


class BookingSpiderTest(scrapy.Spider):

    locs = villes
    name = "booking"
    init_url = dict()
    start_urls = ["https://www.booking.com/"]


    def parse(self, response):

        for loc in self.locs:

            yield scrapy.FormRequest.from_response(
                response,
                formdata={'ss': loc},
                callback=self.after_search ,
                cb_kwargs = {'location':loc, 'page_no':0}
                )





    def after_search(self, response, location, page_no):

        print(location, page_no, end=' ')
        if page_no == 0:
            self.init_url[location] = response.url

        containers = response.css('div.a826ba81c4.fe821aea6c.fa2f36ad22.afd256fc79.d08f526e0d.ed11e24d01.da89aeb942')

        for container in containers:
            
            try:
                name = container.css('div.fcab3ed991.a23c043802::text').get()
            except:
                print(f"Probleme avec le nom de l'hotel à {location} ")
                name = None

            try:
                url = container.css('a.e13098a59f').attrib['href']
            except:
                print(f"Probleme avec l'url de {name} à {location}")
                url = None
            try:
                description = container.css('div.d8eab2cf7f::text').get()
            except:
                print(f"Probleme avec la description de {name} à {location}")
                description = None
            try:
                score = float(container.css('div.b5cd09854e.d10a6220b4::text').get())
            except:
                score = None
                print(f"Probleme avec le score de {name} à {location}")

            dic= {'location' : location,
                   'url' : url,
                   'name' : name,
                   'score' : score,
                   'description' : description}
            try:
                yield response.follow(url=url, callback=self.parse_hotel, cb_kwargs = {'dic':dic})
            except:
                print(f'\n getting to {name}, {location} webpage did not work')
                dic['lat']=None
                dic['lon']=None
                yield dic
            
            
        if page_no<=1:
            next_page = self.init_url[location]+"&offset="+str(25*(page_no+1))
            yield  response.follow(next_page, callback=self.after_search, cb_kwargs = {'location':location, 'page_no':page_no+1})
        
        
    def parse_hotel(self, response, dic): #uniquement pour récupérer les coordonnées GPS
        try:
            ll = response.css('a#hotel_sidebar_static_map').attrib['data-atlas-latlng']
        except:
            print("mais pas réussi à récupérer le selecteur")
            dic['lat']=None
            dic['lon']=None
            yield dic
            return None
        try:
            ll = ll.split(',')
            dic['lat'] = float(ll[0])
            dic['lon'] = float(ll[1])
            yield dic
        except:
            print("mais pas réussi à séparer latitude et longitude")
            dic['lat']=None
            dic['lon']=None
            yield dic

filename = "booking_results.json"

if filename in os.listdir('.'):
    os.remove(filename)
    

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        filename : {"format": "json"},
    }
})

process.crawl(BookingSpiderTest)
process.start()

