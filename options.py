# coding=utf-8
"""
desc..
    :copyright: (c) 2016 by fangpeng(@beginman.cn).
    :license: MIT, see LICENSE for more details.
"""
import functools
import tornado.options


def define_options(opts):
    # Debugging
    opts.define(
        'debug',
        default=False,
        type=bool,
        help="Turn on autoreload and log to stderr",
        callback=functools.partial(enable_debug, opts),
        group="Debugging"
    )

    def config_callback(path):
        opts.parse_config_file(path, final=False)

    opts.define(
        'config',
        type=str,
        help="Path to config file",
        callback=config_callback,
        group="config"
    )

    # App
    opts.define('autoreload', type=bool, default=False, group='App')
    opts.define('cookie_secret', type=str, group='App')
    opts.define('port', default=8000, type=int, help="Server port", group='App')

    opts.add_parse_callback(
        functools.partial(check_required_options, opts)
    )


def check_required_options(opts):
    for required_option_name in (
            ('port'),
    ):
        if not getattr(opts, required_option_name, None):
            msg = (
                '%s required.' % required_option_name
            )
            raise tornado.options.Error(msg)


def enable_debug(opts, debug):
    if debug:
        opts.log_to_stderr = True
        opts.autoreload = True
