# coding: utf8

from .login import Login
from .exceptions import EvaluateException
from .grade import list_from_tagtable
from bs4 import BeautifulSoup

class Evaluate(Login):
    def __init__(self, session=None):
        super().__init__(session=session)


    def menu_pingjiao(self):
        """
        返回一个列表, 为空就是没开
        调用之前，必须先登录，xh参数可以省略
        登陆教务系统以后，弹出的主页中的教学质量评价下拉菜单有子项
        那么，就是开放了评教
        """
        kecheng  = []
        try:
            soup = self.visit_xs_main()
            # ul应该是li
            menu = next(
                filter(
                    lambda x: str(x).find('教学质量评价')!=-1,
                    soup.find_all('li', {'class':'top'})
                )
            )
            for li in menu.find_all('li'):
                a = li.a
                kecheng.append({
                    'url' : a['href'],
                    'name':str(a.string)
                })
            return kecheng

        except StopIteration:
            return None

    @staticmethod
    def _get_kecheng(soup):
        # 课程名 课程号
        # <select>
        #    <option selected="selected">某课程</option>
        #    <option >xxx</option>
        sel = soup.find('select', {'name': 'pjkc'})
        if sel:
            opt = sel.find('option', {'selected': 'selected'})
            if opt and opt.get('value'):
                return str(opt.text), opt.get('value')
        raise EvaluateException('获取课程名，课程号失败')

    @staticmethod
    def _get_action(soup):
        # <form post action>
        action = soup.find('form', {'name': 'Form1'})
        if action and action.get('action'):
            return action.get('action')

        raise EvaluateException('获取form post 中的 action链接失败')

    @staticmethod
    def _get_viewstate(soup):
        # __VIEWSTATE
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate and viewstate.get('value'):
            return viewstate['value']
        raise EvaluateException('获取__VIEWSTATE失败')

    @staticmethod
    def _get_gonggao(soup):
        # 公告，其他建议
        table = soup.find('table', {'class': 'formlist'})
        if table:
            all_tr = table.find_all('tr')
            if all_tr:
                try:
                    gonggao = str(all_tr[0].td.text)
                    qita = str(all_tr[-1].td.textarea.string)
                    return gonggao, qita
                except AttributeError:
                    raise EvaluateException('评教网页结构已更改')
        raise EvaluateException('获取评教公告失败')

    @staticmethod
    def _get_jiaoshi(tlist):
        jiaoshi = tlist[0][-1]
        tlist[0][-1] = '等级'
        return jiaoshi

    @staticmethod
    def _get_pingjia(soup):
        # 评价列表(未格式化的)
        table = soup.find('table', {'class': 'datelist'})
        if table is None:
            raise EvaluateException('获取评价列表<table>失败')

        tlist = list_from_tagtable(str(table))
        if not tlist:
            raise EvaluateException('评价列表<table>转换成list失败')

        # 提取教师姓名
        # todo: 教师是列表，名字+图片，需要改
        # <td>一级指标</td><td width="50">评价号</td><td>评价内容</td><td valign="Middle"><table border="0" cellspacing="0" cellpadding="0"><tbody><tr><td>包晓明</td><td width="2px"></td><td><img src="readimagejs.aspx?zgh=1987020006&amp;lb=ckjszp" width="40px" height="60px"></td></tr></tbody></table></td>
        # '''任课教师：</td><td><img height="60px" src="readimagejs.aspx?zgh=1987020006&amp;lb=ckjszp" width="40px"/>'''
        jiaoshi = Evaluate._get_jiaoshi(tlist)

        #  一级指标, '评价号', '评价内容', '等级'
        key_list = ['yjzb', 'pjh', 'pjnr', 'dj']
        pingjia = [dict(
            zip(key_list, tlist.pop(0))
        )]

        # 解析opthions 和 默认选中的那个
        for row in tlist:
            soup_tag_sel = BeautifulSoup(row[-1], 'html.parser')
            # 解析<select>和子<option>
            # select 标签的name属性为要post的key
            select = soup_tag_sel.find('select')
            if select is None:
                raise EvaluateException('获取select 的 name 属性失败')

            # 解析每一个option的值（等级）到列表框
            opts = soup_tag_sel.find_all('option')
            if opts is None:
                raise EvaluateException('解析option 的值失败')

            options = []
            for opt in opts:
                options.append(opt.get('value'))

            # 把数据整理到item里
            item = row[:-1]
            item.append({
                # 选中的必须在options里
                # todo: 判断selected in options
                'select': {
                    'name': select.get('name'),
                    'value': options.pop(0),  # 第一个是选中的评价
                },
                'options': options,
            })

            # 有问题
            # ??什么问题
            pingjia.append(dict(zip(key_list, item)))
        return pingjia, jiaoshi

    def parse_pingjia(self, res):

        response = self.request.get(res)
        if response.status_code == 200:

            html = response.text
            if html.find('目前未对你放开教学质量评价') != -1:
                raise EvaluateException('目前未对你放开教学质量评价')

            soup = self.soup(html)

            kecheng, kehao = self._get_kecheng(soup)
            action = self._get_action(soup)
            viewstate = self._get_viewstate(soup)
            gonggao, qita = self._get_gonggao(soup)
            pingjia, jiaoshi = self._get_pingjia(soup)

            return {
                'action': action,  # <from post action>
                'vs': viewstate,  # __VIEWSTATE
                'gg': gonggao,  # 公告
                'kc': kecheng,  # 课程
                'kh': kehao,  # 课号
                'js': jiaoshi,  # 教师
                'pj': pingjia,  # 评价
                'qt': str(qita),  # 其他评价与建议（限50）字
            }

    def save(self, viewstate, kehao, qita, pingjia, eventtarget=None, eventtargument=None):

        res = '/xsjxpj.aspx?xkkh={0}&xh={1}&gnmkdm=N12141'.format(kehao, self.session['student']['number'])

        data = {
            '__EVENTTARGET': eventtarget,  # 当前请求为空
            '__EVENTARGUMENT': eventtargument,  # 同上
            '__VIEWSTATE': viewstate,
            'pjkc': kehao,
            'pjxx': qita,
            'txt1': '',
            'TextBox1': 0,
            'Button1': '保  存',
        }

        for item in pingjia:
            data[item['name']] = item['value']

        response = self.request.post(res, data)
        if response.status_code == 200:
            html = response.text
            if html.find('你必须评价完每个教师！！') != -1:
                raise EvaluateException('您有未填写的评价哦，请返回填写完整。')

            elif html.find('其他评价与建议不能超过50个字！！') != -1:
                raise EvaluateException('其他评价与建议不能超过50个字，请返回修改，修改后再次执行该操作。')

            else:
                return True

    def submit(self, viewstate, kehao):
        res = '/xsjxpj.aspx?xkkh={0}&xh={1}&gnmkdm=N12141'.format(kehao, self.session['student']['number'])
        data = {
            '__VIEWSTATE': viewstate,
            'Button2': '提  交',
        }

        response = self.request.post(res, data)

        if response.status_code == 200:
            html = response.text

            if html.find('您已完成评价！') != -1:
                return True

            elif html.find('还有课程没有进行评价！！') != -1:
                raise EvaluateException('还有课程没有进行评价！')

            else:
                raise EvaluateException('提交失败：未知错误')


