# coding: utf8
import datetime

class DefaultConfig:
    # Flask
    HOST = '127.0.0.1'
    PORT = 5000
    SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    JSON_AS_ASCII = False

class ProductionConfig(DefaultConfig):
    DEBUG = False
    BOOTSTRAP_SERVE_LOCAL = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5)


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    BOOTSTRAP_SERVE_LOCAL = True
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(seconds=30)