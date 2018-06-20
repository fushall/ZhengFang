# coding: utf8

import time

from .zhengfang import ZhengFang
from .exceptions import LoginException


class Login(ZhengFang):
    def __init__(self, session=None):
        super().__init__(session=session)

    def visit_xs_main(self, stu_no=None):
        """
        通过访问 http://host/xm_main.aspx?xh={stu_no}，
        获取姓名，来判断是否登陆成功，
        stu_no: 学号
        """
        try:
            stu_no = stu_no if stu_no else self.session['student']['number']
        except KeyError:
            raise LoginException('您还没登陆')

        if stu_no:
            response = self.request.get('/xs_main.aspx?xh={0}'.format(stu_no))
            if response.status_code == 200:



                soup = self.soup(response.text)
                ul   = soup.find('div', {'class': 'info'}).ul
                name = str(ul.find('span', {'id': 'xhxm'}).string)[:-2] # 剔除 '同学'

                self.session['student'].update({'name': name})
                self.session.update({
                    # 之前登陆过了，cookies更新了还是原来的，否则，就是新的
                    'cookies': self.request.cookies,
                    'timestamp': time.time()
                })
                return soup
            else:
                raise LoginException('page_xm_main:请求非200.' + str(response.status_code))
        else:
            raise LoginException('您还没登陆')

    def get_viewstate(self):
        """
        获取无验证码主页的 <input name='__VIEWSTATE' value=xxxxx> 的 value
        不涉及到是否已经登陆
        """

        response = self.request.get('/default3.aspx')
        if response.status_code == 200:
            soup = self.soup(response.text)
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            if viewstate:
                return viewstate['value']
            else:
                raise LoginException('获取__VIEWSTATE失败')
        else:
            raise LoginException('get_viewstate:请求非200.' + str(response.status_code))

    @property
    def online(self):
        now = time.time()
        timestamp = self.session['timestamp']
        minuates = (now - timestamp) / 60
        if minuates < 10 and self.session.get('cookies'):
            return True
        else:
            return False

    def login(self, stu_no, stu_pw):
        """
        http 登陆到教务系统
        stu_no: 学号
        stu_pd: 密码
        """

        data = {
            '__VIEWSTATE': self.get_viewstate(),
            'TextBox1': stu_no,
            'TextBox2': stu_pw,
            'ddl_js': '学生',
            'Button1': ' 登 陆 ',
        }

        response = self.request.post('/default3.aspx', data)
        if response.status_code == 200:
            html = response.text
            # 通过访问 http://host/xm_main.aspx?xh={stu_no}，
            # 获取姓名，来判断是否登陆成功，
            if html.find('xs_main.aspx') != -1 and self.visit_xs_main(stu_no=stu_no):
                self.session['student'].update({
                    'number': stu_no,
                    'password': stu_pw,
                })
                return True

            elif html.find('用户名不存在或未按照要求参加教学活动！！') != -1:
                raise LoginException('用户名不存在或未按照要求参加教学活动！！')

            elif html.find('用户名不能为空！！') != -1:
                raise LoginException('用户名不能为空！！')

            elif html.find('密码错误！！') != -1:
                raise LoginException('密码不对！')

            else:
                raise LoginException('未知的登陆错误！！')

        else:
            raise LoginException('do:请求非200.' + str(response.status_code))