import logging
import os
import platform
from .celery import app as celery_app

__all__ = ('celery_app',)
_STATIC_URL = '/static/'
WINDOWS = 'Windows'
LINUX = 'Linux'
MacOS = 'Darwin'
CURRENT_SYSTEM = platform.system()
logging.info(f"CWD:{os.getcwd()}")
logging.info(f"this app is running on {CURRENT_SYSTEM}")
