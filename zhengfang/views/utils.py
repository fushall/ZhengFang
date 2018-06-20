# coding: utf8

from flask import render_template, session
from zhengfang.login import Login


def message(text, title='提示：'):
    return render_template(
        'message.html',
        message = {
            'title': title,
            'text' : text,
        }
    )


def is_online():
    zf_session = session.get('session')
    print(zf_session)
    if zf_session:
        login = Login(session=zf_session)
        if login.online:
            return zf_session
        else:
            return False
    else:
        return False