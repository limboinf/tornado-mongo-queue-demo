# coding=utf-8
"""
desc..
    :copyright: (c) 2016 by fangpeng(@beginman.cn).
    :license: MIT, see LICENSE for more details.
"""
import os
from functools import partial

import motor
import tornado.ioloop
import tornado.web
from tornado.options import options as opts
from tornado import httpserver

from events import startup
from options import define_options
from handelers import PostHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda root, *a: os.path.join(root, *a)


def app(db, option_parser):
    urls = [
        (r'/post', PostHandler),
    ]
    return tornado.web.Application(
        handlers=urls,
        db=db,
        # template_path=path(ROOT, 'templates'),
        # static_path=path(ROOT, 'media'),
        gzip=True,
        **option_parser.as_dict()
    )


def main():
    define_options(opts)
    opts.parse_command_line()

    db = motor.MotorClient().mongoqueue

    loop = tornado.ioloop.IOLoop.current()
    loop.run_sync(partial(startup, db))
    http_server = httpserver.HTTPServer(app(db, opts))
    http_server.listen(opts.port)
    print("Listening on port %s" % opts.port)
    loop.start()

if __name__ == '__main__':
    main()
