import logging
import os
import platform

from .secret import ES_URI, ES_USERNAME, ES_PASSWORD

_DEBUG = False
_STATIC_URL = '/static/'
WINDOWS = 'Windows'
LINUX = 'Linux'
MacOS = 'Darwin'
CURRENT_SYSTEM = platform.system()
logging.info(f"CWD:{os.getcwd()}")

if CURRENT_SYSTEM == WINDOWS:
    _DEBUG = True

elif CURRENT_SYSTEM == MacOS:
    _DEBUG = True
    import pymysql

    pymysql.version_info = (1, 4, 13, "final", 0)
    pymysql.install_as_MySQLdb()  # 使用pymysql代替mysqldb连接数据库
else:
    """
        服务器环境 
    """
    # _STATIC_URL = '/sdm/static/'
    import pymysql

    pymysql.version_info = (1, 4, 13, "final", 0)
    pymysql.install_as_MySQLdb()  # 使用pymysql代替mysqldb连接数据库
try:
    _DEBUG = secret._DEBUG
except:
    pass
logging.info(f"this app is running on {CURRENT_SYSTEM},DEBUG:{_DEBUG}")
from elasticsearch import Elasticsearch

esClient = Elasticsearch(hosts=ES_URI, http_auth=(ES_USERNAME, ES_PASSWORD),
                         timeout=3600)
