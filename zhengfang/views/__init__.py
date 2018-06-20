# coding: utf8
import config
from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from ext import change_cdn



app = Flask(__name__)

app.config.from_object(config.DevelopmentConfig)
#app.config.from_object(config.ProductionConfig)




boot = Bootstrap(app)
change_cdn(app)
login_manager = LoginManager(app)


# 路由
from . import index, login, grade, functions

# 蓝图
from . import api
app.register_blueprint(api.api, url_prefix='/api')
print(api.api)