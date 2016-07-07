# coding=utf-8
"""
desc..
    :copyright: (c) 2016 by fangpeng(@beginman.cn).
    :license: MIT, see LICENSE for more details.
"""
import datetime
import pymongo
db = pymongo.MongoClient().mongoqueue

db.events.insert({
    'ts': datetime.datetime.utcnow(),
    'name':'hello'
})
