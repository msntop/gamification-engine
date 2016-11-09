from gengine.app.tests import db as db
from gengine.metadata import init_declarative_base, init_session
import unittest
import os
import pkgutil
import testing.redis
import logging

log = logging.getLogger(__name__)

init_session()
init_declarative_base()

__path__ = [x[0] for x in os.walk(os.path.dirname(__file__))]

def create_test_suite():
    suite = unittest.TestSuite()
    for imp, modname, _ in pkgutil.walk_packages(__path__):
        mod = imp.find_module(modname).load_module(modname)
        for test in unittest.defaultTestLoader.loadTestsFromModule(mod):
            suite.addTests(test)
    return suite

if __name__=="__main__":
    try:
        redis = testing.redis.RedisServer()

        from gengine.base.cache import setup_redis_cache
        dsn = redis.dsn()
        setup_redis_cache(dsn["host"], dsn["port"], dsn["db"])

        from gengine.app.cache import init_caches
        init_caches()

        db.setupDB()
        testSuite = create_test_suite()
        text_runner = unittest.TextTestRunner().run(testSuite)
    finally:
        try:
            db.unsetupDB()
        except:
            log.exception()
        try:
            redis.stop()
        except:
            log.exception()
