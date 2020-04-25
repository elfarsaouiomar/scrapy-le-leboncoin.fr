# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import loads
from requests import post
from scrapy import Request
from scrapy.spiders import CrawlSpider
from hashlib import md5
from threading import Thread
from os.path import splitext
from random import randint
from time import sleep
from logging import error
from scrapyLebonCoin.exception.ErrBackException import ErrBackException

class LeboncoinfrSpider(CrawlSpider):

    name = "leboncoin"
    allowed_domains = ["leboncoin.fr"]
    baseUrl = "https://www.leboncoin.fr"

    cookie = {
        "didomi_token":"eyJ1c2VyX2lkIjoiMTcxYWY2Y2ItYzIxYy02YTY4LWExMWItOWNkMDJjYmIwYjBjIiwiY3JlYXRlZCI6IjIwMjAtMDQtMjVUMDM6NDE6MTEuMTI3WiIsInVwZGF0ZWQiOiIyMDIwLTA0LTI1VDE1OjIyOjEwLjQ1MFoiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsiZ29vZ2xlIiwiYW1hem9uIl0sImRpc2FibGVkIjpbXX0sInB1cnBvc2VzIjp7ImVuYWJsZWQiOlsiY29va2llcyIsImFkdmVydGlzaW5nX3BlcnNvbmFsaXphdGlvbiIsImNvbnRlbnRfcGVyc29uYWxpemF0aW9uIiwiYWRfZGVsaXZlcnkiLCJhbmFseXRpY3MiXSwiZGlzYWJsZWQiOltdfX0=;",
        "euconsent":"BOyZO1nOya1hYAHABBFRDG-AAAAvRr_7__7-_9_-_f__9uj3Or_v_f__32ccL59v_h_7v-_7fi_-1nV4u_1vft9yfk1-5ctDztp507iakivXmqdeb1v_nz3_9pxPr8k89r7337Ew_v8_v-b7BCON9IAAAAAA; abtest_user=1;",
        "datadome":"CbfQLP_TAYdTaIhWqXqFCE1cHxXzp~FsUUz6iALPMnP2P8CDf8x-9d_lgnntXmyO_JhQRan4AfFOec7RoPiL7Fz1_fK93aVTNrUjNBD2V_",
    } 
    #
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,fr;q=0.9,en-US;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alivXe",
        "Host": "www.leboncoin.fr",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "user-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    }
    errBackException = ErrBackException()

    def __init__(self, url=None, *args, **kwargs):
        super(LeboncoinfrSpider, self).__init__(*args, **kwargs)
        try:
            if url:
                self.start_urls = url and url.split(',') or []
            else:
                self.logger.error("scrapy crawl {0} -a url=https://www.leboncoin.fr/motos/offres/".format(self.name))

        except Exception as e:
            self.logger.error(e)

    def start_requests(self):
        for url in self.start_urls:
            print("*"*100)
            request = Request(url=url, callback=self.parse_items, errback=self.requestFailure, headers=self.header, cookies=self.cookie)
            yield request

    def requestFailure(self, failure):
        self.errBackException.errBack(failure=failure)


    def parse_items(self, response):
        ads_elems = response.css('._3DFQ- > a::attr(href)').getall()
        for ad_elem in ads_elems:
            url = self.baseUrl+ad_elem
            if url:
                request = Request(url=url,callback=self.parseItemDetails,errback=self.requestFailure,dont_filter=True)
                yield request

            """ follow the pagination """

            for counter in range(0, 10):
                if counter == 0:
                    url = response.url
                else:
                    url = response.url + "p-{0}/".format(counter)
                    paginationRequest = Request(
                        url=url,
                        callback=self.parse_items,
                        errback=self.requestFailure,
                        dont_filter=True
                    )

                    yield paginationRequest

    def parseItemDetails(self, response):
        leboncoin = {}
        try:
            compnayId = self.extractId(response.url)

            leboncoin = loads(response.xpath('//script/text()').re_first(r'window.FLUX_STATE =\s*(.*)'))
            phone = self.getPhone(compnayId)
            if phone:
                leboncoin['phone'] = phone
            leboncoin['images'] = self.getImages(leboncoin.get('adview').get('images').get('urls'))

        except Exception as err:
            self.logger.error(err)

        finally:

            yield {
                "type": None,
                "url": response.url,
                "source": "leboncoin.fr",
                "codeNaf": None,
                "pros": leboncoin
            }

    def extractId(self, url):
        compnyId = None
        try:
            compnyIdSpilt = url.split('/')
            compnyId = compnyIdSpilt[4]
            if compnyId:
                compnyId = compnyId.split('.')
                if compnyId:
                    compnyId = compnyId[0]

        except Exception as getPhoneError:
            self.logger.error(getPhoneError)

        finally:
            return compnyId

    def getPhone(self, compnyId):

        phone = None

        params = {
            'app_id': 'leboncoin_web_utils',
            'list_id': compnyId,
            'text': '1'
        }

        header = {

            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '89',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.leboncoin.fr',
            'Origin': 'https://www.leboncoin.fr',
            'Referer': 'https://www.leboncoin.fr/voitures/1764886480.htm/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',

        }

        url = "https://api.leboncoin.fr/api/utils/phonenumber.json"
        try:
            phoneResponse = post(url=url, headers=header, data=params)

            parseJsonPhon = loads(phoneResponse.text)

            phone = parseJsonPhon['utils']['phonenumber']
        except KeyError:
            self.logger.info('[!] phone not found')

        except Exception as errorInPhoneParser:
            self.logger.error("[!] error in phone parser  %s" % errorInPhoneParser)

        finally:
            return phone

    def randomSleeper(self, valueA, valueB):
        """
            this function here it used to sleep for random time
            bettwen valueA et valueB
        """
        try:

            sleepSecond = randint(valueA, valueB)

            print("[+] I will sleep for {} second".format(sleepSecond))

            sleep(sleepSecond)

            print("[+] This nice sleep oh let's continue")

        except KeyboardInterrupt:
            print("[!] Ctrl+c pressed ")
            exit(0)

        except Exception as er:
            print(er)

    def getImages(self, urls):
        try:

            imagesList = []
            for url in urls:

                images = {}
                print("[+] strat download from {0} ".format(url))
                imageExt = splitext(url)[-1]
                imageFinalName = md5(url.encode()).hexdigest()+""+imageExt
                images['name'] = imageFinalName
                imagesList.append(images)
                downloadimage = Thread(target=self.dowloadImg, args=(url, imageFinalName,))
                downloadimage.start()

            return imagesList

        except Exception as geneException:
            self.logger.error(geneException)

    def dowloadImg(self, url, imageFinalName):
        """
            this function take url and image name
            and it will download the image and save it
            into public folder
          :param url: image link
          :param imageFinalName: the final name
        """
        try:
            if imageFinalName is not None and url is not None:
                fileNameDestination = "public/{0}".format(imageFinalName)
                opener = build_opener()
                # set user agent
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')]
                install_opener(opener)
                urlretrieve(url, fileNameDestination)
                opener.close()

        except URLError as urlErr:
            error('URLError on %s' % urlErr)
            error('Url Error is : %s ' % url)

        except HTTPError as httpErr:
            error('HTTPError on %s' % httpErr)
            error('Url Error is : %s ' % url)

        except Exception as er:
            error('generale exception on %s', er)
            error('Url Error is : %s ' % url)


    

    """


    """
