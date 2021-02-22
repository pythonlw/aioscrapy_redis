# -*-coding:utf-8-*-


class BaseDownloaderMiddleware(object):
    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass




