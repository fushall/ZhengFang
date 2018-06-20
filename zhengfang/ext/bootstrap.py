# coding: utf8

from flask_bootstrap import \
    BOOTSTRAP_VERSION, \
    JQUERY_VERSION, \
    HTML5SHIV_VERSION, \
    RESPONDJS_VERSION, \
    ConditionalCDN, \
    WebCDN


def change_cdn(app):
    cdns = app.extensions['bootstrap']['cdns']
    local = cdns['local']
    static = cdns['static']

    def lwrap(cdn, primary=static):
        return ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', primary, cdn)

    bootstrap = lwrap(
        WebCDN('//cdn.bootcss.com/bootstrap/%s/' %
               BOOTSTRAP_VERSION), local)

    jquery = lwrap(
        WebCDN('//cdn.bootcss.com/jquery/%s/' %
               JQUERY_VERSION), local)

    html5shiv = lwrap(
        WebCDN('//cdn.bootcss.com/html5shiv/%s/' %
               HTML5SHIV_VERSION))

    respondjs = lwrap(
        WebCDN('//cdn.bootcss.com/respond.js/%s/' %
               RESPONDJS_VERSION))

    app.extensions['bootstrap'] = {
        'cdns': {
            'local': local,
            'static': static,
            'bootstrap': bootstrap,
            'jquery': jquery,
            'html5shiv': html5shiv,
            'respond.js': respondjs,
        },
    }

