# coding: utf8


from flask import render_template, session, request


from . import app
from .utils import message

from zhengfang.exceptions import ZFError
from zhengfang.pingjiao import PingJiao

@app.route('/pingjiao/save', methods=['post'])
def get_pingjia():
    try:
        info = session.get('info')
        pingjiao   = PingJiao(info=info)
        values = request.values.to_dict()

        vs   = values.pop('vs')
        kh   = values.pop('kh')
        qt   = values.pop('qt')
        pj   = []
        for k in values:
            pj.append({
                'name' : k,
                'value': values[k]
            })

        pingjiao.save(vs, kh, qt, pj)
        return  message('正在保存至服务器，请返回刷新页面，确认是否保存成功。')
    except ZFError as err:
        return message(err.msg)

@app.route('/pingjiao/submit', methods=['get'])
def submit():
    info      = session.get('info')
    pingjiao  = PingJiao(info=info)

    viewstate = request.values.get('vs')
    if viewstate:
        viewstate = pingjiao.qoute(viewstate, safe='/=')

        kehao     = request.values.get('kh')

        try:
            if pingjiao.submit(viewstate, kehao):
                return message('恭喜！你完成了本学期的教学评价')
            else:
                return message('请完成评教')
        except ZFError as err:
            return message(err.msg)
    return message('评教失败，请返回后刷新，再次执行此操作')


@app.route('/pingjiao', methods=['GET'])
def pingjiao():
    info = session.get('info')
    url  = request.args.get('url')
    try:
        pj = PingJiao(info=info)
        if pj.is_open():

            kecheng = pj.menu_pingjiao()
            url = pj.unqoute(url) if url else kecheng[0]['url']
            # 编码后传输
            for i in kecheng:
                i['url'] = pj.qoute(i['url'])

            pingjia = pj.parse_pingjia(url)
            return render_template('pingjiao.html',
                                   kecheng=kecheng,
                                   pingjia=pingjia)
        else:
            return message('评教暂未开放，或者您已经完成评价')

    except ZFError as err:
        return message(err.msg)


