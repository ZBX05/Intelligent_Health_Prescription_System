from web import *
from gevent import pywsgi

if __name__ == '__main__':
    # app.run(web_config.app_host,web_config.app_port)
    # app.run(web_config.app_host,web_config.app_port,ssl_context=(web_config.app_cert_dir,web_config.app_key_dir))
    server=pywsgi.WSGIServer((web_config.app_host,web_config.app_port),app,certfile=web_config.app_cert_dir
                             ,keyfile=web_config.app_key_dir)
    server.serve_forever()