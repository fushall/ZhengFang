# coding: utf8
from flask import Blueprint, render_template, session, request, make_response, jsonify
from zhengfang.grade import Grade
from zhengfang.exceptions import ZhengFangException



api = Blueprint('api', __name__)

def is_number(s):
    """
    判断s 是否是一个整数/小数
    """
    if isinstance(s, str):
        return s.replace('.', '', 1).isdigit()


def arrange(grade_table):
    '''
    整理数据
    :param grade_list:
    :return:
    '''
    grade_list = None
    last_semester, last_schoolyear = None, None  # 上一学期/年
    struct_semester, semester_data = None, None
    struct_schoolyear, schoolyear_data = None, None

    for item in grade_table:
        schoolyear = item.pop(0)
        semester = item.pop(0)
        others = item

        if last_semester != semester:
            if last_schoolyear != schoolyear:
                # 新学年 并且 新学期
                # 添加一个新学年
                schoolyear_data = []
                struct_schoolyear = dict(schoolyear=schoolyear, data=schoolyear_data)
                if grade_list is None:
                    grade_list = []
                grade_list.append(struct_schoolyear)

            # 仅新学期
            # 添加一个新学期
            semester_data = []
            struct_semester = dict(semester=semester, data=semester_data)
            schoolyear_data.append(struct_semester)

        keys_course = [
            # 课程代码  课程名称  课程性质  课程归属
            'id', 'name', 'nature', 'kind',
            # 学分  绩点  成绩  辅修标记
            'credit', 'point', 'grade_final', 'mark_minor',
            # 补考成绩  重修成绩  学院名称  备注
            'grade_markup', 'grade_retake', 'college_name', 'note',
            # 重修标记
            'mark_retake',
        ]

        struct_course = dict(zip(keys_course, others))
        semester_data.append(struct_course)

        # 循环结尾， 本学期即将变成上学期，今年即将变成旧年
        last_semester, last_schoolyear = semester, schoolyear

    # 返回
    return grade_list

def sort(arranged):
    # QWQ深拷贝不敢碰
    if isinstance(arranged, list):
        for schoolyear in arranged:
            for semester in schoolyear['data']:
                required_courses = []
                optional_courses = []
                public_elective_courses = []
                other_courses = []
                # 归类
                for course in semester['data']:
                    if course['nature'] == '必修课': required_courses.append(course)
                    elif course['nature'] == '选修课': optional_courses.append(course)
                    elif course['nature'] == '公选课': public_elective_courses.append(course)
                    else: other_courses.append(course)
                # 排序
                def _sorted(courses):
                    def _key(c):# c means course
                        # 按成绩排序算法：
                        # 若成绩处为空，按-1算; 为汉字，按0算; 为数字，则正常排序
                        grade_final = c['grade_final']
                        if grade_final == '': return -1
                        elif is_number(grade_final): return grade_final
                        else: return 0
                    return sorted(courses, key=_key, reverse=True)

                # 必修课最前，依次是选修课，公选课 以及 其他课
                # print(required_courses)
                semester['data'] = _sorted(required_courses) + _sorted(optional_courses)+ \
                                   _sorted(public_elective_courses) + _sorted(other_courses)
def mark(sorted_list):
    '''
    给排好的list做标记
    :param sorted_list:
    :return:
    '''
    if isinstance(sorted_list, list):
        for schoolyear in sorted_list:
            for semester in schoolyear['data']:
                for course in semester['data']:
                    # 必修课前加 ** ， 如  '**公共英语'
                    if course['nature'] == '必修课': course['name'] = '**' + course['name']

                    # 如果有补考成绩，则以最后一次补考成绩为准
                    if is_number(course['grade_markup']): course['grade_final'] = course['grade_markup']

                    # 重修
                    if is_number(course['grade_retake']): course['grade_final'] = course['grade_retake']

                    if is_number(course['grade_final']): course['grade_final'] = str(float(course['grade_final']))
                    elif course['grade_final'] == '': course['grade_final'] = '----'

@api.route('/chengji')
def chengji():

    xuehao = request.args.get('xuehao')
    mima = request.args.get('mima')
    print(xuehao, mima)

    try:
        grade = Grade()
        grade.login(xuehao, mima)

        # 排除字段名 如：'课程号', '学年', '学期'
        data = grade.get_grade(raw=True)[1:]

        grade_list = arrange(data)

        sort(grade_list)
        mark(grade_list)
        return jsonify(grade_list)

    except ZhengFangException as e:
        return e.message

