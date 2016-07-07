# coding=utf-8
"""
desc..
    :copyright: (c) 2016 by fangpeng(@beginman.cn).
    :license: MIT, see LICENSE for more details.
"""
import logging
import sys
import datetime

from tornado import gen

import pymongo.errors


_db = None


@gen.coroutine
def create_events_collection(db):
    """Create capped collection"""
    try:
        yield db.create_collection('events', size=100*1024, capped=True)
        logging.info(
            'Created capped collection "events" in database "%s"',
            db.name
        )
    except pymongo.errors.CollectionInvalid:
        # Collection already exists
        collection_options = yield db.events.options()
        if 'capped' not in collection_options:
            logging.error(
                '%s.events exists and is not a capped collection,\n'
                'please drop the collection and start this app again.' %
                db.name
            )
            sys.exit(1)


@gen.coroutine
def startup(db):
    global _db
    if _db:
        # Already started
        return

    _db = db
    yield create_events_collection(db)

    # Typically the global loop, but it's a different loop in tests.
    loop = db.get_io_loop()

    @gen.coroutine
    def tail():
        collection = db.events
        now = datetime.datetime.utcnow()
        last_event_ts = None

        def make_cursor():
            return collection.find(
                {'ts': {'$gte': last_event_ts or now}},
                tailable=True, await_data=True
            )

        cursor = make_cursor()

        while True:
            if not cursor.alive:
                # While collection is empty, tailable cursor dies immediately.
                yield gen.Task(
                    loop.add_timeout,
                    datetime.timedelta(seconds=1)
                )
                logging.debug('new cursor, last_event_ts=%s, now=%s',
                              last_event_ts, now)
                cursor = make_cursor()

            try:
                while (yield cursor.fetch_next):
                    event = cursor.next_object()
                    logging.info(
                        "Event: %r, %s", event.get('name'), event.get('ts')
                    )
                    # to do something....
                    # do_event(event)
                    last_event_ts = event.get('ts')
            except pymongo.errors.OperationFailure:
                # Collection dropped
                logging.exception('Tailing "events" collection')
                yield gen.Task(loop.add_timeout, datetime.timedelta(seconds=1))
                logging.error(
                    'Resuming tailing "events" collection.'
                    ' Last_event_ts = %s, now = %s',
                    last_event_ts, now
                )

                cursor = make_cursor()

            except Exception:
                logging.exception("Tailing 'events' collection.")
                return

    # Start infinite loop
    tail()


def shutdown():
    global _db
    _db = None
