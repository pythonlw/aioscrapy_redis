# _*_ coding: utf-8 _*_

import logging
import aiohttp
from urllib.parse import urlparse
import chardet
import asyncio
from aioscrapy_redis.https.response import Response
from aioscrapy_redis.utils.http_proxy import Proxy_Middle
from aioscrapy_redis.utils.header_ua import get_headers

class DownloadHandler(object):
    """ DownloadHandler """
    def __init__(self, spider):
        self.settings = spider.setting
        self.proxy_middle = Proxy_Middle()
    async def fetch(self, request):
        kwargs = {}
        try:
            if request.headers:
                headers = request.headers
            elif get_headers():
                headers = get_headers()
            elif self.settings.get('headers', False):
                headers = self.settings.get('headers')
            else:
                headers = {
                    'User-Agent':"mozilla/5.0 (windows nt 6.1; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/69.0.3494.0 safari/537.36",
                }
            kwargs['headers'] = headers
            timeout = self.settings.get("TIMEOUT", 40)
            kwargs['timeout'] = int(timeout)
            # ssl
            ssl = self.settings.get('SSL',True)
            kwargs["ssl"]=ssl
            # proxy IP
            proxy = request.meta.get("proxy", False)
            proxy1 = self.proxy_middle.get_local_proxy()
            if proxy:
                if not isinstance(proxy ,str):
                    print("TypeError: proxy should be str;For example:proxy='http://127.0.0.1:10080'")
                    return Response(url=str(request.url),
                        headers=request.headers,status=0,flags=request.flags,
                        request=request,body=b'',exceptions="TypeError: proxy should be str;For example:proxy='http://127.0.0.1:10080'")
                kwargs["proxy"] = proxy
                print("user proxy {}".format(proxy))
            elif proxy1:
                kwargs["proxy"] = proxy1
                print("user proxy {}".format(proxy1))
            #proxy_auth
            proxy_auth=request.headers.get('Proxy-Authorization')
            if proxy_auth and ':' in proxy_auth:
                proxy_auth=aiohttp.BasicAuth(proxy_auth.split(':')[0],proxy_auth.split(':')[0])
                kwargs["proxy_auth"] = proxy_auth
            else:
                if proxy_auth:
                    print('The format of Proxy-Authorization must be username:password')
            #ssl
            ssl=request.headers.get('SSL')
            if ssl in [False,True]:
                kwargs["ssl"] = ssl
            else:
                if ssl != None:
                    print('ssl defaults to True,ssl must be of boolean type')
            # cookies
            cookies=request.cookies
            if isinstance(cookies, dict):
                kwargs['cookies']=cookies
            else:
                if request.cookies:
                    print('cookies must be a dictionary')
            url = request.url
            async with aiohttp.ClientSession() as session:
                try:
                    if request.method == "POST":
                        response = await session.post(url, data=request.data, **kwargs)
                    else:
                        response = await session.get(url, **kwargs)
                except Exception as e:
                    print('request_error:',e)
                    return Response(url=str(request.url),
                        headers=request.headers,
                        status=0,
                        flags=request.flags,
                        request=request,
                        body=b'',
                        exceptions=str(e))
                content = await response.read()
                return Response(url=str(response.url),
                                status=response.status,
                                headers=response.headers,
                                body=content,
                                flags=request.flags,
                                request=request,
                                exceptions=None)
        except Exception as _e:
            print('downloadHandler_error:',_e)
            logging.exception(_e)
            return Response(url=str(request.url),
                            status=404,
                            request=request,
                            exceptions=str(_e)
                            )


class Downloader(object):
    """ Downloader """
    ENCODING_MAP = {}
    def __init__(self, spider):
        self.hanlder = DownloadHandler(spider)

    async def fetch(self, request):
        """
        request, Request
        """
        response1 = await self.hanlder.fetch(request)
        response = self.process_response(request, response1)
        return response

    def process_response(self, request, response):
        if response.exceptions:
            return response
        netloc = urlparse(request.url).netloc
        content = response.body
        if self.ENCODING_MAP.get(netloc) is None:
            encoding = chardet.detect(content)["encoding"]
            encoding = "GB18030" if encoding.upper() in ("GBK", "GB2312") else encoding
            self.ENCODING_MAP[netloc] = encoding
        try:
            text = content.decode(self.ENCODING_MAP[netloc], "replace")
        except Exception as e:text=''
        return  Response(url=str(response.url),
                         status=response.status,
                         headers=response.headers,
                         body=response.body,
                         text=text,
                         request=request,
                         flags=request.flags,
                         exceptions=None,
                         )