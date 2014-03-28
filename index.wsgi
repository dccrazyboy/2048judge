import tornado.web
from handler import *

settings = {
    "debug": True,
}

# application should be an instance of `tornado.web.Application`,
# and don't wrap it with `sae.create_wsgi_app`
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/judge/", JudgeHandler),
], **settings)
