# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2023/8/16
@Software: PyCharm
@disc:
======================================="""
from .account import AccountAdmin
import os.path
import threading
import urllib.parse
import uuid
from datetime import datetime
from urllib.parse import urlencode

from django.contrib import admin
from django.http import JsonResponse
from minio_storage.storage import get_setting
from simplepro.admin import FieldOptions
from simplepro.decorators import button, layer
from simplepro.dialog import MultipleCellDialog, ModalDialog
from simpleui.admin import AjaxAdmin

from utils import human_readable_bytes, human_readable_time, icloud
from ..models import IMedia, Album, LocalMedia, AppleId
from ..services import collect_all_medias, delete_from_icloud, migrateIcloudToLocal








