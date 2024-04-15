# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2023/9/14
@Software: PyCharm
@disc:
======================================="""
import datetime
import hashlib
import io
import json
import logging
import math
import os
import tempfile
import threading
import time
import traceback
from io import BytesIO

import ffmpeg
import requests
from PIL import Image
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from minio import Minio, S3Error
from minio_storage.storage import get_setting
from moviepy.video.io.VideoFileClip import VideoFileClip
from pyicloud.services.photos import PhotoAsset

from proj.settings import MINIO_STORAGE_USE_HTTPS, MINIO_STORAGE_CERT_CHECK, MINIO_STORAGE_MEDIA_BUCKET_NAME
from utils.icloud import IcloudService
from .models import IMedia, LocalMedia, AppleId

MINIO_STORAGE_ENDPOINT = get_setting("MINIO_STORAGE_ENDPOINT")
MINIO_STORAGE_ACCESS_KEY = get_setting("MINIO_STORAGE_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = get_setting("MINIO_STORAGE_SECRET_KEY")
s3_client = Minio(
    endpoint=MINIO_STORAGE_ENDPOINT,
    access_key=MINIO_STORAGE_ACCESS_KEY,
    secret_key=MINIO_STORAGE_SECRET_KEY,
    secure=MINIO_STORAGE_USE_HTTPS,  # 根据你的MinIO服务器是否使用HTTPS来设置
    cert_check=MINIO_STORAGE_CERT_CHECK
)

CHUNK_SIZE = 1024 * 1024  # 每个文件块的大小（字节）1M


def create_icloud_service(appleId: str) -> tuple[bool, IcloudService]:
    qs: AppleId = AppleId.objects.filter(email=appleId).first()
    print("被选中的用户名:", qs.username, qs.passwd)
    _iService = IcloudService(qs.username, qs.passwd, True)
    print(f"连接成功！[需要2FA:{_iService.requires_2fa}, 需要2SA:{_iService.requires_2sa}]")
    return _iService.requires_2fa, _iService


def insert_or_update_media(startRank: int, p: PhotoAsset, appleId: str):
    fn, ext = os.path.splitext(p.filename)
    ext = str(ext).upper()
    startedAt1 = time.time()
    obj, created = IMedia.objects.get_or_create(id=p.id)
    obj.appleId = appleId
    print(f"查询[{obj.id}]成功！[Created:{created},Duration:{time.time() - startedAt1} s]")
    startedAt2 = time.time()
    obj.filename = p.filename
    obj.ext = ext
    obj.size = p.size
    obj.dimensionX = p.dimensions[0]
    obj.dimensionY = p.dimensions[1]
    obj.asset_date = p.asset_date
    obj.added_date = p.added_date
    # download_thumb(obj, p)
    # download_prv(obj, p)
    obj.startRank = startRank  # 每次startRank都会变
    obj.versions = json.dumps(p.versions, indent=4, ensure_ascii=False)
    fields: dict = p._master_record['fields']
    if fields.keys().__contains__("resJPEGThumbRes"):
        obj.thumbURL = fields['resJPEGThumbRes']['value']['downloadURL']
    else:
        obj.thumbURL = fields['resOriginalRes']['value']['downloadURL']
    assetFields: dict = p._asset_record["fields"]
    obj.isHidden = assetFields['isHidden']["value"]
    obj.isFavorite = assetFields['isFavorite']["value"]
    obj.duration = assetFields['duration']["value"]
    obj.orientation = assetFields['orientation']["value"]
    obj.burstFlags = assetFields['burstFlags']["value"]
    obj.adjustmentRenderType = assetFields['adjustmentRenderType']["value"]
    if assetFields.keys().__contains__("timeZoneOffset"):
        obj.timeZoneOffset = assetFields['timeZoneOffset']["value"]
    if assetFields.keys().__contains__("locationEnc"):
        obj.locationEnc = assetFields["locationEnc"]["value"]
    obj.createdDeviceID = p._asset_record["created"]['deviceID']
    obj.createdUserRecordName = p._asset_record["created"]['userRecordName']

    obj.modifiedDeviceID = p._asset_record["modified"]['deviceID']
    obj.modifiedUserRecordName = p._asset_record["modified"]['userRecordName']

    obj.masterRecordChangeTag = p._master_record["recordChangeTag"]
    obj.assetRecordChangeTag = p._asset_record["recordChangeTag"]

    obj.masterRecordType = p._master_record["recordType"]
    obj.assetRecordType = p._asset_record["recordType"]

    obj.delete = p._asset_record["deleted"]

    obj.masterRecord = json.dumps(p._master_record, ensure_ascii=False, indent=4)
    obj.assetRecord = json.dumps(p._asset_record, ensure_ascii=False, indent=4)

    #         if obj.thumb or not os.path.exists(obj.thumb.path):
    #             download_thumb(obj, p)
    #     except ValueError as e:
    #         if "The 'thumb' attribute has no file associated with it." in str(e):
    #             download_thumb(obj, p)
    #         else:
    #             raise ValueError(e)
    #     try:
    #         if obj.prv or not os.path.exists(obj.prv.path):
    #             download_prv(obj, p)
    #     except ValueError as e:
    #         if "The 'prv' attribute has no file associated with it." in str(e):
    #             download_prv(obj, p)
    #         else:
    #             raise ValueError(e)
    print(f"预处理[{obj.id}]成功！[Duration:{time.time() - startedAt2} s]")
    startedAt3 = time.time()
    obj.save()
    print(f"保存[{obj.id}]成功！[Duration:{time.time() - startedAt3} s]")
    return obj


def update(_iService, records, startRank):
    def do(_records, _startRank):
        iPhotos = _iService.record2iphoto(_records)
        for i, iphoto in enumerate(iPhotos):
            insert_or_update_media(_startRank + i, iphoto, _iService.user.get("accountName"))

    th = threading.Thread(target=do, args=(records, startRank))
    th.start()


def collect(startRank: int, appleId):
    require2fa, _iService = create_icloud_service(appleId)
    if require2fa:
        raise Exception("2FA required to create icloud service.")
    resp = _iService.query_medias(startRank=startRank)
    records: list[dict] = resp['records']
    update(_iService, records, startRank)


STATUS_FINISHED = "FINISHED"
STATUS_STOP = "STOPPING"
STATUS_RUNNING = "Running"
STATUS_EXCEPTION = "Exception"
STATUS = STATUS_STOP

TOTAL = -1
FINISHED_COUNT = 0
STARTED_AT = datetime.datetime.now()
EXCEPTION_MSG = None
EXCEPTION_TRACE_BACK = None


def collect_all_medias(iService: IcloudService):
    global STATUS, FINISHED_COUNT, TOTAL, STARTED_AT, EXCEPTION_MSG, EXCEPTION_TRACE_BACK
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
    STATUS = STATUS_RUNNING
    STARTED_AT = datetime.datetime.now()
    try:
        _, TOTAL = iService.media_total()
        medias = iService.photos.all
        FINISHED_COUNT = 0
        for i, photo in enumerate(medias):
            FINISHED_COUNT = i + 1
            progress = FINISHED_COUNT / TOTAL * 100
            dlt = datetime.datetime.now() - STARTED_AT
            finishedCount = math.ceil(TOTAL * progress / 100)
            speed_in_second = finishedCount / dlt.total_seconds()
            left = TOTAL - finishedCount
            dlt_in_second = left / speed_in_second
            dlt1 = datetime.timedelta(seconds=dlt_in_second)
            willFinishedAt = datetime.datetime.now() + dlt1
            startedAt = time.time()
            insert_or_update_media(i, photo, iService.user.get("accountName"))
            print(f"{progress:.2f}% ({FINISHED_COUNT}/{TOTAL}), {photo}, [Duration:{time.time() - startedAt} s]")
        STATUS = STATUS_FINISHED
    except Exception as e:
        STATUS = STATUS_EXCEPTION
        EXCEPTION_MSG = str(e)
        EXCEPTION_TRACE_BACK = traceback.format_exc()
        logging.error("iCloud数据同步异常", exc_info=True)


def download_thumb(obj: IMedia, p):
    fields = p._master_record['fields']
    if fields.keys().__contains__("resJPEGThumbRes"):
        downloadURL = fields['resJPEGThumbRes']['value']['downloadURL']
        thumbResp = requests.get(downloadURL)
        thumbCF = ContentFile(thumbResp.content, f"{p.filename}.JPG")
        obj.thumb = thumbCF
        obj.save()
    else:
        downloadURL = fields['resOriginalRes']['value']['downloadURL']
        originResp = requests.get(downloadURL)
        originCF = ContentFile(originResp.content, f"{p.filename}.JPG")
        obj.origin = originCF
        obj.save()
        video = VideoFileClip(obj.origin.path)
        # 获取视频的第0秒（即开头）的帧，作为缩略图
        thumbnail = video.get_frame(0)
        # 转换为PIL Image对象
        image = Image.fromarray(thumbnail)
        # 创建一个临时的二进制数据缓冲区
        buffer = BytesIO()
        # 将图像保存到二进制缓冲区
        image.save(buffer, format='JPEG')
        # 创建ContentFile对象
        thumbCF = ContentFile(buffer.getvalue())
        # 关闭二进制缓冲区
        buffer.close()
        obj.thumb = thumbCF
        obj.save()


def download_prv(source: IMedia, dest: LocalMedia):
    """"
    com.apple.quicktime-movie
    """
    fields: dict = json.loads(source.masterRecord)['fields']
    originalFileType = fields['resOriginalFileType']['value']
    if fields.keys().__contains__("resVidSmallRes"):
        downloadURL = fields['resVidSmallRes']['value']['downloadURL']
        resp = requests.get(downloadURL)
        cf = ContentFile(resp.content, f"{source.filename}.MP4")
        dest.prv = cf
        dest.save()
    elif originalFileType in ['public.jpeg', 'public.png', 'public.heic']:
        # 由于图片的预览文件和Thumb缩略图一样，所以不用再重新下载
        # HEIC图片有些是动图, 有些是实况图会有resVidSmallRes, 而有些不是实况图便就不会有视频属性
        pass
    elif originalFileType in ['com.compuserve.gif']:
        # 有些GIF图片可能只有一贞， 其次，GIF图片是可以在网页上可浏览的，所以我们可以直接把它原始文件下下来当作其可预览文件。
        download_origin(source, dest)
    elif originalFileType in ['com.apple.quicktime-movie']:
        download_origin(source, dest)
        # 转换命令并将输出保存到 BytesIO 对象
        output_stream = BytesIO()
        ffmpeg.input(dest.origin.path).output(output_stream, format='mp4').run()
        # 创建 ContentFile 对象
        output_stream.seek(0)  # 将流定位到开头
        content = ContentFile(output_stream.read(), name='output.mp4')
        dest.prv = content
        dest.save()
    else:
        raise Exception("iCloud预览数据异常")


def calculate_md5(chunk):
    md5 = hashlib.md5()
    md5.update(chunk)
    return md5.hexdigest()


headers = {'Content-Type': 'application/octet-stream'}


def save_to_s3(file_part, object_name: str, part_number: int, upload_id: str):
    # 上传文件分片，内网测试耗时约：0.45秒
    headers['Content-Md5'] = calculate_md5(file_part)
    etag = s3_client._upload_part(data=file_part, bucket_name=MINIO_STORAGE_MEDIA_BUCKET_NAME, object_name=object_name,
                                  part_number=part_number, upload_id=upload_id, headers=headers)

    return etag


def download_origin(source: IMedia, dest: LocalMedia):
    """"
    com.apple.quicktime-movie
    """
    global headers
    fields: dict = json.loads(source.masterRecord)['fields']
    originalResValue = fields['resOriginalRes']['value']
    fileChecksum = originalResValue['fileChecksum']
    size = originalResValue['size']
    downloadURL = originalResValue['downloadURL']
    originResp = requests.get(downloadURL)
    part_number = 1
    # 创建一个分块上传的 session
    objName = "LocalMedia/origin/" + dest.filename
    logging.info("ObjName: " + objName)
    logging.info("originResp-Headers:" + str(originResp.headers))

    logging.info("Headers:" + str(headers))
    # FIXME: 后期继续实现分片上传
    # 获取分片上传ID
    # upload_id = s3_client._create_multipart_upload(MINIO_STORAGE_MEDIA_BUCKET_NAME, objName, headers)
    # logging.info(f"Upload ID: {upload_id}")
    # _parts = []
    temp_file_name = ""
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_name = temp_file.name
        logging.info("temp_file_name: " + temp_file_name)
        for chunk in originResp.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                temp_file.write(chunk)
                logging.info(f"Chunk {part_number} 下载成功, 并写入到了: {temp_file_name}")
            # TODO: 需要在这里进行进度同步操作, 计算每一个chunk的大小和剩下content的大小
            # 获取分片上传url
            # url = minio_client.get_presigned_url(
            #     "PUT",
            #     MINIO_STORAGE_MEDIA_BUCKET_NAME,
            #     objName,
            #     expires=datetime.timedelta(days=1),
            #     extra_query_params={"partNumber": str(part_number), "uploadId": upload_id}
            # )
            # logging.info(f"Uploading chunk {part_number}...")
            # etag = save_to_s3(chunk, objName, part_number, upload_id)
            # # 将上传的分片添加到分片列表
            # _parts.append((part_number, etag))
            # print(f"Uploaded part {part_number}")
            part_number += 1
    # response = s3_client._complete_multipart_upload(MINIO_STORAGE_MEDIA_BUCKET_NAME, objName, upload_id, _parts)
    # print(f"upload id: {upload_id}, parts: {_parts}")
    # temp_file.seek(0)
        default_storage.save(objName, temp_file)
        # s3_client.fput_object(MINIO_STORAGE_MEDIA_BUCKET_NAME, objName, temp_file_name, size)
        dest.origin = objName
        dest.save()
    os.remove(temp_file_name)


def delete_from_icloud(qs, lm):
    from .admin import iService
    resp = iService.delete(json.loads(qs.assetRecord)['recordName'], qs.assetRecordType,
                           qs.masterRecordChangeTag)
    print(resp.text)
    respJson = resp.json()
    records = respJson["records"]
    record = records[0]
    if record["fields"]["isDeleted"]["value"] == 1:
        if lm is not None:
            lm.assetRecordAfterDelete = resp.text
            lm.detach_icloud_date = datetime.datetime.now()
            lm.save()
        qs.delete()
    return resp


def migrateIcloudToLocal(qs):
    def _migrate(qs):
        try:
            lm, created = LocalMedia.objects.get_or_create(id=qs.id)
            lm.filename = qs.filename
            lm.ext = qs.ext
            lm.size = qs.size
            lm.duration = qs.duration
            lm.orientation = qs.orientation
            lm.dimensionX = qs.dimensionX
            lm.dimensionY = qs.dimensionY
            lm.adjustmentRenderType = qs.adjustmentRenderType
            lm.timeZoneOffset = qs.timeZoneOffset
            lm.burstFlags = qs.burstFlags

            lm.masterRecordChangeTag = qs.masterRecordChangeTag
            lm.assetRecordChangeTag = qs.assetRecordChangeTag

            lm.added_date = qs.added_date
            lm.asset_date = qs.asset_date

            lm.versions = qs.versions
            lm.masterRecord = qs.masterRecord
            lm.assetRecord = qs.assetRecord

            thumbResp = requests.get(qs.thumbURL)
            thumbCF = ContentFile(thumbResp.content, f"{qs.filename}.JPG")
            lm.thumb = thumbCF

            lm.save()
            download_prv(qs, lm)
            download_origin(qs, lm)
            resp = delete_from_icloud(qs, lm)
        except Exception as e:
            logging.error("媒体资源迁移失败！", exc_info=True)

    th = threading.Thread(target=_migrate, args=(qs,))
    th.start()
