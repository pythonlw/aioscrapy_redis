# -*-coding:utf-8-*-

class Proxy_Middle():
    def get_local_proxy(self):
        from urllib.request import getproxies
        proxy = getproxies().get('http')
        return proxy

















