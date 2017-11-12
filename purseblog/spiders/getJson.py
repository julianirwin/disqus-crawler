# coding=utf-8
import scrapy

# Imports needed for talking to the Splash API
import json
from scrapy.http.headers import Headers

# Define the Splash API endpoint
RENDER_HTML_URL = "http://localhost:8050/render.html"


class JsonGrabberSpider(scrapy.Spider):
    name = "json_grabber"

    # the crawler takes an URL in input
    # this URL is the output of the UrlGrabberSpider in getDisqusUrl.py
    def __init__(self, url):
        self.start_urls = [url]

    # We use scrapy to and the Xpath syntax to extract information
    # We then store this inforamatino in a file called thread.json
    def parse(self, response):
        json = response.xpath("//script[@id='disqus-threadData']/text()").extract()[0]
        # Other ways of getting the same information would be:
        # response.xpath("//iframe[@title='Disqus']")
        # response.xpath("//iframe[contains(@id,'dsq')]")

        filename = 'thread.json'
        with open(filename, 'wb') as f:
            f.write(bytes(json, 'utf-8'))
