# conding: utf8

from flask import render_template, redirect, url_for, request

from . import app

from flask import render_template

from zhengfang.grade import Grade
from zhengfang.exceptions import ZhengFangException

@app.route('/')
def index():

    notice = '''
    
    <br>请广大同学奔走相告，查成绩不要钱，勿轻信任何免费or收费查成绩，
    <br>请保护好自己的隐私！请保护好自己的隐私！请保护好自己的隐私！
    <br>（学号以及密码，以及登陆教务系统后的个人信息，如：身份证，民族等）
    <br>本系统由学生团队开发，网站内部不私自保存任何信息，请同学们放心。
    <br><br><br><br><br><br><br>时间：2017年7月15日
    
    
    
    '''
    return render_template('index.html', a=22, notice=notice)

