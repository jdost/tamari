import tamari
from werkzeug.contrib.fixers import ProxyFix

tamari.app.wsgi_app = ProxyFix(tamari.app.wsgi_app)
tamari.app.run()
