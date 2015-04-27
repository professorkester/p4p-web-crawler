
import scrapy
from webcrawler.items import KickassItem

class KickassSpider(scrapy.Spider):
    name = "kickass"
    allowed_domains = ["https://kickass.to/"]

    start_urls = [
       "https://kickass.to"
    ]

    #Make request to a number of pages of movies with parse_movie_page as a callback
    def parse(self, response):
        num_pages = 11

        for x in range(0,11):
            if (x == 0):
                yield scrapy.Request(url="https://kickass.to/movies/",callback=self.parse_movie_page,dont_filter=True)
            else:
                yield scrapy.Request(url="https://kickass.to/movies/" + str(x) + "/",callback=self.parse_movie_page,dont_filter=True)

    #Parse and make a request to each movie link inside a page of page of movies with parse_movie as a callback
    def parse_movie_page(self,response):
        list_movies_url = response.xpath(".//div[@class='markeredBlock torType filmType']/a/@href").extract()

        for url in list_movies_url:
            movie_page = "https://kickass.to" + url
            yield scrapy.Request(url=movie_page,callback=self.parse_movie,dont_filter=True)
    
    #Make a request to a movie page, and scrape the relevant information
    def parse_movie(self,response):
        item = KickassItem()

        title = response.xpath(".//h1[@class='novertmarg']/a/span/text()").extract()
        title = title[0]

        author = response.xpath(".//div[@class='font11px lightgrey line160perc']/span/span/a/text()").extract()
        author = author[0]

        author_reputation = response.xpath(".//div[@class='font11px lightgrey line160perc']/span[@class='badgeInline']/span[@class='repValue positive']/text()").extract()
        author_reputation = author_reputation[0]

        downloads = response.xpath(".//div[@class='font11px lightgrey line160perc']/text()").extract()
        downloads = downloads[3].split("Downloaded")[1].split("times")[0].strip()

        post_date = response.xpath(".//div[@class='font11px lightgrey line160perc']/text()").extract()
        post_date = post_date[0].split("Added on")[1].split("by")[0].strip()

        replies = response.xpath(".//div[@class='tabs tabSwitcher']/ul[@class='tabNavigation']/li/a/span/i/text()").extract()
        replies = replies[0]

        likes = response.xpath(".//span[@id='thnxCount']/span/text()").extract()
        likes = likes[0]

        dislikes = response.xpath(".//*[@id='fakeCount']/span/text()").extract()
        dislikes = dislikes[0]

        seeders = response.xpath("//div[@class='seedLeachContainer']/div[@class='seedBlock']/strong/text()").extract()
        seeders = seeders[0]

        leechers = response.xpath("//div[@class='seedLeachContainer']/div[@class='leechBlock']/strong/text()").extract()
        leechers = leechers[0]

        imdb_rating = response.xpath("//*[@id='tab-main']/div[2]/div/ul[1]/li[4]/text()").extract()
        imdb_rating = imdb_rating[0]

        #rotten_tomatoes = response.xpath("//*[@id='tab-main']/div[2]/div/ul[1]/li[5]/span[1]").extract()
        #rotten_tomatoes = rotten_tomatoes[0]

        detected_quality = response.xpath(".//div[@class='dataList']/ul[@class='block overauto botmarg0']/li[2]/span/text()").extract()
        detected_quality = detected_quality[0]

        movie_release_date = response.xpath("//*[@id='tab-main']/div[2]/div/ul[2]/li[2]/text()").extract()
        movie_release_date = movie_release_date[0]

        #language = response.xpath(".//div[@class='dataList']/ul[2]/li[4]/span/text()").extract()
        #language = language[0].strip()

        genre = response.xpath(".//div[@class='dataList']/ul[@class='block overauto botmarg0']/li[6]/a[@class='plain']/span/text()").extract()

        #Getting the unit of file_size, e.g. GB,MB,etc.
        file_size_unit = response.xpath("//*[@id='tab-main']/div[5]/div[1]/div[1]/strong/span/text()").extract()

        file_size = response.xpath("//*[@id='tab-main']/div[5]/div[1]/div[1]/strong/text()").extract()
        file_size = file_size[0] + file_size_unit[0]

        cast = response.xpath("//*[@id='tab-main']/div[2]/div/div[1]/span/a/text()").extract()

        item["title"] = title
        item["author"] = author
        item["author_reputation"] = author_reputation
        item["downloads"] = downloads
        item["post_date"] = post_date
        item["replies"] = replies
        item["likes"] = likes
        item["dislikes"] = dislikes
        item["seeders"] = seeders
        item["leechers"] = leechers
        item["imdb_rating"] = imdb_rating
        #item["rotten_tomatoes"] = rotten_tomatoes
        item["detected_quality"] = detected_quality
        item["movie_release_date"] = movie_release_date
        #item["language"] = language
        item["genre"] = genre
        item["file_size"] = file_size
        item["cast"] = cast

        yield item