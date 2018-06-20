# coding: utf8

import re

from .login import Login
from .exceptions import GradeException


def is_number(s):
    """
    判断s 是否是一个整数/小数
    """
    if isinstance(s, str):
        return s.replace('.', '', 1).isdigit()

def is_not_number(s):
    return not is_number(s)

def list_from_tagtable(tagtable):
    """
    解析<table>里的数据成[[字段], [记录1], ...]
    """
    p_tr = re.compile('<tr.+?/tr>', re.S)
    p_td_data = re.compile('<td[^>]*>(.+?)</td>', re.S)

    item = []
    for i in p_tr.findall(tagtable):
        item.append(
            list( # 转换成list对象
                map(
                    lambda x: str(x).replace('\xa0', '') , # 替换条件
                    p_td_data.findall(i) # 操作的list
                )
            )
        )
    return item

def dict_from_gradetlist(tlist):
    """
    将包含成绩的tlist 转换成dict
    tlist: <table>内数据转换而成的list
            tlist[0] 为字段，其余为数据

    参考
    [
        ['学年', '学期', '课程代码', '课程名称',
         '课程性质', '课程归属', '学分', '绩点',
         '成绩', '辅修标记', '补考成绩', '重修成绩',
         '学院名称', '备注''重修标记'
         ],
        ['2015-2016', '1', '2701010203', 'MS Office高级（二级）',
        '必修课', '', '4', '2',
        '74', '0', '', '',
        '计算机与信息工程系', '','0'
        ],
    ]

    """

    dict_grade = {}
    for item in tlist:

        key_year = item.pop(0)
        key_term = item.pop(0)

        key = key_year + '-' + key_term
        if key not in dict_grade:
            dict_grade[key] = []

        dict_grade[key].append(item)

    return dict_grade

def sorted_gradedict(tdict):
    """
     排序结构如下的字典：
    {
        '2015-2016-2': [
            ['0000090409', '大学语文',   '公选课', '', '2.0', '4', '98.5',  '0', '', '', '教务处', '', '0'],
            ['2701010102', '高等数学Ⅱ', '必修课', '', '4',   '4', '94',    '0', '', '', '计算机与信息工程系', '', '0'],
            ...
        ],
        '2016-2017-1': [
            ['270101020, ...],
            [... ],
            ...
         ],
         ....
    }
    """

    for key in tdict:
        # 每一学期的N条数据
        items = tdict[key]

        # 必修课、选修课和公选课分开排
        l1, l2, l3, l4 = [], [], [], []
        for item in items:
            # 如果有补考成绩，则以最后一次补考成绩为准
            if is_number(item[8]):
                item[6] = item[8]
            # 重修
            if is_number(item[9]):
                item[6] = item[9]

            if item[2] == '必修课':
                l1.append(item)
            elif item[2] == '选修课':
                l2.append(item)
            elif item[2] == '公选课':
                l3.append(item)
            else:
                l4.append(item)

        def _(i):
            """
            按成绩排序算法：
            若成绩处为空，按-1算
            为汉字，按0 算
            为数字，则正常排序
            """
            score = i[6]
            if score == '':
                return -1
            elif is_number(score):
                return float(score)
            else:
                return 0

        l = sorted(l1, key=_, reverse=True)+ \
            sorted(l2, key=_, reverse=True)+ \
            sorted(l3, key=_, reverse=True)+ \
            sorted(l4, key=_, reverse=True)

        # 添加各类标记
        for i in l:
            # 添加补考标记
            score = i[6]
            if is_number(i[8]):
                i[6] = '[补]' + score

            # 添加重修标记
            elif is_number(i[9]):
                i[6] = '[重]' + score

            # 补位
            else:
                i[6] = ' 　 ' + score

            # 必修课前添加 '**'标识
            # i[2]：课程性质
            # i[1]：课程名称
            if i[2] == '必修课':
                i[1] = '**' + i[1]

        # 替换原来的list
        tdict[key] = l
    return tdict

class Grade(Login):
    def __init__(self, session=None):
        super().__init__(session=session)


    def get_gradeviewstate(self, res):
        response = self.request.get(res)
        if response.status_code == 200:
            soup = self.soup(response.text)
            return soup.find('input', {'name': '__VIEWSTATE'})['value']

        else:
            raise GradeException('get_viewstate:请求非200.' + str(response.status_code))


    def get_grade(self, raw=False):
        name = self.session['student']['name']
        number = self.session['student']['number']

        res = '/xscj_gc.aspx?xh={0}&xm={1}&gnmkdm=N121605'.format(number, name)
        data = {
            'Button2': '在校学习成绩查询',
            '__VIEWSTATE': self.get_gradeviewstate(res),
            'ddlXN': '',
            'ddlXQ': ''
        }
        response = self.request.post(res, data)
        if response.status_code == 200:

            soup = self.soup(response.text)

            # 提取 html <table> ... </table>表格内容
            table = str(soup.find('table', {'class': 'datelist'}))

            # 从表格转换成list
            tlist = list_from_tagtable(table)

            if raw:
                return tlist

            # 按学年-学期分组，未排序
            tdict = dict_from_gradetlist(tlist[1:])


            # 返回排序结果
            return sorted_gradedict(tdict)
        else:
            raise GradeException('get:请求非200.' + str(response.status_code))