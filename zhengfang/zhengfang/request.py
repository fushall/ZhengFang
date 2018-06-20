# coding: utf8

import requests
import urllib.parse

from .exceptions import RequestException



class ZFRequest:
    def __init__(self, host):

        # url
        self._host = host

        self._session = requests.session()
        self._session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        # 可以自定义超时时间(connect, read) 或者 None
        self._timeout = None

    # property

    def url(self, res=None):
        return 'http://' + self._host + (('/'+res) if res[0] != '/' else res)

    # methods

    def request(self, method, url, **kwargs):
        try:
            response = self._session.request(method, url,
                                        timeout=self._timeout,
                                        allow_redirects=False, # 以免Object moved浪费系统资源
                                        **kwargs)

            # 不设定页面的字符编码成gbk，一些字会有乱码，比如“玥”
            response.encoding = 'gbk'

            text = response.text
            if response.status_code == 302 and text.find('Object moved'):
                raise RequestException('Object moved')

            return response
        except requests.Timeout:
            raise RequestException('Timeout')

        except requests.ConnectionError:
            raise RequestException('ConnectionError')

    def get(self, res, params=None, **kwargs):
        url = self.url(res)
        return self.request('GET', url, params=params, **kwargs)

    def post(self, res, data, **kwargs):
        # 正方教务系统，会把post的数据中的空格转换成+号，+号url编码
        url = self.url(res)
        try:
            return self.request('POST', url, data=self.urlencode(data, encoding='gbk'), **kwargs)

        except UnicodeEncodeError:
            raise RequestException('数据中有不支持的字符')

    @property
    def cookies(self):
        return requests.utils.dict_from_cookiejar(self._session.cookies)

    @cookies.setter
    def cookies(self, value):
        """
        value 是存有cookies 的字典，例如：{"sessioncookie": "123456789"}
        """
        self._session.cookies = requests.utils.cookiejar_from_dict(value)

    @staticmethod
    def urlencode(query, encoding=None, **kwargs):
        # url编码
        return urllib.parse.urlencode(query, encoding=encoding, **kwargs)

    @staticmethod
    def quote(string, safe='/', encoding=None, errors=None):
        return urllib.parse.quote_plus(string, safe, encoding, errors)

    @staticmethod
    def unqoute(string, encoding='utf-8', errors='replace'):
        return urllib.parse.unquote_plus(string, encoding, errors)
