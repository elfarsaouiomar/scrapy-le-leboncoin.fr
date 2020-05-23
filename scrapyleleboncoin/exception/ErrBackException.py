from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from logging import error


class ErrBackException(Exception):

    def errBack(self, failure):
        error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            error("Http Staus Code is %s", response.status)
            error('HttpError on %s', response.url)
            error('Proxy Address is : {}'.format(response.meta.get('proxy')))

            # list of status denied
            # by default 403 but some server chnage the status code
            accessDenied = [503,403]

            if response.status in accessDenied:
                error("[-] Forbidden: Access is denied.")
                # change the tor or the VPN

            if response.status == 400:
                error('[-] Error: Bad request')

            if response.status == 500:
                error("[-] internal server")

            if response.status == 404:
                error("[-] route not found ")

        elif failure.check(DNSLookupError):
            request = failure.request
            error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            error('TimeoutError on %s', request.url)
