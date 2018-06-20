# coding: utf8

from flask import request, render_template, session, redirect, flash

from . import app, login_manager
from .utils import message

from zhengfang.exceptions import ZhengFangException
from zhengfang.login import Login


@login_manager.user_loader
def load_user(user_id):
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',
                               navbar_title='准备登陆...')

    elif request.method == 'POST':
        # 学号 密码
        stu_no = request.values.get('stu_no')
        stu_pw = request.values.get('stu_pw')


        try:
            zflogin = Login()
            zflogin.login(stu_no, stu_pw)
            session['session'] = zflogin.session
            print(session['session'])
            stu_name = zflogin.session['student']['name']
            return render_template('functions.html',
                                   navbar_title='你好，'+stu_name+'同学')

        except ZhengFangException as err:
            flash(err.message)
            return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('index.html')