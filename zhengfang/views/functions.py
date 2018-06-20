# coding: utf8



from views import app
from flask import render_template, session
from .utils import message, is_online

from zhengfang.login import Login
@app.route('/functions')
def functions():

    zf_session = is_online()
    if zf_session:
        return render_template('functions.html',
                               navbar_title='请选择功能：')
    else:
        return message('请登录')
