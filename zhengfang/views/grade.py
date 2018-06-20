# coding: utf8


from flask import render_template, session, request


from . import app
from .utils import message, is_online

from zhengfang.exceptions import ZhengFangException
from zhengfang.grade import Grade


@app.route('/grade', methods=['GET'])
def grade():

    try:
        zf_session = is_online()
        if zf_session:
            zf_grade = Grade(session=zf_session)
            score = zf_grade.get_grade()
            return render_template('grade.html', grade=score)
        else:
            return message('你也没登陆啊')

    except ZhengFangException as err:
        return message(err.message)

