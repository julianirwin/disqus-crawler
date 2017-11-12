# coding=utf-8
import scrapy

# Imports needed for talking to the Splash API
import json
from scrapy.http.headers import Headers
from urllib.parse import quote
import re

# Define the Splash API endpoint
RENDER_HTML_URL = "http://localhost:8050/render.html"


DISQUS_BASE_URL = ("https://disqus.com/embed/comments/?"
                   "base=default&"
                   "f=breitbartproduction&"
                   "t_i={id}&"
                   "t_u={url}&"
                   "s_o=default#version=fdcca7a38a395b6f606790b81e4f3d0d")


class UrlGrabberSpider(scrapy.Spider):
    name = "url_grabber"

    # the crawler takes an URL in input
    # so we put that in the initializer
    def __init__(self, url):
        self.start_urls = [url]

    # We call the Splash API as a middleware
    # to render the desired URL
    # In this casse we don't want the page to render all the javascript
    # So we set the js_enabled parameter to False
    def start_requests(self):
        for url in self.start_urls:
            body = json.dumps({"url": url, "wait": 0.5, "js_enabled": False })
            headers = Headers({'Content-Type': 'application/json'})
            yield scrapy.Request(RENDER_HTML_URL, self.parse, method="POST",
                                 body=body, headers=headers)

    # Then, as a callback from the Splash request,
    # we actually use scrapy and the Xpath syntax to extract information.
    # We then store this information into a file called url.txt
    def parse(self, response):
        iframe = response.xpath("//iframe[contains(@src,'http://disqus.com') "
                                "or contains(@src,'https://disqus.com')]")
        # iframe = response.xpath("//iframe[
        # Other ways of getting the same information would be:
        # response.xpath("//iframe[@title='Disqus']")
        script_text = response.xpath('//div[@id="MainW"]/script').extract()[0]
        disqus_id = self._disqus_id_from_script(script_text)
        disqus_url = self._disqus_url_from_script(script_text)
        enc_disqus_url = quote(disqus_url)
        url = self._build_disqus_url(disqus_id, disqus_url)
        # import pdb; pdb.set_trace()
        # response.xpath("//iframe[contains(@id,'dsq')]")
        # url = iframe.xpath("@src").extract()[0]

        # Output to a file
        filename = 'url.txt'
        with open(filename, 'wb') as f:
            f.write(bytes(url, 'utf-8'))
    
    def _build_disqus_url(self, article_id, article_url):
        return DISQUS_BASE_URL.format(id=article_id, url=article_url)

    def _disqus_id_from_script(self, script_text):
        pat = "disqus_identifier\s*=\s*'(\d+)'"
        return re.search(pat, script_text).groups()[0]

    def _disqus_url_from_script(self, script_text):
        pat = "disqus_url\s*?=\s*'(.*)'"
        return re.search(pat, script_text).groups()[0]
