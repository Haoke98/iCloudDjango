# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/19
@Software: PyCharm
@disc:
======================================="""
import logging

import requests
from celery import shared_task, current_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from icloud.models import IMedia, LocalMedia
from icloud.services import insert_or_update_media, create_icloud_service, delete_from_icloud, \
    download_prv, download_origin


@shared_task(soft_time_limit=3600, time_limit=7200)
def sync_list(apple_id: str, *args, **kwargs):
    """
    同步iMedia
    :param apple_id: 苹果🍎ID
    :param args:
    :param kwargs:
    :return:
    """
    # TODO: 实现传惨传cookie文件或者cookie内容,来实现不同的地方免登录操作( 共享cookie )
    print(f"任务已经启动....{apple_id}")
    requires_2fa, iService = create_icloud_service(apple_id)
    if requires_2fa:
        return {"msg": "该AppleID需要进行2FA验证", "appleId": apple_id}
    # TODO: 实现对不同的相册进行iMedia的同步, 选那个相册用参数来控制
    # for album in albums:
    #     photos = iService.photos.albums[album.name]
    #     total = len(photos)
    # if album.count == total:
    #     print(f"{album.name}: 无需同步跳过")
    #     continue
    # for i, p in enumerate(photos):
    #     th = threading.Thread(target=collect, args=(p, album, i, total))
    #     th.start()
    # album.agg()
    # album.save()
    # target_photo = None
    print("iService:", iService)
    _, TOTAL = iService.media_total()
    medias = iService.photos.all
    for i, photo in enumerate(medias):
        insert_or_update_media(i, photo, iService.user.get("accountName"))
        # 更新任务进度
        # TODO: 这里可以实时统计一下每次同步中同步了多少个视频?多少个图片之类的
        current_task.update_state(state='PROGRESS', total=TOTAL,
                                  processed=i + 1,
                                  extra_process_info={})
    return {"msg": "ok"}


@shared_task(soft_time_limit=3600, time_limit=7200)
def migrate(icloud_media_id: str, *args, **kwargs):
    # TODO: 实现传惨传cookie文件或者cookie内容,来实现不同的地方免登录操作( 共享cookie )
    print(f"任务已经启动....{icloud_media_id}")
    cloudObj = IMedia.objects.filter(id=icloud_media_id).first()
    apple_id = cloudObj.appleId
    requires_2fa, iService = create_icloud_service(apple_id)
    if requires_2fa:
        return {"msg": "该AppleID需要进行2FA验证", "appleId": apple_id}
    # TODO: 实现对不同的相册进行iMedia的同步, 选那个相册用参数来控制
    if cloudObj is not None:
        localObj, created = LocalMedia.objects.get_or_create(id=cloudObj.id)
        localObj.filename = cloudObj.filename
        localObj.ext = cloudObj.ext
        localObj.size = cloudObj.size
        localObj.duration = cloudObj.duration
        localObj.orientation = cloudObj.orientation
        localObj.dimensionX = cloudObj.dimensionX
        localObj.dimensionY = cloudObj.dimensionY
        localObj.adjustmentRenderType = cloudObj.adjustmentRenderType
        localObj.timeZoneOffset = cloudObj.timeZoneOffset
        localObj.burstFlags = cloudObj.burstFlags

        localObj.masterRecordChangeTag = cloudObj.masterRecordChangeTag
        localObj.assetRecordChangeTag = cloudObj.assetRecordChangeTag

        localObj.added_date = cloudObj.added_date
        localObj.asset_date = cloudObj.asset_date

        localObj.versions = cloudObj.versions
        localObj.masterRecord = cloudObj.masterRecord
        localObj.assetRecord = cloudObj.assetRecord

        thumbResp = requests.get(cloudObj.thumbURL)
        thumbObjName = f"LocalMedia/thumb/{cloudObj.filename}.JPG"
        thumbCF = ContentFile(thumbResp.content, f"{cloudObj.filename}.JPG")
        resp = default_storage.save(thumbObjName, thumbCF)
        print("上传Thumb成功:" + str(resp))
        localObj.thumb = thumbObjName

        localObj.save()

        download_prv(cloudObj, localObj)

        download_origin(cloudObj, localObj)

        resp = delete_from_icloud(cloudObj, localObj)
    return {
        'state': True,
        'msg': f'迁移开始！'
    }
