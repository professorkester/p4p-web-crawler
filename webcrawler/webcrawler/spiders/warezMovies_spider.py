import scrapy
import sys
import re
from webcrawler.items import WarezbbItem

class WarezbbSpider(scrapy.Spider):
    start_page = 0
    end_page = 100000000 # well...
    name = "warezMovies"

    allowed_domains = ["https://www.warez-bb.org/*"]
    download_delay = 6

    start_urls = [
       "https://www.warez-bb.org/login.php"
    ]
    fail_count = 0
    catalog_id = { 
        "movie":0,
        "app":1,
        "music":2,
        "tv":3,
        "game":4,
        "anime":5 
    }

    #Topic  type :  0 -Movie,  1- Software APP, 2- Music

    movie_forum_page = "https://www.warez-bb.org/viewforum.php?f=4"
    tv_forum_page = "https://www.warez-bb.org/viewforum.php?f=57"
    game_forum_page = "https://www.warez-bb.org/viewforum.php?f=5"
    console_game_forum_page = "https://www.warez-bb.org/viewforum.php?f=28"
    app_forum_page = "https://www.warez-bb.org/viewforum.php?f=3"
    anime_forum_page = "https://www.warez-bb.org/viewforum.php?f=88"

    sticked_titles_id = [
        "21537617",
        "21451815",
        "21626981",
        "15678",
        "21399630",
        "6000413",
        "4170791",
        "2538913",
        "2538871",
        "589688",
        "16040260",
        "589689",
        "21793204"
    ]

    curr_page = 0

    def parse(self, response):
        """ Makes request to login onto warezbb
            with after_login as a callback
        """
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'nzgangster', 'password': 'KANyezus'},
            callback=self.after_login, dont_filter=True
        )


    def after_login(self, response):
        """ Checks that the spider has logged on
            and makes a number of requests to
            warez-bb sub-forums.
        """
        if "authentication failed" in response.body:
            print "Failed to Log in, exiting now"
            return
        else:
            print "Logged in"
            yield scrapy.Request(url=self.movie_forum_page,
                meta={'id': self.catalog_id["movie"]},
                callback=self.parse_outside_post, dont_filter=True)


    def parse_outside_post(self, response): 
        catalog_id = response.meta['id']
        if self.curr_page > self.end_page:
           # raise CloseSpider("crawled " + str(self.end_page))
           print "!@! last time inside parse_outside_post"
           pass
        elif self.curr_page >= self.start_page:
            print "collect threads from " + str(self.curr_page)
            f = open("numberOfPagesWarezMovies.txt","w")
            f.write(str(self.curr_page))
            catalog_id = response.meta['id']
            rows = response.xpath("//div[@class='list-rows']")
            for row in rows:
                # creating an item for storing
                item = WarezbbItem()

                # extracting the title
                title = row.xpath(".//div/span/span[@class='title']/a/text()")
                title = title.extract()[0].strip()

                item['title'] = title
                item['sources'] = self.get_movie_sources(title)
                item['detected_quality'] = self.get_movie_quality(title)

                replies = row.xpath(".//div[@class='topics']/span/text()")
                replies = replies.extract()
                item['replies'] = replies[0]

                views = row.xpath(".//div[@class='views']/span/text()")
                views = views.extract()
                item['views'] = views[0]

                item['catalog_id'] = catalog_id

                link = row.xpath(".//div/span/span[@class='title']/a/@href")
                link = link.extract()
                link_string = str(link)
                link_id = link_string[link_string.index("=")+1:]
                if link_id[:-2] not in self.sticked_titles_id:
                    link = "https://www.warez-bb.org/" + link[0]
                    item['link'] = link
                    yield scrapy.Request(url=link,
                        meta={'item': item},
                        callback=self.parse_inside_post, dont_filter=True)

        try:
            self.curr_page = self.curr_page + 1
            print "!@! going to page " +  str(self.curr_page)
            current_page = response.xpath("//b[@class='active-button']")
            current_page = current_page[0].xpath('text()').extract()[0]
            next_page = int(current_page) + 1
            next_link = response.xpath("//a[@title='Page " + str(next_page) + "']/@href")
            next_link = "https://www.warez-bb.org/" + next_link[0].extract()
            yield scrapy.Request(url=next_link, meta={'id' : catalog_id},
                callback=self.parse_outside_post, dont_filter=True)
        except:
            print "no next page"
            pass

    def parse_inside_post(self, response):
        item = response.meta['item']
        author = response.xpath(".//div[@class='author']/strong/text()")
        author = author.extract()
        item['author'] = author[0]

        post_date = response.xpath(".//div[@class='date']/a/text()").extract()
        post_date = post_date[0]
        item['post_date'] = post_date

        codes = response.xpath(".//div[@class='code']/span/text()")
        codes = codes.extract()
        codes_to_add = []
        for code in codes:
            if ("http" in code) and ( "imdb" not in code):
                codes_to_add.append(code)
        item['code_fields'] = codes_to_add
        yield item

    def get_movie_sources(self, title):
        found = re.search('^\[(.*?)\]', title)
        if found: 
            sources = found.group(1)
            if "/" in sources:
                char_to_spilt_by = "/"
            elif "+" in sources:
                char_to_spilt_by = "+"
            elif "\\" in sources:
                char_to_spilt_by = "\\"
            elif "|" in sources:
                char_to_spilt_by = "|"
            elif "-" in sources:
                char_to_spilt_by = "-"
            else:
                char_to_spilt_by = None
        else: 
            return None
        if char_to_spilt_by is not None:
            return sources.split(char_to_spilt_by)
        else:
            return [sources]

    def get_movie_quality(self, title):
        quality_types = [ 
            "dvdrip", "bdrip",
            "dvdsrc", "telesync",
            "bluray", "dbd",
            "cam", "hdts",
            "tc", "telecine",
            "ppv", "webrip",
            "vodrip", "workprint",
            "screener", "hdrip",
            "720p", "web-dl",
            "1080p", "hdtv",
            "480p", "web dl",
            "brrip", "mp4"
            ]
        title = title.lower()
        movie_quality_array = []
        for type_ in quality_types:
            if type_ in title:
                movie_quality_array.append(type_)

        return movie_quality_array