# coding=utf-8
"""
desc..
    :copyright: (c) 2016 by fangpeng(@beginman.cn).
    :license: MIT, see LICENSE for more details.
"""
import datetime
import tornado.web
import tornado.escape
from tornado import gen


class PostHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        name = self.get_argument('name')
        db = self.settings['db']
        _id = yield db.events.insert({
            'name': name,
            'ts': datetime.datetime.utcnow()
        })
        message = {
            "id": str(_id),
            "name": name,
        }
        self.write(message)
        self.finish()
