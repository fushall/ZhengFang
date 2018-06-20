# coding: utf8
from views import app

if __name__ == '__main__':
    if app.config['DEBUG']:
        import test

        print(app.url_map)
        app.run(host=app.config['HOST'],
                port=app.config['PORT'],
                debug=app.config['DEBUG'])