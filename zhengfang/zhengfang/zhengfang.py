# coding: utf8

from bs4 import BeautifulSoup

from .request import ZFRequest


class ZhengFang:
    # 未来还可以加入公告，等等
    def __init__(self, host='jiaoshi.jiaowu.nmxxy.cn:444', session=None):

        # 面向正方教务系统的http请求
        self.request = ZFRequest(host=host)

        # 解析html
        self.soup = lambda markup: BeautifulSoup(markup=markup, features='html.parser')

        if session is None:
            self.session = {
                'student': {
                    'name': None,       # 姓名
                    'number': None,     # 学号
                    'password': None,   # 密码
                },
                # HTTP请求中cookies字典，如：{"sessioncookie": "123456789"}
                'cookies': None,
                # 时间戳，用来判断登陆过期
                'timestamp': 0.0,
            }
        else:
            self.session = session
            # cookies为空的时候也应该做点儿什么。。。
            self.request.cookies = self.session.get('cookies')
